#!/usr/bin/env bash
# Phase F: propose compose path updates; apply only with --apply-compose.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() {
  cat <<'EOF'
Usage: update-compose.sh [--dry-run|--execute] [--apply-compose] <service-key>

Always writes proposed compose under Validation/Phase10.5/proposed/.
Classifies compose validation failures (missing .env, secrets, networks, syntax).
Hard-fail only when --execute --apply-compose.
EOF
}

parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"
[[ $# -ge 1 ]] || { usage; exit 2; }
SERVICE="$1"
load_service "$SERVICE"
init_service_log "$SERVICE"
RUN_PHASE="update-compose"

[[ -f "$SVC_COMPOSE_ABS" ]] || die "Compose missing: $SVC_COMPOSE_ABS"
[[ -n "$SVC_SOURCE" && -n "$SVC_TARGET" ]] || {
  info "No source→target rewrite for $SERVICE"
  VERIFICATION_STATUS="compose_n/a"
  write_migration_json "$PHASE_DIR/reports/compose-${SERVICE}.json"
  print_operator_summary
  exit 0
}

assert_source_path "$SVC_SOURCE"
assert_target_path "$SVC_TARGET"

VERIFY_JSON="$PHASE_DIR/reports/verify-${SERVICE}.json"
if is_apply_compose && [[ "$SVC_ALREADY" != "yes" ]]; then
  if [[ ! -f "$VERIFY_JSON" ]] || ! grep -q '"status": "SUCCESS"\|"verification_status": "copy_verified"' "$VERIFY_JSON" 2>/dev/null; then
    if is_execute; then
      die "Refusing --apply-compose without successful verify report: $VERIFY_JSON"
    else
      warn "No successful verify report yet — propose-only is OK in dry-run"
    fi
  fi
fi

COMPOSE_DIR="$(dirname "$SVC_COMPOSE_ABS")"
COMPOSE_BASE="$(basename "$SVC_COMPOSE_ABS")"
PROPOSED_DIR="$PHASE_DIR/proposed/${SERVICE}"
mkdir -p "$PROPOSED_DIR"
PROPOSED="$PROPOSED_DIR/$COMPOSE_BASE"
BACKUP="$PROPOSED_DIR/${COMPOSE_BASE}.pre-migrate.bak"

section "Compose update: $SERVICE"
if grep -Fq "$SVC_SOURCE" "$SVC_COMPOSE_ABS"; then
  sed "s|$SVC_SOURCE|$SVC_TARGET|g" "$SVC_COMPOSE_ABS" >"$PROPOSED"
  info "Proposed rewrite: $SVC_SOURCE → $SVC_TARGET"
else
  cp -a "$SVC_COMPOSE_ABS" "$PROPOSED"
  warn "Source path string not found verbatim in compose — proposed file is a copy for manual edit (live drift possible)"
fi

compose_config_check "CURRENT" "$COMPOSE_DIR" "$COMPOSE_BASE"

# Proposed lives under Validation/.../proposed/<service>/, which does not inherit
# the project's gitignored .env. Copy it in for validation only — the applied
# compose still resolves env_file relative to the real services/<svc>/ directory.
if [[ -f "$COMPOSE_DIR/.env" && ! -f "$PROPOSED_DIR/.env" ]]; then
  cp -a "$COMPOSE_DIR/.env" "$PROPOSED_DIR/.env"
  info "Staged .env into proposed dir for compose validation"
fi
compose_config_check "PROPOSED" "$PROPOSED_DIR" "$COMPOSE_BASE"

diff -u "$SVC_COMPOSE_ABS" "$PROPOSED" >"$PROPOSED_DIR/compose.diff" || true
info "Proposed: $PROPOSED"
info "Diff:     $PROPOSED_DIR/compose.diff"

if ! is_apply_compose; then
  info "Compose NOT applied (pass --apply-compose after review)"
  VERIFICATION_STATUS="compose_proposed"
  write_migration_json "$PHASE_DIR/reports/compose-${SERVICE}.json"
  print_operator_summary
  exit 0
fi

if is_dry_run; then
  info "[dry-run] would backup to $BACKUP and replace $SVC_COMPOSE_ABS"
  VERIFICATION_STATUS="compose_apply_dry_run"
  write_migration_json "$PHASE_DIR/reports/compose-${SERVICE}.json"
  print_operator_summary
  exit 0
fi

cp -a "$SVC_COMPOSE_ABS" "$BACKUP"
cp -a "$PROPOSED" "$SVC_COMPOSE_ABS"
info "Applied compose update; backup at $BACKUP"
compose_config_check "AFTER_APPLY" "$COMPOSE_DIR" "$COMPOSE_BASE"
log "Compose updated=true"
VERIFICATION_STATUS="compose_applied"
RUN_STATUS="SUCCESS"
write_migration_json "$PHASE_DIR/reports/compose-${SERVICE}.json"
print_operator_summary
