#!/usr/bin/env bash
# Phase D: rsync copy (dry-run default). Never deletes source. Never cp -r.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() { echo "Usage: copy-config.sh [--dry-run|--execute] [--force-review] [--quiet] <service-key>"; }

parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"
[[ $# -ge 1 ]] || { usage; exit 2; }
SERVICE="$1"
load_service "$SERVICE"
init_service_log "$SERVICE"
RUN_PHASE="copy"

[[ -n "$SVC_SOURCE" ]] || die "No source_config for $SERVICE"
[[ -n "$SVC_TARGET" ]] || die "No target_config for $SERVICE"
assert_source_path "$SVC_SOURCE"
assert_target_path "$SVC_TARGET"
command -v rsync >/dev/null 2>&1 || die "rsync required"

section "Copy: $SERVICE"
if [[ ! -e "$SVC_SOURCE" ]]; then
  if is_dry_run; then
    warn "Source missing offline: $SVC_SOURCE — dry-run continues without rsync"
    VERIFICATION_STATUS="copy_skipped_missing_source"
    write_migration_json "$PHASE_DIR/reports/copy-${SERVICE}.json"
    print_operator_summary
    exit 0
  fi
  die "Source missing: $SVC_SOURCE"
fi

SRC="${SVC_SOURCE%/}/"
DST="${SVC_TARGET%/}/"
rsync_exclude_args

RSYNC_OPTS=(-aHAX)
if ((${#RSYNC_EXCLUDE_ARGS[@]} > 0)); then
  RSYNC_OPTS+=("${RSYNC_EXCLUDE_ARGS[@]}")
  info "rsync excludes: ${SVC_EXCLUDES}"
fi

if is_dry_run; then
  RSYNC_OPTS+=(-n --info=stats2)
  info "[dry-run] rsync ${RSYNC_OPTS[*]} $SRC → $DST"
  rsync "${RSYNC_OPTS[@]}" "$SRC" "$DST" || warn "rsync dry-run returned non-zero (permission gaps possible)"
  log "Copy complete (dry-run)"
  VERIFICATION_STATUS="copy_dry_run_complete"
else
  RSYNC_OPTS+=(--info=progress2)
  mkdir -p "$SVC_TARGET"
  info "rsync ${RSYNC_OPTS[*]} $SRC → $DST"
  rsync "${RSYNC_OPTS[@]}" "$SRC" "$DST"
  log "Copy complete"
  VERIFICATION_STATUS="copy_complete"
fi

count_tree_stats "$SVC_SOURCE"
write_migration_json "$PHASE_DIR/reports/copy-${SERVICE}.json"
print_operator_summary
