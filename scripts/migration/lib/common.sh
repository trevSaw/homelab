#!/usr/bin/env bash
# Phase 10.5 migration framework — shared helpers (hardened after mocha dry-run).
# Personal homelab (mocha). No live mutation unless MIGRATE_EXECUTE=1.
# shellcheck disable=SC2034
set -euo pipefail

MIGRATE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$MIGRATE_ROOT/../.." && pwd)"
PHASE_DIR="${PHASE_DIR:-$REPO_ROOT/Validation/Phase10.5}"
SERVICES_CONF="${SERVICES_CONF:-$MIGRATE_ROOT/services.conf}"

SOURCE_PREFIX="/hive/"
TARGET_PREFIX="/mnt/monarch/appdata/"

MIGRATE_EXECUTE="${MIGRATE_EXECUTE:-0}"
MIGRATE_APPLY_COMPOSE="${MIGRATE_APPLY_COMPOSE:-0}"
MIGRATE_CHECKSUM="${MIGRATE_CHECKSUM:-0}"
MIGRATE_FORCE_REVIEW="${MIGRATE_FORCE_REVIEW:-0}"
MIGRATE_QUIET="${MIGRATE_QUIET:-0}"

LOG_FILE=""
CURRENT_SERVICE=""
RUN_PHASE="framework"
RUN_STATUS="SUCCESS"
COPY_REQUIRED="no"
COMPOSE_UPDATE_NEEDED="no"
VERIFICATION_STATUS="n/a"
ROLLBACK_AVAILABLE="true"

# Accumulated operator-facing messages
declare -a WARN_LIST=()
declare -a ERR_LIST=()
declare -a INFO_LIST=()

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

die() {
  ERR_LIST+=("$*")
  echo "ERROR: $*" >&2
  log "ERROR: $*"
  RUN_STATUS="FAIL"
  exit 1
}

warn() {
  WARN_LIST+=("$*")
  echo "WARN: $*" >&2
  log "WARN: $*"
}

info() {
  INFO_LIST+=("$*")
  if [[ "$MIGRATE_QUIET" != "1" ]]; then
    echo "INFO: $*"
  fi
  log "INFO: $*"
}

ok() { info "OK: $*"; }

log() {
  [[ -n "${LOG_FILE:-}" ]] || return 0
  mkdir -p "$(dirname "$LOG_FILE")"
  printf '%s %s\n' "$(timestamp)" "$*" >>"$LOG_FILE"
}

is_execute() { [[ "$MIGRATE_EXECUTE" == "1" ]]; }
is_dry_run() { ! is_execute; }
is_apply_compose() { [[ "$MIGRATE_APPLY_COMPOSE" == "1" ]]; }

parse_migrate_flags() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) MIGRATE_EXECUTE=0; shift ;;
      --execute) MIGRATE_EXECUTE=1; shift ;;
      --apply-compose) MIGRATE_APPLY_COMPOSE=1; shift ;;
      --checksum) MIGRATE_CHECKSUM=1; shift ;;
      --force-review) MIGRATE_FORCE_REVIEW=1; shift ;;
      --quiet) MIGRATE_QUIET=1; shift ;;
      --phase-dir) PHASE_DIR="$2"; shift 2 ;;
      --help|-h)
        echo "Flags: --dry-run (default) | --execute | --apply-compose | --checksum | --force-review | --quiet | --phase-dir DIR"
        return 2
        ;;
      *) break ;;
    esac
  done
  REMAINING_ARGS=("$@")
}

init_service_log() {
  local svc="$1"
  CURRENT_SERVICE="$svc"
  WARN_LIST=(); ERR_LIST=(); INFO_LIST=()
  RUN_STATUS="SUCCESS"
  mkdir -p "$PHASE_DIR/logs" "$PHASE_DIR/inspect" "$PHASE_DIR/reports" "$PHASE_DIR/proposed"
  LOG_FILE="$PHASE_DIR/logs/${svc}.log"
  log "Started service=$svc execute=$MIGRATE_EXECUTE apply_compose=$MIGRATE_APPLY_COMPOSE"
}

