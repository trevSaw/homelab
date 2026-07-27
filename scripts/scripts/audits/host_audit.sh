#!/usr/bin/env bash
set -uo pipefail

###############################################################################
# HOST AUDIT
# Version: 4.0
# Schema: 1.0
###############################################################################

AUDIT_NAME="Host"
AUDIT_VERSION="4.0"
SCHEMA_VERSION="1.0"

START_EPOCH=$(date +%s)
START_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

REPORT_ROOT="/mnt/monarch/reports"
REPORT_DATE=$(date +%F)
REPORT_DIR="${REPORT_ROOT}/${REPORT_DATE}"

mkdir -p "$REPORT_DIR"

REPORT="${REPORT_DIR}/01-host.md"

exec > "$REPORT"
exec 2>&1

###############################################################################
# Helper Functions
###############################################################################

safe_cmd() {
    "$@" 2>/dev/null || true
}

exists() {
    command -v "$1" >/dev/null 2>&1
}

###############################################################################
# Inventory
###############################################################################

HOSTNAME=$(hostname)

OS=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"' || echo "Unknown")

KERNEL=$(uname -r)

if exists lscpu; then
    CPU_MODEL=$(lscpu | awk -F: '/Model name/ {gsub(/^[ \t]+/,"",$2);print $2;exit}')
else
    CPU_MODEL="Unknown"
fi

CPU_THREADS=$(nproc 2>/dev/null || echo "?")

MEMORY_TOTAL=$(free -h | awk '/Mem:/ {print $2}')

if exists nvidia-smi; then
    GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | paste -sd "," -)
else
    GPU="None Detected"
fi

FILESYSTEMS=$(df -T 2>/dev/null | awk 'NR>1{print $2}' | sort -u | paste -sd "," -)

docker_running="Not Installed"
if exists docker; then
    docker_running="Installed"
    if systemctl is-active docker >/dev/null 2>&1; then
        docker_running="Running"
    fi
fi

ollama_status="Not Installed"
exists ollama && ollama_status="Installed"

n8n_status="Not Running"
pgrep -f n8n >/dev/null 2>&1 && n8n_status="Running"

###############################################################################
# Metrics
###############################################################################

LOAD_AVG=$(cut -d' ' -f1-3 /proc/loadavg)

MEM_USED=$(free -h | awk '/Mem:/ {print $3}')
MEM_AVAIL=$(free -h | awk '/Mem:/ {print $7}')

SWAP_USED=$(free -h | awk '/Swap:/ {print $3}')
SWAP_TOTAL=$(free -h | awk '/Swap:/ {print $2}')

ROOT_USE=$(df / | awk 'NR==2 {gsub("%","",$5);print $5}')

HIVE_USE=$(df /hive 2>/dev/null | awk 'NR==2 {gsub("%","",$5);print $5}')
[ -z "$HIVE_USE" ] && HIVE_USE=0

FAILED_SERVICES=$(systemctl --failed --no-legend 2>/dev/null | wc -l)

TOP_CPU=$(ps -eo cmd,%cpu --sort=-%cpu | sed -n '2p')
TOP_MEM=$(ps -eo cmd,%mem --sort=-%mem | sed -n '2p')

###############################################################################
# Health Checks
###############################################################################

PASS=0
WARNING=0
CRITICAL=0
UNKNOWN=0

ROOT_STATUS="PASS"
((ROOT_USE>=90)) && ROOT_STATUS="CRITICAL"
((ROOT_USE>=80 && ROOT_USE<90)) && ROOT_STATUS="WARNING"

HIVE_STATUS="PASS"
((HIVE_USE>=90)) && HIVE_STATUS="CRITICAL"
((HIVE_USE>=80 && HIVE_USE<90)) && HIVE_STATUS="WARNING"

SWAP_PERCENT=$(free | awk '/Swap:/ {if($2==0){print 0}else{print int(($3/$2)*100)}}')

SWAP_STATUS="PASS"
((SWAP_PERCENT>=80)) && SWAP_STATUS="CRITICAL"
((SWAP_PERCENT>=50 && SWAP_PERCENT<80)) && SWAP_STATUS="WARNING"

FAILED_STATUS="PASS"
((FAILED_SERVICES>0)) && FAILED_STATUS="WARNING"

