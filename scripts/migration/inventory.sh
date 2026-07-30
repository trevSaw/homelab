#!/usr/bin/env bash
# Phase A: inventory one service or all (read-only).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() {
  echo "Usage: inventory.sh [--quiet] [<service-key>|--all]"
}

parse_migrate_flags "$@" || { usage; exit 2; }
set -- "${REMAINING_ARGS[@]:-}"

inventory_one() {
  local key="$1"
  load_service "$key"
  init_service_log "$key"
  RUN_PHASE="inventory"

  echo "-------------------------------------"
  echo "Inventory: $SVC_KEY"
  echo "Compose:   $SVC_COMPOSE"
  echo "Containers:$SVC_CONTAINERS"
  echo "Source:    ${SVC_SOURCE:-"(none)"}"
  echo "Target:    ${SVC_TARGET:-"(none)"}"
  echo "Keep/hive: ${SVC_KEEP:-"(none)"}"
  echo "Excludes:  ${SVC_EXCLUDES:-"(none)"}"
  echo "Risk/Order:$SVC_RISK / $SVC_ORDER"
  echo "Required:  $SVC_REQUIRED | Already: $SVC_ALREADY"
  echo "Notes:     $SVC_NOTES"
  echo "Mounts:"
  if [[ -f "$SVC_COMPOSE_ABS" ]]; then
    grep -E '^\s+- .*:|source:|/hive|/mnt/monarch|\./|PATH_' "$SVC_COMPOSE_ABS" | sed 's/^/  /' || true
  else
    echo "  (compose missing)"
  fi

  if [[ -n "$SVC_SOURCE" && -e "$SVC_SOURCE" ]]; then
    count_tree_stats "$SVC_SOURCE"
    estimate_migratable_bytes "$SVC_SOURCE" "${SVC_EXCLUDES:-}"
    echo "Source stats: $(human_bytes "$STAT_BYTES") files=$STAT_FILES dirs=$STAT_DIRS"
    if [[ -n "${SVC_EXCLUDES:-}" ]]; then
      echo "Migratable:   $(human_bytes "$EST_BYTES") (after excludes)"
    fi
  elif [[ -n "$SVC_SOURCE" ]]; then
    warn "source not present on this host: $SVC_SOURCE"
  fi

  # Live mount drift hint (homepage-style)
  if [[ -n "$SVC_CONTAINERS" ]] && command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    local c
    IFS=',' read -ra CNS <<<"$SVC_CONTAINERS"
    for c in "${CNS[@]}"; do
      [[ -z "$c" ]] && continue
      if docker inspect "$c" >/dev/null 2>&1; then
        local mounts
        mounts="$(docker inspect -f '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}' "$c" 2>/dev/null || true)"
        if [[ -n "$mounts" ]]; then
          echo "Live mounts ($c):"
          echo "$mounts" | sed 's/^/  /'
        fi
      fi
    done
  fi

  VERIFICATION_STATUS="inventory_complete"
  write_migration_json "$PHASE_DIR/reports/inventory-${key}.json"
  json_to_markdown "$PHASE_DIR/reports/inventory-${key}.json" "$PHASE_DIR/reports/inventory-${key}.md"
  print_operator_summary
}

ensure_dirs
if [[ $# -lt 1 || "$1" == "--all" ]]; then
  while IFS= read -r key; do
    inventory_one "$key" || warn "inventory failed for $key (see warnings)"
    echo
  done < <(list_service_keys)
else
  inventory_one "$1"
fi
