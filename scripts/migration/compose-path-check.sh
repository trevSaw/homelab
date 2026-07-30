#!/usr/bin/env bash
# Offline compose path safety check (hardened messaging).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

ensure_dirs
WARN=0
FAIL=0
REPORT_MD="$PHASE_DIR/Compose_Path_Check_Runtime.md"
SHARED_HOST_MOUNTS="/var/run/docker.sock|/etc/localtime|/dev/dri"

{
  echo "# Compose path check (runtime)"
  echo
  echo "Generated: $(timestamp)"
  echo
  echo "Shared host mounts (docker.sock, localtime, dri) appearing in multiple compose files are EXPECTED — not duplicates to fix."
  echo
} >"$REPORT_MD"

mapfile -t COMPOSE_FILES < <(
  find "$REPO_ROOT/services" -type f \( \
    -name 'compose.yml' -o -name 'compose.yaml' -o \
    -name 'docker-compose.yml' -o -name 'docker-compose.yaml' \
  \) ! -path '*/needing-to-be-deleted/*' | sort
)

declare -A SEEN_MOUNTS=()

check_file() {
  local f="$1"
  local rel="${f#$REPO_ROOT/}"
  echo "## $rel" >>"$REPORT_MD"
  local line host
  while IFS= read -r line; do
    host=""
    if [[ "$line" =~ source:[[:space:]]*(.+) ]]; then
      host="${BASH_REMATCH[1]}"
      host="${host%\"}"; host="${host#\"}"
    elif [[ "$line" =~ ^[[:space:]]*-[[:space:]]+([^:]+:.+) ]]; then
      local vol="${BASH_REMATCH[1]}"
      [[ "$vol" == /* || "$vol" == ./* || "$vol" == \$\{* ]] || continue
      host="${vol%%:*}"
    else
      continue
    fi
    host="${host//\"/}"
    [[ -z "$host" ]] && continue
    echo "- mount host: \`$host\`" >>"$REPORT_MD"

    if [[ "$host" =~ ^($SHARED_HOST_MOUNTS)$ ]]; then
      echo "  - INFO shared host mount (EXPECTED if seen in multiple stacks)" >>"$REPORT_MD"
      SEEN_MOUNTS[$host]="$rel"
      continue
    fi

    if [[ -n "${SEEN_MOUNTS[$host]:-}" && "${SEEN_MOUNTS[$host]}" != "$rel" ]]; then
      echo "  - WARN duplicate data path also in ${SEEN_MOUNTS[$host]} (confirm intentional shared library/media)" >>"$REPORT_MD"
      WARN=$((WARN + 1))
    else
      SEEN_MOUNTS[$host]="$rel"
    fi

    case "$host" in
      /hive/jellyfin/tv|/hive/jellyfin/movie|/hive/downloads*|/hive/library*|/hive/cloud/data*|/hive/backups*|/hive/echoos|/hive/NZBget/config/downloads*)
        echo "  - OK keep-on-hive dataset" >>"$REPORT_MD"
        ;;
      /hive/ollama)
        echo "  - INFO ollama legacy path (migrate config+models → /mnt/monarch/appdata/ollama)" >>"$REPORT_MD"
        ;;
      /hive/config/*|/hive/data/*)
        echo "  - INFO live legacy PATH under /hive/config|/hive/data (homepage-style drift)" >>"$REPORT_MD"
        ;;
      /hive/*)
        echo "  - INFO legacy /hive path (candidate or keep)" >>"$REPORT_MD"
        ;;
      /mnt/monarch/appdata/*)
        echo "  - INFO appdata path" >>"$REPORT_MD"
        ;;
      \$\{PATH_DATA\}*|\$\{PATH_CONFIG\}*)
        echo "  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata when env set)" >>"$REPORT_MD"
        ;;
      ./*|../*)
        echo "  - INFO relative path" >>"$REPORT_MD"
        ;;
      /var/run/docker.sock|/etc/localtime|/dev/dri|/var/run/dbus/*|/var/lib/cosmos|/)
        echo "  - INFO host-system mount" >>"$REPORT_MD"
        ;;
      /mnt/monarch|/hive)
        echo "  - WARN whole-pool mount (tooling) — do not treat as migratable config" >>"$REPORT_MD"
        WARN=$((WARN + 1))
        ;;
      *)
        echo "  - WARN unsupported/unknown host path" >>"$REPORT_MD"
        WARN=$((WARN + 1))
        ;;
    esac
    if [[ "$host" == *"<"* || "$host" == *YOUR_* ]]; then
      echo "  - FAIL broken/placeholder path" >>"$REPORT_MD"
      FAIL=$((FAIL + 1))
    fi
  done < <(grep -E 'source:|^\s+- .*:|/hive|/mnt/monarch|PATH_' "$f" || true)
  echo >>"$REPORT_MD"
}

for f in "${COMPOSE_FILES[@]}"; do
  check_file "$f"
done

while IFS= read -r key; do
  load_service "$key" || continue
  [[ "$SVC_REQUIRED" == "yes" ]] || continue
  [[ -n "$SVC_SOURCE" && -n "$SVC_TARGET" ]] || continue
  if [[ -f "$SVC_COMPOSE_ABS" ]] && grep -Fq "$SVC_TARGET" "$SVC_COMPOSE_ABS"; then
    if [[ "$SVC_ALREADY" != "yes" ]]; then
      echo "## Premature target reference: $key" >>"$REPORT_MD"
      echo "- FAIL compose already references target \`$SVC_TARGET\` while migration_required=yes" >>"$REPORT_MD"
      FAIL=$((FAIL + 1))
    fi
  fi
done < <(list_service_keys)

{
  echo "## Summary"
  echo
  echo "- WARN=$WARN"
  echo "- FAIL=$FAIL"
} >>"$REPORT_MD"

info "Wrote $REPORT_MD (WARN=$WARN FAIL=$FAIL)"
echo "-------------------------------------"
echo "Compose path check"
echo "Warnings: $WARN"
echo "Errors:   $FAIL"
echo "Report:   $REPORT_MD"
echo "-------------------------------------"
(( FAIL > 0 )) && exit 1
exit 0
