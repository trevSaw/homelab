#!/bin/bash
set -euo pipefail

echo "===== NETWORK AUDIT ====="
echo "Timestamp: $(date)"
echo ""

echo "## LISTENING PORTS"
ss -tulpn 2>/dev/null | head -n 50 || netstat -tulpn 2>/dev/null || echo "No network tools available"
echo ""

echo "## ROUTING TABLE"
ip route 2>/dev/null || route -n 2>/dev/null || echo "No routing info"
echo ""

echo "## INTERFACES"
ip a 2>/dev/null || ifconfig 2>/dev/null || echo "No interface info"
echo ""

echo "## DOCKER NETWORKS"
docker network ls 2>/dev/null || echo "Docker unavailable"
echo ""

echo "## DNS CONFIG"
cat /etc/resolv.conf 2>/dev/null || echo "No resolv.conf"
echo ""
