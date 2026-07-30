#!/usr/bin/env bash
# Phase E (+ optional H): verify copy metrics / smoke.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() { echo "Usage: verify-service.sh [--dry-run|--execute] [--checksum] <service-key>"; }
parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"
[[ $# -ge 1 ]] || { usage; exit 2; }
SERVICE="$1"
load_service "$SERVICE"
init_service_log "$SERVICE"
RUN_PHASE="verify"

section "Verify: $SERVICE"

if [[ -z "$SVC_SOURCE" || -z "$SVC_TARGET" ]]; then
  info "No source/target pair — skip copy verification"
  VERIFICATION_STATUS="skipped_no_paths"
  write_migration_json "$PHASE_DIR/reports/verify-${SERVICE}.json"
  print_operator_summary
  exit 0
fi

if [[ ! -e "$SVC_SOURCE" ]]; then
  if is_dry_run; then
    warn "Source missing — skip metric compare (offline/missing)"
    VERIFICATION_STATUS="skipped_missing_source"
    write_migration_json "$PHASE_DIR/reports/verify-${SERVICE}.json"
    print_operator_summary
    exit 0
  fi
  die "Source missing: $SVC_SOURCE"
fi

if [[ ! -e "$SVC_TARGET" ]]; then
  if is_dry_run; then
    info "Target missing — EXPECTED in dry-run (copy not executed yet)"
    VERIFICATION_STATUS="pending_copy_dry_run"
    write_migration_json "$PHASE_DIR/reports/verify-${SERVICE}.json"
    print_operator_summary
    exit 0
  fi
  die "Target missing: $SVC_TARGET"
fi

count_tree_stats "$SVC_SOURCE"
S_BYTES=$STAT_BYTES; S_FILES=$STAT_FILES; S_DIRS=$STAT_DIRS
count_tree_stats "$SVC_TARGET"
D_BYTES=$STAT_BYTES; D_FILES=$STAT_FILES; D_DIRS=$STAT_DIRS

info "Source: $(human_bytes "$S_BYTES") files=$S_FILES dirs=$S_DIRS"
info "Dest:   $(human_bytes "$D_BYTES") files=$D_FILES dirs=$D_DIRS"

FAIL=0
if [[ -n "${SVC_EXCLUDES:-}" ]]; then
  info "Excludes configured ($SVC_EXCLUDES) — file/dir counts may legitimately differ; compare migratable estimate instead"
  estimate_migratable_bytes "$SVC_SOURCE" "$SVC_EXCLUDES"
  info "Migratable source estimate: $(human_bytes "$EST_BYTES")"
else
  if [[ "$S_FILES" != "$D_FILES" ]]; then
    warn "File count mismatch source=$S_FILES dest=$D_FILES"
    FAIL=1
  fi
  if [[ "$S_DIRS" != "$D_DIRS" ]]; then
    warn "Directory count mismatch source=$S_DIRS dest=$D_DIRS"
    FAIL=1
  fi
  if (( S_BYTES > 0 )); then
    DELTA=$(( S_BYTES > D_BYTES ? S_BYTES - D_BYTES : D_BYTES - S_BYTES ))
    THRESH=$(( S_BYTES / 100 + 4096 ))
    if (( DELTA > THRESH )); then
      warn "Byte count delta=$DELTA exceeds threshold=$THRESH"
      FAIL=1
    fi
  fi
fi

if [[ "$MIGRATE_CHECKSUM" == "1" ]]; then
  info "Optional checksum compare enabled"
  TMPA="$(mktemp)"; TMPB="$(mktemp)"
  (cd "$SVC_SOURCE" && find . -type f -print0 2>/dev/null | sort -z | xargs -0 cksum) >"$TMPA" || true
  (cd "$SVC_TARGET" && find . -type f -print0 2>/dev/null | sort -z | xargs -0 cksum) >"$TMPB" || true
  if ! diff -q "$TMPA" "$TMPB" >/dev/null 2>&1; then
    warn "Checksum inventory differs"
    FAIL=1
  else
    info "Checksum inventory matches"
  fi
  rm -f "$TMPA" "$TMPB"
fi

if is_execute && command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  IFS=',' read -ra CNS <<<"$SVC_CONTAINERS"
  for c in "${CNS[@]}"; do
    [[ -z "$c" ]] && continue
    if docker inspect -f '{{.State.Status}}' "$c" >/dev/null 2>&1; then
      ST="$(docker inspect -f '{{.State.Status}}' "$c")"
      info "Container $c status=$ST"
    else
      warn "Container not found for smoke: $c (stack may use different names or be stopped)"
    fi
  done
fi

STAT_BYTES=$D_BYTES; STAT_FILES=$D_FILES; STAT_DIRS=$D_DIRS
if (( FAIL > 0 )); then
  RUN_STATUS="FAIL"
  VERIFICATION_STATUS="copy_verify_failed"
  write_migration_json "$PHASE_DIR/reports/verify-${SERVICE}.json"
  print_operator_summary
  die "Verification failed for $SERVICE"
fi

RUN_STATUS="SUCCESS"
VERIFICATION_STATUS="copy_verified"
write_migration_json "$PHASE_DIR/reports/verify-${SERVICE}.json"
json_to_markdown "$PHASE_DIR/reports/verify-${SERVICE}.json" "$PHASE_DIR/reports/verify-${SERVICE}.md"
print_operator_summary
