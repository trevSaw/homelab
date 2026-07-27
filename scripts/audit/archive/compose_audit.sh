#!/bin/bash
set -euo pipefail

echo "===== COMPOSE AUDIT ====="
echo "Timestamp: $(date)"
echo "PATH: $file"
echo "SIZE: $(wc -c < "$file") bytes"
echo "LAST MODIFIED: $(stat -c %y "$file" 2>/dev/null || stat -f %Sm "$file")"
echo ""

SEARCH_PATHS=(
  "/mnt/monarch/appdata"
  "/hive"
)

echo "## SEARCH PATHS"
printf '%s\n' "${SEARCH_PATHS[@]}"
echo ""

for BASE_DIR in "${SEARCH_PATHS[@]}"; do

  if [ ! -d "$BASE_DIR" ]; then
    echo "SKIP (missing): $BASE_DIR"
    echo ""
    continue
  fi

  echo "=============================="
  echo "BASE: $BASE_DIR"
  echo "=============================="
  echo ""

  # Find compose files safely (limit depth to avoid junk dirs)
  find "$BASE_DIR" -maxdepth 5 -type f \( \
    -name "compose.yml" -o \
    -name "docker-compose.yml" -o \
    -name "docker-compose.yaml" \
  \) 2>/dev/null | while read -r file; do

    echo "----- FILE -----"
    echo "$file"
    echo ""

    # Prevent massive outputs from huge compose files
    # Only first 150 lines (enough for audit patterns)
    head -n 150 "$file"
    echo ""

  done

done
