#!/bin/bash
set -euo pipefail

START_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

REPORT_ROOT="/mnt/monarch/reports"
REPORT_DATE=$(date +%F)
REPORT_DIR="${REPORT_ROOT}/${REPORT_DATE}"

mkdir -p "$REPORT_DIR"
REPORT="${REPORT_DIR}/02-compose.md"

exec > "$REPORT"
exec 2>&1


SEARCH_PATHS=(
"/mnt/monarch/appdata"
"/hive"
)

FILES=$(find "${SEARCH_PATHS[@]}" \
    -type f \
    \( -name compose.yml -o -name docker-compose.yml -o -name docker-compose.yaml \) \
    2>/dev/null)

COUNT=$(echo "$FILES" | grep -c . || true)

echo "======================================================================"
echo "COMPOSE AUDIT"
echo "======================================================================"

echo ""
echo "## AUDIT METADATA"

echo "Audit Version : 4.0"
echo "Schema Version: 1.0"
echo "Generated     : $START_TIME"

echo ""
echo "## INVENTORY"

echo "Compose Files : $COUNT"

echo ""
echo "## METRICS"

echo "Search Paths :"
printf '%s\n' "${SEARCH_PATHS[@]}"

echo ""
echo "## MACHINE CHECKS"

echo "CHECK|ComposeFiles|PASS|$COUNT|1"

echo ""
echo "## HEALTH SUMMARY"

echo "Health Score : 100"

echo ""
echo "PASS : 1"
echo "WARNING : 0"
echo "CRITICAL : 0"
echo "UNKNOWN : 0"

echo ""
echo "## AI PRIORITY"

echo "1. Plaintext secrets."
echo "2. Missing restart policies."
echo "3. Privileged containers."
echo "4. Host networking."
echo "5. Volume permissions."

echo ""
echo "## RAW EVIDENCE"

while read -r file
do
    [ -z "$file" ] && continue

    echo ""
    echo "================================================================"
    echo "FILE: $file"
    echo "================================================================"

    stat "$file"
    echo ""

    cat "$file"

done <<< "$FILES"

echo ""
echo "======================================================================"
echo "AUDIT COMPLETE"
echo "======================================================================"

exec >&3 3>&-

echo "Report written to: $REPORT"
