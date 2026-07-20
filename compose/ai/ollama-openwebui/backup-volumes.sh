#!/usr/bin/env bash
# Backup key volumes for the Open WebUI stack (before image upgrades / DB changes).
# Usage: run from the directory containing your compose file, or use -f.
#
#   ./backup-volumes.sh                    # backup to ./backups/
#   ./backup-volumes.sh -f compose.yml     # use specific compose file
#   ./backup-volumes.sh --stop             # stop stack, backup, then start (consistent DB)
#   BACKUP_DIR=/mnt/backups ./backup-volumes.sh
#
set -euo pipefail

COMPOSE_FILE=""
STOP_STACK=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -f|--file)
      COMPOSE_FILE="$2"
      shift 2
      ;;
    --stop)
      STOP_STACK=true
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# Default compose file: same dir as this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-${SCRIPT_DIR}/compose.yaml}"
if [[ ! -f "$COMPOSE_FILE" ]]; then
  COMPOSE_FILE="${COMPOSE_FILE%/*}/compose.yml"
fi
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Compose file not found. Use -f /path/to/compose.yaml" >&2
  exit 1
fi

COMPOSE_DIR="$(cd "$(dirname "$COMPOSE_FILE")" && pwd)"
COMPOSE_FILE="$COMPOSE_DIR/$(basename "$COMPOSE_FILE")"

# Project name = COMPOSE_PROJECT_NAME env, or directory name (Compose default)
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-$(basename "$COMPOSE_DIR")}"
BACKUP_ROOT="${BACKUP_DIR:-$COMPOSE_DIR/backups}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_PATH="$BACKUP_ROOT/backup-${PROJECT_NAME}-${TIMESTAMP}"

# Key volumes to backup (names as in compose 'volumes:' section). Ollama/models excluded (can re-pull).
VOLUMES=(open-webui llm_postgres-data redis-data)

echo "Compose: $COMPOSE_FILE"
echo "Project: $PROJECT_NAME"
echo "Backup:  $BACKUP_PATH"
echo ""

if [[ "$STOP_STACK" == true ]]; then
  echo "Stopping stack for consistent backup..."
  (cd "$COMPOSE_DIR" && docker compose -f "$COMPOSE_FILE" down)
fi

mkdir -p "$BACKUP_PATH"
cd "$BACKUP_PATH"

for vol in "${VOLUMES[@]}"; do
  full_name="${PROJECT_NAME}_${vol}"
  if ! docker volume inspect "$full_name" &>/dev/null; then
    echo "Skip (volume not found): $full_name"
    continue
  fi
  echo "Backing up $full_name ..."
  docker run --rm \
    -v "$full_name:/data:ro" \
    -v "$(pwd):/backup" \
    alpine \
    tar czf "/backup/${vol}.tar.gz" -C /data .
  echo "  -> ${vol}.tar.gz"
done

if [[ "$STOP_STACK" == true ]]; then
  echo ""
  echo "Starting stack..."
  (cd "$COMPOSE_DIR" && docker compose -f "$COMPOSE_FILE" up -d)
fi

echo ""
echo "Done. Backups in: $BACKUP_PATH"
echo "To restore a volume: docker run --rm -v VOLUME_NAME:/data -v $BACKUP_PATH:/backup alpine sh -c 'cd /data && tar xzf /backup/VOLUME_NAME.tar.gz'"
