#!/usr/bin/env bash
# Phase B: verify destination readiness.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() { echo "Usage: verify-destination.sh [--dry-run|--execute] [--force-review] <service-key>"; }
parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"
[[ $# -ge 1 ]] || { usage; exit 2; }
SERVICE="$1"
load_service "$SERVICE"
init_service_log "$SERVICE"
RUN_PHASE="verify-destination"

[[ -n "$SVC_TARGET" ]] || die "No target_config for $SERVICE"
[[ "$SVC_TARGET" == /mnt/monarch/appdata/* ]] || die "Target must be under /mnt/monarch/appdata: $SVC_TARGET"
assert_target_path "$SVC_TARGET"

section "Verify destination: $SERVICE"
PARENT="$(dirname "$SVC_TARGET")"
if mutate_guard "mkdir -p $SVC_TARGET"; then
  mkdir -p "$SVC_TARGET"
  info "Created destination: $SVC_TARGET"
else
  info "[dry-run] plan: mkdir -p $SVC_TARGET (parent=$PARENT)"
fi

if [[ -d /mnt/monarch/appdata ]]; then
  FS_TYPE="$(findmnt -no FSTYPE /mnt/monarch 2>/dev/null || echo unknown)"
  AVAIL="$(df -h --output=avail /mnt/monarch/appdata 2>/dev/null | tail -n1 | tr -d ' ' || echo unknown)"
  info "Filesystem type=$FS_TYPE avail=$AVAIL"
fi

if [[ -d "$SVC_TARGET" ]] && find "$SVC_TARGET" -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
  if [[ "$SVC_ALREADY" == "yes" || "$SVC_REQUIRED" == "verify" ]]; then
    info "Destination already populated — EXPECTED for verify/already_migrated"
  elif [[ "$MIGRATE_FORCE_REVIEW" != "1" && "$SVC_REQUIRED" == "yes" ]]; then
    die "Destination non-empty; refusing without --force-review: $SVC_TARGET"
  else
    warn "Destination non-empty"
  fi
fi

VERIFICATION_STATUS="destination_ok"
write_migration_json "$PHASE_DIR/reports/destination-${SERVICE}.json"
print_operator_summary
