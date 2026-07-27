#!/bin/bash
set -euo pipefail

echo "===== DOCKER AUDIT ====="
echo "Timestamp: $(date)"
echo ""

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not installed"
  exit 0
fi

echo "## DOCKER VERSION"
docker version --format '{{.Server.Version}}' 2>/dev/null || docker --version
echo ""

echo "## RUNNING CONTAINERS"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "## CONTAINER RESOURCE USAGE"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

echo "## UNUSED VOLUMES (potential orphaned data)"
docker volume ls -qf dangling=true || true
echo ""

echo "## NETWORKS"
docker network ls
echo ""

echo "## IMAGE USAGE (top 10 largest)"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -n 10
echo ""