for STATE in "$ROOT_STATUS" "$HIVE_STATUS" "$SWAP_STATUS" "$FAILED_STATUS"
do
    case "$STATE" in
        PASS) ((PASS++));;
        WARNING) ((WARNING++));;
        CRITICAL) ((CRITICAL++));;
        *) ((UNKNOWN++));;
    esac
done

HEALTH_SCORE=$((100-(WARNING*5)-(CRITICAL*20)))

###############################################################################
# Output
###############################################################################

echo "======================================================================"
echo "HOST AUDIT"
echo "======================================================================"
echo

echo "## AUDIT METADATA"
echo "Audit Name      : $AUDIT_NAME"
echo "Audit Version   : $AUDIT_VERSION"
echo "Schema Version  : $SCHEMA_VERSION"
echo "Generated       : $START_TIME"
echo

echo "## INVENTORY"
echo "Hostname        : $HOSTNAME"
echo "Operating System: $OS"
echo "Kernel          : $KERNEL"
echo "CPU             : $CPU_MODEL"
echo "CPU Threads     : $CPU_THREADS"
echo "Memory          : $MEMORY_TOTAL"
echo "GPU             : $GPU"
echo "Filesystems     : $FILESYSTEMS"
echo "Docker          : $docker_running"
echo "Ollama          : $ollama_status"
echo "n8n             : $n8n_status"
echo

echo "## METRICS"
echo "Load Average      : $LOAD_AVG"
echo "Memory Used       : $MEM_USED"
echo "Memory Available  : $MEM_AVAIL"
echo "Swap Used         : $SWAP_USED / $SWAP_TOTAL"
echo "Root Usage        : ${ROOT_USE}%"
echo "Hive Usage        : ${HIVE_USE}%"
echo "Failed Services   : $FAILED_SERVICES"
echo "Top CPU Process   : $TOP_CPU"
echo "Top Memory Process: $TOP_MEM"
echo

echo "## MACHINE CHECKS"
echo "CHECK|RootFilesystem|$ROOT_STATUS|$ROOT_USE|80"
echo "CHECK|HiveStorage|$HIVE_STATUS|$HIVE_USE|80"
echo "CHECK|SwapUsage|$SWAP_STATUS|$SWAP_PERCENT|50"
echo "CHECK|FailedServices|$FAILED_STATUS|$FAILED_SERVICES|0"
echo "CHECK|LoadAverage|PASS|$LOAD_AVG|$CPU_THREADS Threads"
echo

echo "## HEALTH SUMMARY"
echo "Health Score : $HEALTH_SCORE"
echo
echo "PASS      : $PASS"
echo "WARNING   : $WARNING"
echo "CRITICAL  : $CRITICAL"
echo "UNKNOWN   : $UNKNOWN"
echo

echo "## AI PRIORITY"

if [ "$FAILED_STATUS" != "PASS" ]; then
    echo "1. Review failed systemd services."
fi

echo "2. Review highest CPU utilization."
echo "3. Verify storage utilization trends."
echo

echo "## RAW EVIDENCE"

echo
echo "### SYSTEM"
safe_cmd hostnamectl

echo
echo "### UPTIME"
safe_cmd uptime

echo
echo "### KERNEL"
safe_cmd uname -a

echo
echo "### LOAD"
cat /proc/loadavg

echo
echo "### MEMORY"
safe_cmd free -h

echo
echo "### DISK"
safe_cmd df -hT

echo
echo "### INODES"
safe_cmd df -i

echo
echo "### FAILED SERVICES"
safe_cmd systemctl --failed --no-pager

echo
echo "### TOP CPU"
safe_cmd ps -eo pid,user,cmd,%cpu,%mem --sort=-%cpu | head -15

echo
echo "### TOP MEMORY"
safe_cmd ps -eo pid,user,cmd,%cpu,%mem --sort=-%mem | head -15

END_EPOCH=$(date +%s)
END_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
RUNTIME=$((END_EPOCH-START_EPOCH))

echo
echo "======================================================================"
echo "AUDIT COMPLETE"
echo "======================================================================"
echo
echo "Audit Version : $AUDIT_VERSION"
echo "Schema Version: $SCHEMA_VERSION"
echo "Health Score  : $HEALTH_SCORE"
echo "Started       : $START_TIME"
echo "Finished      : $END_TIME"
echo "Runtime       : ${RUNTIME}s"

exit 0

exec >&3 3>&-

echo "Report written to: $REPORT"
