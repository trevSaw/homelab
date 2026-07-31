#!/usr/bin/env bash
# Phase E (+ optional H): verify copy metrics / smoke.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() { echo "Usage: verify-service.sh [--dry-run|--execute] [--checksum] [--smoke-only] <service-key>"; }
parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"
[[ $# -ge 1 ]] || { usage; exit 2; }
SERVICE="$1"
load_service "$SERVICE"
init_service_log "$SERVICE"
RUN_PHASE="verify"

section "Verify: $SERVICE"

# Post-start smoke: the service is already writing to the destination, so any
# source↔dest compare here measures live divergence rather than copy fidelity.
# The copy gate has already run (pre-start) and cannot be skipped by this path.
if [[ "${MIGRATE_SMOKE_ONLY:-0}" == "1" ]]; then
  info "Smoke-only mode — container state check; copy comparison already gated pre-start"
  report_container_states
  RUN_STATUS="SUCCESS"
  VERIFICATION_STATUS="smoke_complete"
  write_migration_json "$PHASE_DIR/reports/smoke-${SERVICE}.json"
  print_operator_summary
  exit 0
fi

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
  # Inventories are built and compared under LC_ALL=C and keyed by path, so the
  # verdict depends only on which files exist and what they contain — never on
  # the order the filesystem happened to enumerate them in. See the block
  # comment above build_checksum_inventory in lib/common.sh.
  info "Checksum compare enabled (LC_ALL=C byte order, set comparison keyed by path)"
  CK_REPORT="$PHASE_DIR/reports/checksum-diff-${SERVICE}.txt"
  rm -f "$CK_REPORT"
  SRC_INV="$(mktemp)"; DST_INV="$(mktemp)"

  # Source honours rsync_excludes (excluded files were never meant to be copied);
  # destination is inventoried in full so anything unexpected shows up as EXTRA.
  build_checksum_inventory "$SVC_SOURCE" "$SRC_INV" "${SVC_EXCLUDES:-}"
  S_INV=$INVENTORY_RECORDS
  if (( INVENTORY_SKIPPED > 0 )); then
    warn "Source inventory incomplete: $INVENTORY_SKIPPED file(s) unreadable or contain newlines — cannot verify"
    FAIL=1
  fi
  build_checksum_inventory "$SVC_TARGET" "$DST_INV" ""
  D_INV=$INVENTORY_RECORDS
  if (( INVENTORY_SKIPPED > 0 )); then
    warn "Destination inventory incomplete: $INVENTORY_SKIPPED file(s) unreadable or contain newlines — cannot verify"
    FAIL=1
  fi
  info "Inventory records: source=$S_INV dest=$D_INV"

  compare_checksum_inventories "$SRC_INV" "$DST_INV" "$CK_REPORT"
  rm -f "$SRC_INV" "$DST_INV"

  if (( CHECKSUM_MISSING > 0 || CHECKSUM_CHANGED > 0 || CHECKSUM_EXTRA > 0 )); then
    warn "Checksum mismatch: missing=$CHECKSUM_MISSING changed=$CHECKSUM_CHANGED extra=$CHECKSUM_EXTRA matched=$CHECKSUM_MATCHED"
    warn "Differing files listed in: $CK_REPORT"
    FAIL=1
  else
    info "Checksum inventory matches: $CHECKSUM_MATCHED file(s) identical (missing=0 changed=0 extra=0)"
  fi
fi

if is_execute; then
  report_container_states
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
