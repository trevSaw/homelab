#!/usr/bin/env bash
# Phase A/B helper: preflight checks (hardened). Never stops containers.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() {
  cat <<'EOF'
Usage: preflight.sh [--dry-run|--execute] [--quiet] <service-key>

Checks: compose file, docker, compose CLI, rsync, /mnt/monarch mount,
source exists (when required), destination safety, free space (migratable estimate),
git dirty (expected warning during framework work), ZFS health.
EOF
}

parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"
[[ $# -ge 1 ]] || { usage; exit 2; }
SERVICE="$1"
load_service "$SERVICE"
init_service_log "$SERVICE"
ensure_dirs
RUN_PHASE="preflight"

CRITICAL=0
crit() { CRITICAL=$((CRITICAL + 1)); ERR_LIST+=("$*"); echo "CRITICAL: $*"; log "CRITICAL: $*"; RUN_STATUS="FAIL"; }

section "Preflight: $SERVICE"

# Required commands
for cmd in bash rsync awk find du df; do
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "command available: $cmd"
  else
    crit "required command missing: $cmd"
  fi
done

[[ -f "$SVC_COMPOSE_ABS" ]] && ok "compose exists: $SVC_COMPOSE" || crit "compose missing: $SVC_COMPOSE_ABS"

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    ok "docker daemon reachable"
  else
    is_execute && crit "docker daemon not reachable" || warn "docker daemon not reachable (OK for offline dry-run)"
  fi
  if docker compose version >/dev/null 2>&1; then
    ok "docker compose available"
  else
    is_execute && crit "docker compose not available" || warn "docker compose not available"
  fi
else
  is_execute && crit "docker not installed" || warn "docker not installed (OK for offline dry-run)"
fi

if [[ -d /mnt/monarch ]]; then
  ok "/mnt/monarch present"
  if mountpoint -q /mnt/monarch 2>/dev/null || findmnt /mnt/monarch >/dev/null 2>&1; then
    ok "/mnt/monarch mounted"
  else
    warn "/mnt/monarch exists but mountpoint check inconclusive"
  fi
  if [[ -d /mnt/monarch/appdata ]]; then
    ok "/mnt/monarch/appdata present"
  else
    is_execute && crit "/mnt/monarch/appdata missing" || warn "/mnt/monarch/appdata missing"
  fi
else
  is_execute && crit "/mnt/monarch missing" || warn "/mnt/monarch missing (offline workstation)"
fi

SRC_BYTES=0
EST_BYTES=0
if [[ -n "$SVC_SOURCE" ]]; then
  if [[ "$SVC_SOURCE" == /hive/* ]]; then
    assert_source_path "$SVC_SOURCE"
    if [[ -e "$SVC_SOURCE" ]]; then
      ok "source exists: $SVC_SOURCE"
      count_tree_stats "$SVC_SOURCE"
      SRC_BYTES=$STAT_BYTES
      estimate_migratable_bytes "$SVC_SOURCE" "${SVC_EXCLUDES:-}" reuse
      EST_BYTES=$EST_BYTES
      info "source tree: $(human_bytes "$SRC_BYTES") files=$STAT_FILES dirs=$STAT_DIRS"
      if [[ -n "${SVC_EXCLUDES:-}" ]]; then
        info "migratable estimate (excludes applied): $(human_bytes "$EST_BYTES") excludes=$SVC_EXCLUDES"
      fi
    else
      if [[ "$SVC_REQUIRED" == "yes" ]]; then
        is_execute && crit "source missing: $SVC_SOURCE" || warn "source missing (offline?): $SVC_SOURCE"
      else
        warn "source path not present: $SVC_SOURCE"
      fi
    fi
  else
    warn "source is not under /hive/ (special case): $SVC_SOURCE"
  fi
else
  ok "no source_config (verify / already-migrated / deferred)"
fi

if [[ -n "$SVC_TARGET" && "$SVC_TARGET" == /mnt/monarch/appdata/* ]]; then
  assert_target_path "$SVC_TARGET"
  if [[ -d "$SVC_TARGET" ]]; then
    if find "$SVC_TARGET" -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
      if [[ "$SVC_ALREADY" == "yes" || "$SVC_REQUIRED" == "verify" ]]; then
        ok "destination populated (EXPECTED for already_migrated/verify): $SVC_TARGET"
      elif [[ "$MIGRATE_FORCE_REVIEW" == "1" ]]; then
        warn "destination non-empty; --force-review set: $SVC_TARGET"
      else
        if is_execute && [[ "$SVC_REQUIRED" == "yes" ]]; then
          crit "destination non-empty; refuse overwrite without --force-review: $SVC_TARGET"
        else
          warn "destination non-empty (review before execute): $SVC_TARGET"
        fi
      fi
    else
      ok "destination empty: $SVC_TARGET"
    fi
  else
    ok "destination does not exist yet (mkdir in verify-destination): $SVC_TARGET"
  fi

  if [[ -d /mnt/monarch/appdata ]]; then
    AVAIL="$(df -B1 --output=avail /mnt/monarch/appdata 2>/dev/null | tail -n1 | tr -d '[:space:]' || echo 0)"
    USE_BYTES="$EST_BYTES"
    USE_BYTES="$(printf '%s' "$USE_BYTES" | tr -d '[:space:]')"
    SRC_BYTES="$(printf '%s' "$SRC_BYTES" | tr -d '[:space:]')"
    [[ "$USE_BYTES" =~ ^[0-9]+$ ]] || USE_BYTES=0
    [[ "$SRC_BYTES" =~ ^[0-9]+$ ]] || SRC_BYTES=0
    (( USE_BYTES > 0 )) || USE_BYTES=$SRC_BYTES
    if [[ "$USE_BYTES" =~ ^[0-9]+$ ]] && (( USE_BYTES > 0 )) && [[ "$AVAIL" =~ ^[0-9]+$ ]]; then
      NEED=$((USE_BYTES + USE_BYTES / 10 + 104857600))
      if (( AVAIL >= NEED )); then
        ok "free SSD space $(human_bytes "$AVAIL") >= need ~$(human_bytes "$NEED")"
      else
        crit "insufficient free SSD space: avail=$(human_bytes "$AVAIL") need~$(human_bytes "$NEED")"
      fi
    else
      info "free-space vs source skipped (no migratable byte estimate)"
    fi
  fi
elif [[ -n "$SVC_TARGET" ]]; then
  warn "target not under /mnt/monarch/appdata (special/deferred): $SVC_TARGET"
fi

# Permissions hint on source
if [[ -n "$SVC_SOURCE" && -e "$SVC_SOURCE" ]]; then
  info "source ownership: $(ls -ld "$SVC_SOURCE" | awk '{print $3":"$4" mode="$1}')"
fi

if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [[ -z "$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null)" ]]; then
    ok "git working tree clean"
  else
    warn "git working tree not clean — EXPECTED while Phase 10.5 framework changes are uncommitted"
  fi
fi

if command -v zpool >/dev/null 2>&1; then
  ZMSG="$(zpool status -x 2>/dev/null || true)"
  if echo "$ZMSG" | grep -qi 'all pools are healthy'; then
    ok "ZFS: all pools healthy"
  elif echo "$ZMSG" | grep -qi 'no pools available'; then
    warn "ZFS: no pools available on this host"
  else
    warn "ZFS status: $ZMSG"
  fi
else
  info "zpool not available (OK off mocha)"
fi

log "Preflight complete critical=$CRITICAL warnings=${#WARN_LIST[@]}"
echo
echo "Preflight summary: CRITICAL=$CRITICAL WARNINGS=${#WARN_LIST[@]} service=$SERVICE"
VERIFICATION_STATUS="preflight_ok"
(( CRITICAL > 0 )) && VERIFICATION_STATUS="preflight_failed"
write_migration_json "$PHASE_DIR/reports/preflight-${SERVICE}.json"
print_operator_summary
(( CRITICAL > 0 )) && exit 1
exit 0
