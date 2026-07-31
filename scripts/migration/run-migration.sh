#!/usr/bin/env bash
# Orchestrator A→I. Default --dry-run. Never --execute in Phase 10.5 delivery.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() {
  cat <<'EOF'
Usage: run-migration.sh [--dry-run|--execute] [--apply-compose] [--checksum] [--force-review] [--quiet] <service-key>
EOF
}

parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"
[[ $# -ge 1 ]] || { usage; exit 2; }
SERVICE="$1"

load_service "$SERVICE"
init_service_log "$SERVICE"
ensure_dirs
RUN_PHASE="orchestrator"
log "Started"
section "run-migration: $SERVICE (execute=$MIGRATE_EXECUTE apply_compose=$MIGRATE_APPLY_COMPOSE)"

FLAGS=(--phase-dir "$PHASE_DIR")
is_execute && FLAGS+=(--execute) || FLAGS+=(--dry-run)
[[ "$MIGRATE_APPLY_COMPOSE" == "1" ]] && FLAGS+=(--apply-compose)
[[ "$MIGRATE_CHECKSUM" == "1" ]] && FLAGS+=(--checksum)
[[ "$MIGRATE_FORCE_REVIEW" == "1" ]] && FLAGS+=(--force-review)
[[ "$MIGRATE_QUIET" == "1" ]] && FLAGS+=(--quiet)

run_step() {
  local name="$1"; shift
  section "$name"
  log "$name"
  "$@"
}

# Already migrated
if [[ "$SVC_REQUIRED" == "no" && "$SVC_ALREADY" == "yes" ]]; then
  info "Already on appdata — inventory + path check only"
  run_step "Preflight" "$SCRIPT_DIR/preflight.sh" "${FLAGS[@]}" "$SERVICE" || true
  run_step "Inventory" "$SCRIPT_DIR/inventory.sh" "${FLAGS[@]}" "$SERVICE"
  VERIFICATION_STATUS="skipped_already_migrated"
  RUN_STATUS="SUCCESS"
  write_migration_json "$PHASE_DIR/reports/migration-${SERVICE}.json"
  json_to_markdown "$PHASE_DIR/reports/migration-${SERVICE}.json" "$PHASE_DIR/reports/migration-${SERVICE}.md"
  print_operator_summary
  exit 0
fi

if [[ "$SVC_REQUIRED" == "deferred" ]]; then
  warn "Service is deferred — inventory only; no copy"
  run_step "Inventory" "$SCRIPT_DIR/inventory.sh" "${FLAGS[@]}" "$SERVICE"
  VERIFICATION_STATUS="deferred"
  write_migration_json "$PHASE_DIR/reports/migration-${SERVICE}.json"
  print_operator_summary
  exit 0
fi

run_step "Preflight" "$SCRIPT_DIR/preflight.sh" "${FLAGS[@]}" "$SERVICE"
run_step "Inventory" "$SCRIPT_DIR/inventory.sh" "${FLAGS[@]}" "$SERVICE"

if [[ -n "$SVC_TARGET" && "$SVC_TARGET" == /mnt/monarch/appdata/* ]]; then
  run_step "Verify destination" "$SCRIPT_DIR/verify-destination.sh" "${FLAGS[@]}" "$SERVICE"
fi

# Phase C: inspect only in dry-run; stop only on execute
IFS=',' read -ra CNS <<<"$SVC_CONTAINERS"
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  TS="$(date -u +%Y%m%dT%H%M%SZ)"
  for c in "${CNS[@]}"; do
    [[ -z "$c" ]] && continue
    if docker inspect "$c" >/dev/null 2>&1; then
      OUT="$PHASE_DIR/inspect/${SERVICE}-${c}-${TS}.json"
      docker inspect "$c" >"$OUT"
      info "Saved docker inspect → $OUT"
    else
      warn "Container not found for inspect: $c (may be stopped or named differently)"
    fi
  done
  if is_execute && [[ "$SVC_REQUIRED" == "yes" ]]; then
    for c in "${CNS[@]}"; do
      [[ -z "$c" ]] && continue
      info "Stopping container $c"
      docker stop "$c"
    done
  else
    info "[dry-run] would stop containers: $SVC_CONTAINERS"
  fi
else
  warn "Docker unavailable — skip inspect/stop"
fi

if [[ -n "$SVC_SOURCE" && -n "$SVC_TARGET" && ( "$SVC_REQUIRED" == "yes" || "$SVC_REQUIRED" == "verify" ) ]]; then
  if [[ "$SVC_REQUIRED" == "yes" ]]; then
    run_step "Copy configuration" "$SCRIPT_DIR/copy-config.sh" "${FLAGS[@]}" "$SERVICE"
    run_step "Verify copy" "$SCRIPT_DIR/verify-service.sh" "${FLAGS[@]}" "$SERVICE"
    run_step "Update compose" "$SCRIPT_DIR/update-compose.sh" "${FLAGS[@]}" "$SERVICE"
  else
    info "verify-only service — no copy; confirm live paths match PATH_*/appdata"
    VERIFICATION_STATUS="verify_only"
  fi
fi

if is_execute && command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  COMPOSE_DIR="$(dirname "$SVC_COMPOSE_ABS")"
  COMPOSE_BASE="$(basename "$SVC_COMPOSE_ABS")"
  info "Starting via docker compose up -d (this project only)"
  (
    cd "$COMPOSE_DIR"
    docker compose -f "$COMPOSE_BASE" up -d
  )
  # --smoke-only: the copy gate already ran pre-start. Re-comparing source and
  # destination now would flag the logs/caches the freshly started service is
  # writing to its new config path as verification failures.
  run_step "Smoke" "$SCRIPT_DIR/verify-service.sh" "${FLAGS[@]}" --smoke-only "$SERVICE"
else
  info "[dry-run] would start compose project $SVC_COMPOSE"
fi

if [[ -z "${VERIFICATION_STATUS:-}" || "$VERIFICATION_STATUS" == "n/a" ]]; then
  VERIFICATION_STATUS="orchestrator_complete"
fi
is_dry_run && RUN_STATUS="SUCCESS" || RUN_STATUS="${RUN_STATUS:-SUCCESS}"
if [[ -n "$SVC_SOURCE" && -e "$SVC_SOURCE" ]]; then
  count_tree_stats "$SVC_SOURCE"
fi
# Rebuild warning list from phase reports so final summary is complete
WARN_LIST=()
ERR_LIST=()
load_phase_findings "$SERVICE"
write_migration_json "$PHASE_DIR/reports/migration-${SERVICE}.json"
json_to_markdown "$PHASE_DIR/reports/migration-${SERVICE}.json" "$PHASE_DIR/reports/migration-${SERVICE}.md"
log "Finished"
echo
echo "==== FINAL SUMMARY ===="
print_operator_summary
info "Report: $PHASE_DIR/reports/migration-${SERVICE}.json"
info "Rollback helper: $SCRIPT_DIR/rollback.sh [--execute] $SERVICE"
info "NOTE: originals are NOT renamed to .old automatically; do that manually after soak."
