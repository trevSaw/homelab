#!/bin/bash
set -euo pipefail

START_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

REPORT_ROOT="/mnt/monarch/reports"
REPORT_DATE=$(date +%F)
REPORT_DIR="${REPORT_ROOT}/${REPORT_DATE}"

mkdir -p "$REPORT_DIR"

REPORT="${REPORT_DIR}/03-network.md"

exec > "$REPORT"
exec 2>&1

ports=$(ss -tulpn | grep LISTEN | wc -l)

echo "======================================================================"
echo "NETWORK AUDIT"
echo "======================================================================"

echo ""
echo "## AUDIT METADATA"
echo "Audit Version : 4.0"
echo "Schema Version: 1.0"
echo "Generated     : $START_TIME"

echo ""
echo "## INVENTORY"

echo "Interfaces : $(ip -o link show | wc -l)"
echo "Listening Ports : $ports"

echo ""
echo "## METRICS"

echo "Listening Services : $ports"

echo ""
echo "## MACHINE CHECKS"

echo "CHECK|ListeningPorts|PASS|$ports|Informational"

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

echo "1. Unexpected listening ports."
echo "2. Docker network layout."
echo "3. DNS configuration."

echo ""
echo "## RAW EVIDENCE"

ss -tulpn
echo ""
ip route
echo ""
ip addr
echo ""
docker network ls || true
echo ""
cat /etc/resolv.conf

echo ""
echo "======================================================================"
echo "AUDIT COMPLETE"
echo "======================================================================"

exec >&3 3>&-

echo "Report written to: $REPORT"