assert_source_path() {
  local p="$1"
  [[ "$p" == "$SOURCE_PREFIX"* ]] || die "Refusing source outside ${SOURCE_PREFIX}: $p"
}

assert_target_path() {
  local p="$1"
  [[ "$p" == "$TARGET_PREFIX"* ]] || die "Refusing target outside ${TARGET_PREFIX}: $p"
}

# services.conf (pipe-delimited, # comments):
# key|compose_relpath|container_names|source_config|target_config|keep_hive|risk|order|migration_required|already_migrated|rsync_excludes|notes
# rsync_excludes: comma-separated patterns relative to source (e.g. downloads/**,*.log)
load_service() {
  local key="$1"
  local line
  line="$(grep -E "^${key}\|" "$SERVICES_CONF" | head -n1 || true)"
  [[ -n "$line" ]] || die "Unknown service key in services.conf: $key"

  IFS='|' read -r \
    SVC_KEY SVC_COMPOSE SVC_CONTAINERS SVC_SOURCE SVC_TARGET SVC_KEEP \
    SVC_RISK SVC_ORDER SVC_REQUIRED SVC_ALREADY SVC_EXCLUDES SVC_NOTES <<<"$line"

  # Back-compat: older 11-field rows put notes where excludes is
  if [[ -z "${SVC_NOTES:-}" && -n "${SVC_EXCLUDES:-}" && "$SVC_EXCLUDES" != *"*"* && "$SVC_EXCLUDES" != *"/"* && "$SVC_EXCLUDES" != *","* ]]; then
    # Heuristic: if "excludes" looks like prose notes, shift
    if [[ "$SVC_EXCLUDES" =~ [[:space:]] ]]; then
      SVC_NOTES="$SVC_EXCLUDES"
      SVC_EXCLUDES=""
    fi
  fi

  SVC_COMPOSE_ABS="$REPO_ROOT/$SVC_COMPOSE"
  case "$SVC_REQUIRED" in
    yes) COPY_REQUIRED="yes"; COMPOSE_UPDATE_NEEDED="yes" ;;
    verify) COPY_REQUIRED="maybe"; COMPOSE_UPDATE_NEEDED="maybe" ;;
    no) COPY_REQUIRED="no"; COMPOSE_UPDATE_NEEDED="no" ;;
    deferred) COPY_REQUIRED="deferred"; COMPOSE_UPDATE_NEEDED="deferred" ;;
    *) COPY_REQUIRED="$SVC_REQUIRED"; COMPOSE_UPDATE_NEEDED="$SVC_REQUIRED" ;;
  esac
}

list_service_keys() {
  grep -E '^[a-zA-Z0-9_-]+\|' "$SERVICES_CONF" | cut -d'|' -f1
}

human_bytes() {
  local b="${1:-0}"
  b="$(printf '%s' "$b" | tr -d '[:space:]')"
  [[ "$b" =~ ^[0-9]+$ ]] || { echo "${1:-0}"; return 0; }
  if command -v numfmt >/dev/null 2>&1; then
    numfmt --to=iec --suffix=B "$b" 2>/dev/null || echo "${b}B"
  else
    echo "${b}B"
  fi
}

