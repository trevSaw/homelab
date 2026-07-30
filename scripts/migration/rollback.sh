#!/usr/bin/env bash
# Phase I: rollback compose/data via rename — NEVER rm -rf.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() {
  echo "Usage: rollback.sh [--dry-run|--execute] <service-key> [--compose-only|--data-only]"
}

parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"
[[ $# -ge 1 ]] || { usage; exit 2; }
SERVICE="$1"
shift || true
MODE="all"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --compose-only) MODE="compose"; shift ;;
    --data-only) MODE="data"; shift ;;
    *) die "Unknown arg: $1" ;;
  esac
done

load_service "$SERVICE"
init_service_log "$SERVICE"
RUN_PHASE="rollback"

COMPOSE_BASE="$(basename "$SVC_COMPOSE")"
BACKUP="$PHASE_DIR/proposed/${SERVICE}/${COMPOSE_BASE}.pre-migrate.bak"

section "Rollback: $SERVICE ($MODE)"

rollback_compose() {
  if [[ ! -f "$BACKUP" ]]; then
    warn "No compose backup at $BACKUP"
    return 0
  fi
  if mutate_guard "restore compose from $BACKUP → $SVC_COMPOSE_ABS"; then
    cp -a "$BACKUP" "$SVC_COMPOSE_ABS"
    info "Compose restored"
    compose_config_check "ROLLBACK" "$(dirname "$SVC_COMPOSE_ABS")" "$COMPOSE_BASE"
  fi
}

rollback_data() {
  [[ -n "$SVC_SOURCE" ]] || { info "No source_config — skip data rollback"; return 0; }
  local old="${SVC_SOURCE%/}.old"
  if [[ ! -e "$old" ]]; then
    warn "No retired source at $old — originals may still be at $SVC_SOURCE"
    return 0
  fi
  if [[ -e "$SVC_SOURCE" ]]; then
    die "Cannot restore $old because $SVC_SOURCE exists — resolve manually"
  fi
  if mutate_guard "mv $old → $SVC_SOURCE"; then
    if [[ -n "$SVC_TARGET" && -e "$SVC_TARGET" ]]; then
      local rolled="${SVC_TARGET%/}.rolled.$(date +%Y%m%d%H%M%S)"
      assert_target_path "$SVC_TARGET"
      mv "$SVC_TARGET" "$rolled"
      info "Moved target aside to $rolled"
    fi
    assert_source_path "$SVC_SOURCE"
    mv "$old" "$SVC_SOURCE"
    info "Restored source from $old"
  fi
}

case "$MODE" in
  compose) rollback_compose ;;
  data) rollback_data ;;
  all) rollback_compose; rollback_data ;;
esac

VERIFICATION_STATUS="rollback_complete"
write_migration_json "$PHASE_DIR/reports/rollback-${SERVICE}.json"
print_operator_summary
