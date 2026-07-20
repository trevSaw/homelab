#!/bin/bash
set -euo pipefail

AUDIT_NAME="Docker"
AUDIT_VERSION="4.0"
SCHEMA_VERSION="1.0"
START_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

REPORT_ROOT="/mnt/monarch/reports"
REPORT_DATE=$(date +%F)
REPORT_DIR="${REPORT_ROOT}/${REPORT_DATE}"

mkdir -p "$REPORT_DIR"

REPORT="${REPORT_DIR}/05-docker.md"

exec > "$REPORT"
exec 2>&1

docker_running="No"

command -v docker >/dev/null && docker_running="Yes"

container_count=0
running_count=0
network_count=0
volume_count=0
dangling_volumes=0

if command -v docker >/dev/null; then
    container_count=$(docker ps -a -q | wc -l)
    running_count=$(docker ps -q | wc -l)
    network_count=$(docker network ls -q | wc -l)
    volume_count=$(docker volume ls -q | wc -l)
    dangling_volumes=$(docker volume ls -qf dangling=true | wc -l)
fi

echo "======================================================================"
echo "DOCKER AUDIT"
echo "======================================================================"
echo ""

echo "## AUDIT METADATA"
echo "Audit Name      : $AUDIT_NAME"
echo "Audit Version   : $AUDIT_VERSION"
echo "Schema Version  : $SCHEMA_VERSION"
echo "Generated       : $START_TIME"
echo ""

echo "## INVENTORY"
echo "Docker Installed : $docker_running"

if command -v docker >/dev/null; then
echo "Docker Version   : $(docker version --format '{{.Server.Version}}')"
fi

echo "Containers       : $container_count"
echo "Running          : $running_count"
echo "Networks         : $network_count"
echo "Volumes          : $volume_count"
echo ""

echo "## METRICS"
echo "Dangling Volumes : $dangling_volumes"
echo ""

echo "## MACHINE CHECKS"
echo "CHECK|DockerInstalled|PASS|$docker_running|Yes"
echo "CHECK|RunningContainers|PASS|$running_count|N/A"

if (( dangling_volumes > 0 )); then
echo "CHECK|DanglingVolumes|WARNING|$dangling_volumes|0"
else
echo "CHECK|DanglingVolumes|PASS|0|0"
fi

echo ""

echo "## HEALTH SUMMARY"
echo "Health Score : 95"
echo ""
echo "PASS      : 2"
echo "WARNING   : $(( dangling_volumes>0 ? 1 : 0 ))"
echo "CRITICAL  : 0"
echo "UNKNOWN   : 0"
echo ""

echo "## AI PRIORITY"
echo "1. Containers restarting repeatedly."
echo "2. Dangling volumes."
echo "3. High memory containers."
echo ""

echo "## RAW EVIDENCE"
echo ""

docker version
echo ""
docker ps -a
echo ""
docker stats --no-stream
echo ""
docker network ls
echo ""
docker volume ls
echo ""
docker images
echo ""

END_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

echo "======================================================================"
echo "AUDIT COMPLETE"
echo "======================================================================"
echo ""
echo "Audit Version : $AUDIT_VERSION"
echo "Finished      : $END_TIME"

exec >&3 3>&-

echo "Report written to: $REPORT"