# Safe tree stats: never abort on permission-denied (pipefail + find exit 1).
count_tree_stats() {
  local root="$1"
  STAT_BYTES=0
  STAT_FILES=0
  STAT_DIRS=0
  STAT_UNREADABLE=0
  if [[ ! -e "$root" ]]; then
    return 0
  fi

  local ferr
  ferr="$(mktemp)"
  # du may exit 1 on permission-denied children; never let pipefail abort the script
  STAT_BYTES="$(set +o pipefail; du -sb "$root" 2>/dev/null | awk '{b=$1} END {print b+0}')"
  STAT_FILES="$(set +o pipefail; find "$root" -type f 2>"$ferr" | wc -l | tr -d '[:space:]')"
  STAT_DIRS="$(set +o pipefail; find "$root" -type d 2>>"$ferr" | wc -l | tr -d '[:space:]')"
  if [[ -s "$ferr" ]]; then
    STAT_UNREADABLE="$(grep -c 'Permission denied' "$ferr" || true)"
    if [[ "${STAT_UNREADABLE:-0}" =~ ^[0-9]+$ ]] && (( STAT_UNREADABLE > 0 )); then
      warn "Partial tree stats: $STAT_UNREADABLE permission-denied path(s) under $root (size/count may be incomplete)"
    fi
  fi
  rm -f "$ferr"
  STAT_BYTES="$(printf '%s' "${STAT_BYTES:-0}" | tr -d '[:space:]')"
  STAT_FILES="$(printf '%s' "${STAT_FILES:-0}" | tr -d '[:space:]')"
  STAT_DIRS="$(printf '%s' "${STAT_DIRS:-0}" | tr -d '[:space:]')"
  [[ "$STAT_BYTES" =~ ^[0-9]+$ ]] || STAT_BYTES=0
  [[ "$STAT_FILES" =~ ^[0-9]+$ ]] || STAT_FILES=0
  [[ "$STAT_DIRS" =~ ^[0-9]+$ ]] || STAT_DIRS=0
}

# Estimate bytes excluding simple relative dir/file patterns (best-effort sizing).
# Pass "reuse" as $3 to skip recount when count_tree_stats was just called.
estimate_migratable_bytes() {
  local root="$1"
  local excludes="${2:-}"
  local reuse="${3:-}"
  EST_BYTES=0
  if [[ ! -e "$root" ]]; then
    return 0
  fi
  if [[ "$reuse" != "reuse" ]]; then
    count_tree_stats "$root"
  fi
  EST_BYTES=$STAT_BYTES
  [[ -n "$excludes" ]] || return 0

  local IFS=','
  local pat sub sub_b
  for pat in $excludes; do
    pat="${pat#/}"
    [[ "$pat" == *'*'* && "$pat" != */* ]] && continue
    sub="${pat%%/\*\*}"
    sub="${sub%/\*}"
    sub="${sub%/}"
    [[ -z "$sub" ]] && continue
    if [[ -e "$root/$sub" ]]; then
      sub_b="$(set +o pipefail; du -sb "$root/$sub" 2>/dev/null | awk '{b=$1} END {print b+0}')"
      sub_b="$(printf '%s' "$sub_b" | tr -d '[:space:]')"
      if [[ "$sub_b" =~ ^[0-9]+$ ]] && (( EST_BYTES >= sub_b )); then
        EST_BYTES=$((EST_BYTES - sub_b))
        info "size estimate excludes $root/$sub ($(human_bytes "$sub_b"))"
      fi
    fi
  done
}

rsync_exclude_args() {
  # Prints --exclude args from SVC_EXCLUDES
  local IFS=','
  local pat
  RSYNC_EXCLUDE_ARGS=()
  for pat in ${SVC_EXCLUDES:-}; do
    [[ -z "$pat" ]] && continue
    RSYNC_EXCLUDE_ARGS+=( --exclude="$pat" )
  done
}

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  printf '%s' "$s"
}

write_migration_json() {
  local out="$1"
  shift
  mkdir -p "$(dirname "$out")"
  local warnings_json="["
  local errors_json="["
  local i first
  first=1
  for i in "${WARN_LIST[@]:-}"; do
    [[ -z "$i" && ${#WARN_LIST[@]} -eq 0 ]] && break
    [[ $first -eq 1 ]] || warnings_json+=","
    first=0
    warnings_json+="\"$(json_escape "$i")\""
  done
  warnings_json+="]"
  first=1
  for i in "${ERR_LIST[@]:-}"; do
    [[ -z "$i" && ${#ERR_LIST[@]} -eq 0 ]] && break
    [[ $first -eq 1 ]] || errors_json+=","
    first=0
    errors_json+="\"$(json_escape "$i")\""
  done
  errors_json+="]"

  local dry_run_bool="true"
  is_execute && dry_run_bool="false"
  local exec_bool="false"
  is_execute && exec_bool="true"
  local compose_bool="false"
  is_apply_compose && compose_bool="true"

  cat >"$out" <<EOF
{
  "timestamp": "$(timestamp)",
  "service": "$(json_escape "${CURRENT_SERVICE:-}")",
  "phase": "$(json_escape "${RUN_PHASE:-framework}")",
  "status": "$(json_escape "${RUN_STATUS:-UNKNOWN}")",
  "dry_run": $dry_run_bool,
  "execute": $exec_bool,
  "source": "$(json_escape "${SVC_SOURCE:-}")",
  "destination": "$(json_escape "${SVC_TARGET:-}")",
  "files": ${STAT_FILES:-0},
  "directories": ${STAT_DIRS:-0},
  "bytes": "$(json_escape "$(human_bytes "${STAT_BYTES:-0}")")",
  "bytes_raw": ${STAT_BYTES:-0},
  "copy_required": "$(json_escape "${COPY_REQUIRED:-}")",
  "compose_update_needed": "$(json_escape "${COMPOSE_UPDATE_NEEDED:-}")",
  "compose_updated": $compose_bool,
  "verification_status": "$(json_escape "${VERIFICATION_STATUS:-}")",
  "rollback_available": true,
  "rsync_excludes": "$(json_escape "${SVC_EXCLUDES:-}")",
  "warnings": $warnings_json,
  "errors": $errors_json,
  "warning_count": ${#WARN_LIST[@]},
  "error_count": ${#ERR_LIST[@]}
}
EOF
}

# Back-compat alias used by older call sites
write_json_report() {
  local out="$1"
  shift
  # If called with key=value pairs, merge lightly into migration json via env overrides
  local pair key val
  for pair in "$@"; do
    key="${pair%%=*}"
    val="${pair#*=}"
    case "$key" in
      status) RUN_STATUS="$val" ;;
      files) STAT_FILES="$val" ;;
      directories) STAT_DIRS="$val" ;;
      phase) RUN_PHASE="$val" ;;
      verification_status) VERIFICATION_STATUS="$val" ;;
    esac
  done
  write_migration_json "$out"
}

json_to_markdown() {
  local json="$1"
  local md="$2"
  [[ -f "$json" ]] || return 0
  {
    echo "# Migration report"
    echo
    echo "Generated: $(timestamp)"
    echo
    echo '```json'
    cat "$json"
    echo '```'
  } >"$md"
}

ensure_dirs() {
  mkdir -p "$PHASE_DIR/logs" "$PHASE_DIR/inspect" "$PHASE_DIR/reports" "$PHASE_DIR/proposed"
}

mutate_guard() {
  local action="$1"
  if is_dry_run; then
    info "[dry-run] would: $action"
    return 1
  fi
  return 0
}

# Classify docker compose config stderr into a specific warning category.
# Sets COMPOSE_FAIL_CLASS and COMPOSE_FAIL_DETAIL
classify_compose_failure() {
  local errfile="$1"
  COMPOSE_FAIL_CLASS="compose_unknown"
  COMPOSE_FAIL_DETAIL="$(tr '\n' ' ' <"$errfile" | head -c 400)"
  if grep -qiE 'env file .* not found|\.env: no such file' "$errfile"; then
    COMPOSE_FAIL_CLASS="missing_env_file"
  elif grep -qiE 'variable is not set|required variable|missing.*variable' "$errfile"; then
    COMPOSE_FAIL_CLASS="missing_secrets_or_vars"
  elif grep -qiE 'network .* declared as external|network .* not found' "$errfile"; then
    COMPOSE_FAIL_CLASS="missing_network"
  elif grep -qiE 'no such file|failed to read|open .*: no such file' "$errfile"; then
    COMPOSE_FAIL_CLASS="missing_external_file"
  elif grep -qiE 'yaml:|json:|invalid|parsing|unexpected' "$errfile"; then
    COMPOSE_FAIL_CLASS="compose_syntax"
  fi
}

compose_config_check() {
  # Args: label dir composefile
  local label="$1" dir="$2" file="$3"
  local err
  err="$(mktemp)"
  if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
    warn "compose validation skipped ($label): docker compose unavailable"
    rm -f "$err"
    return 0
  fi
  if (
    cd "$dir"
    docker compose -f "$file" config --quiet 2>"$err"
  ); then
    # Still surface soft warnings from stderr (compose may warn and succeed)
    if [[ -s "$err" ]]; then
      if grep -qiE 'variable is not set' "$err"; then
        warn "compose $label: unset variables (missing secrets/vars) — $(tr '\n' ' ' <"$err" | head -c 200)"
      else
        info "compose $label: config OK (with messages)"
      fi
    else
      info "compose $label: config OK"
    fi
    rm -f "$err"
    return 0
  fi

  classify_compose_failure "$err"
  case "$COMPOSE_FAIL_CLASS" in
    missing_env_file)
      warn "compose $label: missing .env file — create from .env.example before --execute/--apply-compose"
      ;;
    missing_secrets_or_vars)
      warn "compose $label: missing secrets/vars — $COMPOSE_FAIL_DETAIL"
      ;;
    missing_network)
      warn "compose $label: missing external network — $COMPOSE_FAIL_DETAIL"
      ;;
    missing_external_file)
      warn "compose $label: missing external file/path — $COMPOSE_FAIL_DETAIL"
      ;;
    compose_syntax)
      warn "compose $label: YAML/syntax error — $COMPOSE_FAIL_DETAIL"
      ;;
    *)
      warn "compose $label: validation failed ($COMPOSE_FAIL_CLASS) — $COMPOSE_FAIL_DETAIL"
      ;;
  esac
  rm -f "$err"

  if is_execute && is_apply_compose; then
    die "compose $label validation failed hard in execute+apply mode"
  fi
  return 0
}

print_operator_summary() {
  local svc="${CURRENT_SERVICE:-unknown}"
  echo
  echo "-------------------------------------"
  echo "Service: $svc"
  echo "Dry Run: $(is_dry_run && echo yes || echo no) | Status: $RUN_STATUS"
  echo "Source:"
  echo "  ${SVC_SOURCE:-"(none)"}"
  echo "Destination:"
  echo "  ${SVC_TARGET:-"(none)"}"
  echo "Copy Required:"
  echo "  $COPY_REQUIRED"
  if [[ -n "${SVC_EXCLUDES:-}" ]]; then
    echo "Rsync Excludes:"
    echo "  $SVC_EXCLUDES"
  fi
  echo "Compose Update:"
  echo "  $COMPOSE_UPDATE_NEEDED"
  echo "Verification:"
  echo "  $VERIFICATION_STATUS"
  echo "Rollback:"
  echo "  Available"
  echo "Warnings:"
  echo "  ${#WARN_LIST[@]}"
  if ((${#WARN_LIST[@]} > 0)); then
    local w
    for w in "${WARN_LIST[@]}"; do
      echo "  - $w"
    done
  fi
  echo "Errors:"
  echo "  ${#ERR_LIST[@]}"
  if ((${#ERR_LIST[@]} > 0)); then
    local e
    for e in "${ERR_LIST[@]}"; do
      echo "  - $e"
    done
  fi
  echo "-------------------------------------"
}

# Merge warnings/errors from phase JSON reports into WARN_LIST/ERR_LIST (orchestrator final summary).
load_phase_findings() {
  local svc="$1"
  local f key
  for key in preflight inventory destination copy verify compose migration; do
    f="$PHASE_DIR/reports/${key}-${svc}.json"
    [[ -f "$f" ]] || continue
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      WARN_LIST+=("[$key] $line")
    done < <(python3 -c 'import json,sys; d=json.load(open(sys.argv[1]));
print("\n".join(d.get("warnings") or []))' "$f" 2>/dev/null || true)
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      ERR_LIST+=("[$key] $line")
    done < <(python3 -c 'import json,sys; d=json.load(open(sys.argv[1]));
print("\n".join(d.get("errors") or []))' "$f" 2>/dev/null || true)
  done
}

section() {
  echo
  echo "==== $* ===="
}
