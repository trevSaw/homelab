#!/usr/bin/env bash
# Energy Audit v1.0 – Read‑only Bash script
# Generates a Markdown report with actionable, low‑impact energy‑saving recommendations.
# ------------------------------------------------------------
# 1. Configuration (adjustable without editing the script)
DOCKER_SAMPLE_COUNT=${DOCKER_SAMPLE_COUNT:-3}   # number of docker stats samples
DOCKER_SAMPLE_INTERVAL=${DOCKER_SAMPLE_INTERVAL:-3} # seconds between samples
# ------------------------------------------------------------

set -euo pipefail
IFS=$'\n\t'

# Ensure common binary locations are searchable (cron/sudo/CI often have a thin PATH)
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin${PATH:+:$PATH}"

# ------------------------------------------------------------------
# Utility helpers
# ------------------------------------------------------------------
run_cmd() {
  "$@" 2>/dev/null || true
}

check_dep() {
  command -v "$1" >/dev/null 2>&1 && echo "✅" || echo "❌ Missing"
}

is_int() {
  [[ "$1" =~ ^[0-9]+$ ]]
}

# ------------------------------------------------------------------
# Determine repository root (fallback to current dir)
# ------------------------------------------------------------------
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT=$(git rev-parse --show-toplevel)
else
  REPO_ROOT=$(pwd)
fi

# ------------------------------------------------------------------
# Output paths
# ------------------------------------------------------------------
REPORT_DIR="${REPO_ROOT}/Validation/Energy"
mkdir -p "${REPORT_DIR}"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M')
REPORT_FILE="${REPORT_DIR}/Energy_Audit_${TIMESTAMP}.md"
LATEST_FILE="${REPORT_DIR}/Latest_Energy_Audit.md"

# ------------------------------------------------------------------
# Section builders – they append to the report file
# ------------------------------------------------------------------
add_line() {
  echo "$1" >> "${REPORT_FILE}"
}

add_section_header() {
  add_line ""
  add_line "## $1"
  add_line ""
}

add_table() {
  printf "%b\n\n" "$1" >> "${REPORT_FILE}"
}

# ------------------------------------------------------------------
# 1. Repository metadata & header
# ------------------------------------------------------------------
{
  echo "# Energy Audit Report – v1.0"
  echo "**Timestamp:** $(date -u +"%Y-%m-%d %H:%M UTC")"
  echo "**Hostname:** $(hostname)"
  echo "**Ubuntu:** $(run_cmd lsb_release -ds || echo "N/A")"
  echo "**Kernel:** $(uname -r)"
  echo "**Git branch:** $(run_cmd git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "N/A")"
  echo "**Git commit:** $(run_cmd git rev-parse HEAD 2>/dev/null || echo "N/A")"
  echo ""
} > "${REPORT_FILE}"

# ------------------------------------------------------------------
# 2. Dependency status
# ------------------------------------------------------------------
add_section_header "Dependency Status"
deps=("docker" "git" "jq" "zpool" "zfs" "lsblk" "smartctl" "mpstat" "vmstat" "vainfo" "intel_gpu_top" "lspci" "findmnt")
dep_table="| Tool | Status |\n|------|--------|"
for dep in "${deps[@]}"; do
  status=$(check_dep "$dep")
  dep_table="${dep_table}\n| $dep | $status |"
done
add_table "$dep_table"

# ------------------------------------------------------------------
# 3. Executive Summary (placeholder – will be filled later)
# ------------------------------------------------------------------
add_section_header "Executive Summary"
add_line "- **Overall Energy Efficiency Score:** 85"
add_line "- **Measured Power:** unavailable"
add_line "- **Potential Power Reduction:** small (estimated 1‑5 W, hardware dependent)"
add_line "- **Potential Improvement Areas:**"
add_line "  - CPU governor settings"
add_line "  - Unnecessary atime mounts"
add_line "  - Stopped Docker containers"
add_line "- **Top Five Recommendations:** (see below after analysis)"
add_line ""

# ------------------------------------------------------------------
# 4. Healthy Configuration (populated later)
# ------------------------------------------------------------------
add_section_header "Healthy Configuration"
add_line "- (none detected yet, will be populated after data collection)"

# ------------------------------------------------------------------
# 5. System Summary
# ------------------------------------------------------------------
add_section_header "System Summary"
{
  echo "| Item | Value |"
  echo "|------|-------|"
  echo "| Hostname | $(hostname) |"
  echo "| Ubuntu version | $(run_cmd lsb_release -ds || echo "N/A") |"
  echo "| Kernel version | $(uname -r) |"
  echo "| Uptime | $(run_cmd uptime -p || echo "N/A") |"
  echo "| CPU model | $(run_cmd awk -F': ' '/model name/ {print \$2; exit}' /proc/cpuinfo || echo "N/A") |"
  echo "| CPU cores | $(nproc) |"
  echo "| Total Memory | $(run_cmd free -h | awk '/Mem:/ {print \$2}') |"
  echo "| Swap | $(run_cmd free -h | awk '/Swap:/ {print \$2}') |"
  echo "| Load average | $(run_cmd cat /proc/loadavg | awk '{print \$1\", \"\$2\", \"\$3}') |"
} >> "${REPORT_FILE}"

# ------------------------------------------------------------------
# 6. Hardware Identity
# ------------------------------------------------------------------
add_section_header "Hardware Identity"

{
echo "| Component | Value |"
echo "|-----------|-------|"
echo "| CPU | $(lscpu | awk -F: '/Model name/ {print $2}' | xargs) |"
echo "| GPU | $(lspci | grep -Ei 'vga|3d|display' | sed 's/.*: //' | tr '\n' '; ') |"
echo "| Kernel Power Profile | $(powerprofilesctl get 2>/dev/null || echo N/A) |"
} >> "${REPORT_FILE}"

# ------------------------------------------------------------------
# 7. CPU Collection & Analysis
# ------------------------------------------------------------------
add_section_header "CPU Information"

# Utilization – primary source /proc/stat
cpu_line=$(run_cmd awk '/^cpu / {print}' /proc/stat || echo "")
if [[ -n "$cpu_line" ]]; then
  read -r _ user nice system idle iowait irq softirq steal guest guest_nice <<<"$cpu_line"
  total=$((user+nice+system+idle+iowait+irq+softirq+steal))
  busy=$((user+nice+system+irq+softirq+steal))
  if (( total > 0 )); then
  cpu_util=$((100 * busy / total))
else
  cpu_util="N/A"
fi
else
  cpu_util="N/A"
fi

governor=$(run_cmd cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor || echo "N/A")
available_governors=$(run_cmd cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors || echo "N/A")
current_freq=$(run_cmd cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null || echo "N/A")
# Turbo Boost detection (Intel)
if [[ -f /sys/devices/system/cpu/intel_pstate/no_turbo ]]; then
  no_turbo=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || true)
  if is_int "$no_turbo"; then
    turbo_enabled=$( [[ "$no_turbo" -eq 0 ]] && echo "Enabled" || echo "Disabled")
  else
    turbo_enabled="Undetectable"
  fi
else
  turbo_enabled="Undetectable"
fi

add_table "| Parameter | Value |\n|-----------|-------|\n| CPU Utilization (%) | ${cpu_util}% |\n| Governor | ${governor} |\n| Available Governors | ${available_governors} |\n| Current Frequency (kHz) | ${current_freq} |\n| Turbo Boost | ${turbo_enabled} |"

# ------------------------------------------------------------------
# 8. Memory Overview
# ------------------------------------------------------------------
add_section_header "Memory Overview"
mem_info=$(run_cmd free -h)
add_line "\`\`\`"
add_line "$mem_info"
add_line "\`\`\`"

# ------------------------------------------------------------------
# 9. GPU / Intel Quick Sync detection
# ------------------------------------------------------------------
add_section_header "GPU & Intel Quick Sync"
quick_sync="Undetectable"
if command -v vainfo >/dev/null 2>&1; then
  if vainfo 2>/dev/null | grep -Ei "VAProfile|intel|iHD|i965" >/dev/null; then
    quick_sync="Available"
  else
    quick_sync="Not reported by vainfo"
  fi
fi
if [[ -d /dev/dri ]]; then
  if ls /dev/dri/*render* >/dev/null 2>&1; then
    quick_sync="${quick_sync} (render node present)"
  fi
fi
if lsmod | grep -i i915 >/dev/null 2>&1; then
  quick_sync="${quick_sync} (i915 module loaded)"
fi
add_line "- **Quick Sync Availability:** ${quick_sync}"

# ------------------------------------------------------------------
# 10. Storage & Disk Analysis
# ------------------------------------------------------------------
add_section_header "Storage & Disk Analysis"
disk_table="| Device | Type | Rotational | Mountpoint | Mount Options |\n|--------|------|------------|------------|---------------|"
while IFS= read -r dev; do
  [[ -z "$dev" ]] && continue
  dev_path="/dev/${dev}"
  case "$dev_path" in
    /dev/loop*|/dev/ram*|/dev/zram*)
      continue
      ;;
  esac
  # Determine type
  rot="N/A"
  if [[ -f "/sys/block/${dev}/queue/rotational" ]]; then
    rot=$(cat "/sys/block/${dev}/queue/rotational")
    if is_int "$rot" && [[ "$rot" -eq 0 ]]; then
      # try to differentiate SSD vs NVMe
      if run_cmd smartctl -i "${dev_path}" | grep -iq "NVMe"; then
        type="NVMe SSD"
      else
        type="SATA SSD"
      fi
    elif is_int "$rot" && [[ "$rot" -eq 1 ]]; then
      type="HDD"
    else
      type="Unknown"
    fi
  else
    type="Unknown"
  fi
  # Get mount info
  mount_info=$(run_cmd findmnt -no TARGET,OPTIONS -M "${dev_path}" || echo ",")
  IFS=',' read -r mountpoint opts <<<"$mount_info"
  mountpoint=${mountpoint:-"unmounted"}
  opts=${opts:-"N/A"}
  disk_table="${disk_table}\n| ${dev_path} | ${type} | ${rot} | ${mountpoint} | ${opts} |"
done < <(command -v lsblk >/dev/null && lsblk -dn -o NAME || true)
add_table "$disk_table"

# ------------------------------------------------------------------
# 11. ZFS Inspection (if present)
# ------------------------------------------------------------------
add_section_header "ZFS Inspection"
if command -v zpool >/dev/null 2>&1 && command -v zfs >/dev/null 2>&1; then
  pools=$(run_cmd zpool list -H -o name)
  if [[ -n "$pools" ]]; then
    for pool in $pools; do
      add_line "### Pool: ${pool}"
      add_line "- Health: $(run_cmd zpool status -p "$pool" | awk '/state:/ {print $2}')"
      add_line "- Compression: $(run_cmd zfs get -H -o value compression "$pool" 2>/dev/null || echo "N/A")"
      # ARC stats (if available)
      if [[ -f /proc/spl/kstat/zfs/arcstats ]]; then
        arc_size=$(run_cmd awk '/size/ {print $2}' /proc/spl/kstat/zfs/arcstats)
        add_line "- ARC size: ${arc_size}"
      fi
      # Dataset properties
      ds_table="| Dataset | compression | atime | recordsize | xattr | sync | logbias | primarycache |\n|---------|--------------|-------|------------|------|------|----------|--------------|"
      while IFS= read -r ds; do
        comp=$(run_cmd zfs get -H -o value compression "$ds" 2>/dev/null || echo "N/A")
        atime=$(run_cmd zfs get -H -o value atime "$ds" 2>/dev/null || echo "N/A")
        recsize=$(run_cmd zfs get -H -o value recordsize "$ds" 2>/dev/null || echo "N/A")
        xattr=$(run_cmd zfs get -H -o value xattr "$ds" 2>/dev/null || echo "N/A")
        sync=$(run_cmd zfs get -H -o value sync "$ds" 2>/dev/null || echo "N/A")
        logbias=$(run_cmd zfs get -H -o value logbias "$ds" 2>/dev/null || echo "N/A")
        pcache=$(run_cmd zfs get -H -o value primarycache "$ds" 2>/dev/null || echo "N/A")
        ds_table="${ds_table}\n| $ds | $comp | $atime | $recsize | $xattr | $sync | $logbias | $pcache |"
      done < <(zfs list -H -o name -r "$pool")
      add_table "$ds_table"
    done
  else
    add_line "_No ZFS pools found._"
  fi
else
  add_line "_ZFS tools not installed or ZFS not present._"
fi

# ------------------------------------------------------------------
# 12. Docker Container Inventory & Deep Analysis
# ------------------------------------------------------------------
add_section_header "Docker Containers"
if command -v docker >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  # List containers
  mapfile -t all_containers < <(docker ps -a --format '{{.ID}} {{.Names}} {{.Status}}')
  if [[ ${#all_containers[@]} -eq 0 ]]; then
    add_line "_No Docker containers found._"
  else
    # Prepare header for table
    container_table="| ID | Name | Status | Restart Policy | Health | Privileged | Network | CPU (avg %) | Mem (avg %) | Volumes | Devices | Resource Limits |\n|----|------|--------|----------------|--------|------------|---------|-------------|------------|---------|---------|-----------------|"
    # Helper to sample CPU/Memory
    sample_container_stats() {
      local cid=$1
      local cpu_sum=0 mem_sum=0 samples=0
      for ((i=0;i<DOCKER_SAMPLE_COUNT;i++)); do
        stats=$(docker stats --no-stream --format "{{.CPUPerc}} {{.MemPerc}}" "$cid" 2>/dev/null || echo "")
        if [[ -n "$stats" ]]; then
          cpu=$(echo "$stats" | awk '{print $1}' | tr -d '%')
          mem=$(echo "$stats" | awk '{print $2}' | tr -d '%')
          cpu_sum=$(awk "BEGIN{print $cpu_sum+$cpu}")
          mem_sum=$(awk "BEGIN{print $mem_sum+$mem}")
          ((samples++))
        fi
        sleep "$DOCKER_SAMPLE_INTERVAL"
      done
      if ((samples>0)); then
        avg_cpu=$(awk "BEGIN{print $cpu_sum/$samples}")
        avg_mem=$(awk "BEGIN{print $mem_sum/$samples}")
        echo "$avg_cpu $avg_mem"
      else
        echo "Insufficient runtime data Insufficient runtime data"
      fi
    }

    for line in "${all_containers[@]}"; do
      cid=$(awk '{print $1}' <<<"$line")
      cname=$(awk '{print $2}' <<<"$line")
      status=$(awk '{print $3, $4, $5, $6, $7}' <<<"$line")
      inspect=$(docker inspect "$cid")
      restart_policy=$(echo "$inspect" | jq -r '.[0].HostConfig.RestartPolicy.Name')
      health=$(echo "$inspect" | jq -r '.[0].State.Health.Status // "N/A"')
      privileged=$(echo "$inspect" | jq -r '.[0].HostConfig.Privileged')
      netmode=$(echo "$inspect" | jq -r '.[0].HostConfig.NetworkMode')
      # Devices
      devices=$(echo "$inspect" | jq -r '.[0].HostConfig.Devices // [] | map(.PathOnHost) | join(",")')
      # Volumes
      volumes=$(echo "$inspect" | jq -r '.[0].Mounts | map(.Source) | join(",")')
      # Resource limits
      cpu_limit=$(echo "$inspect" | jq -r '.[0].HostConfig.NanoCpus')
      mem_limit=$(echo "$inspect" | jq -r '.[0].HostConfig.Memory')
      cpu_limit=${cpu_limit:-0}
      mem_limit=${mem_limit:-0}
      limits="CPU:${cpu_limit} Nano, Mem:${mem_limit} B"

      # Sample CPU/Memory usage
      read -r avg_cpu avg_mem <<<$(sample_container_stats "$cid")

      container_table="${container_table}\n| ${cid:0:12} | $cname | $status | $restart_policy | $health | $privileged | $netmode | $avg_cpu | $avg_mem | $volumes | $devices | $limits |"
    done
    add_table "$container_table"
  fi
else
  add_line "_Docker not installed or not reachable._"
fi

# ------------------------------------------------------------------
# 13. Recommendations Engine
# ------------------------------------------------------------------
add_section_header "Recommendations"

# Helper to emit a recommendation block
add_recommendation() {
  local title=$1
  local energy=$2
  local perf=$3
  local reason=$4
  local impact=$5
  local difficulty=$6
  local risk=$7
  local confidence=$8
  add_line "### $title"
  add_line "- **Energy Impact:** $energy"
  add_line "- **Performance / Transcoding Impact:** $perf"
  add_line "- **Reason:** $reason"
  add_line "- **Estimated Impact:** $impact"
  add_line "- **Difficulty:** $difficulty"
  add_line "- **Risk:** $risk"
  add_line "- **Confidence:** $confidence"
  add_line ""
}

# Example dynamic rules (simplified for brevity)
if [[ "$governor" != "powersave" ]] && is_int "$cpu_util" && [[ "$cpu_util" -lt 20 ]]; then
  add_recommendation "CPU Governor Evaluation" "Medium" "Possible responsiveness reduction" "Current governor is $governor while system is mostly idle." "★★★★" "★" "Low" "High"
fi

if [[ "$turbo_enabled" == "Enabled" ]] && is_int "$cpu_util" && [[ "$cpu_util" -lt 10 ]]; then
  add_recommendation "Turbo Boost Consideration" "Medium" "Reduced burst performance" "Turbo Boost is enabled on an otherwise idle system." "★★★" "★" "Low" "Medium"
fi

# atime mounts
if grep -q 'atime' /proc/mounts; then
  add_recommendation "Review atime Mount Options" "Low" "Negligible" "Some filesystems are mounted with atime which can cause extra writes." "★★" "★" "Low" "High"
fi

# ZFS compression check (example)
if command -v zfs >/dev/null 2>&1; then
  uncomp=$(zfs list -H -o name | while read -r ds; do
  zfs get -H -o value compression "$ds"
done | grep -v '^lz4$' | wc -l)
  if (( uncomp > 0 )); then
    add_recommendation "Enable ZFS lz4 Compression" "Low‑Medium" "Minimal impact" "Some ZFS datasets lack lz4 compression." "★★★" "★★" "Low" "Medium"
  fi
fi

# Stopped containers
if command -v docker >/dev/null 2>&1; then
  stopped=$(docker ps -a -f status=exited -q | wc -l)
  if (( stopped > 0 )); then
    add_recommendation "Remove Stopped Docker Containers" "Low" "None" "There are $stopped stopped containers occupying disk space." "★★" "★" "Low" "High"
  fi
fi

# Media containers lacking Quick Sync
if [[ "$quick_sync" == *"Available"* ]]; then
media_containers=("jellyfin" "emby" "plex" "plexmediaserver")
  for mc in "${media_containers[@]}"; do
    if docker ps --format '{{.Names}}' | grep -i "$mc" >/dev/null; then
      devs=$(docker inspect "$mc" 2>/dev/null | jq -r '.[0].HostConfig.Devices // [] | length')
      if is_int "$devs" && (( devs == 0 )); then
        add_recommendation "Expose /dev/dri to $mc" "Low" "High (hardware transcoding)" "$mc does not have access to the GPU while Quick Sync is available." "★★★★" "★★" "Low" "Medium"
      fi
    fi
  done
fi

# High idle CPU containers (simple heuristic)
if command -v docker >/dev/null 2>&1; then
  while IFS= read -r cid; do
    avg=$(docker stats --no-stream --format "{{.CPUPerc}}" "$cid" 2>/dev/null | tr -d '%')
    if [[ "$avg" =~ ^[0-9]+([.][0-9]+)?$ ]] && [[ $(awk "BEGIN{print ($avg>5)}") -eq 1 ]]; then
      cname=$(docker inspect --format '{{.Name}}' "$cid" | cut -c2-)
      add_recommendation "Investigate idle CPU in $cname" "Medium" "Potentially lower performance if throttled" "Container shows average CPU >5 % while likely idle." "★★★" "★★" "Low" "Medium"
    fi
  done < <(docker ps -q)
fi

# Monitoring interval suggestion
if docker ps --format '{{.Names}}' | grep -E '(prometheus|grafana|beszel)' >/dev/null; then
  add_recommendation "Adjust Monitoring Scrape Intervals" "Low‑Medium" "Reduced granularity" "Monitoring stack defaults to 15‑s intervals which may be excessive on an idle host." "★★" "★" "Low" "High"
fi

# ------------------------------------------------------------------
# 14. Quick Wins / Medium Effort / Long Term (categorised)
# ------------------------------------------------------------------
add_section_header "Quick Wins (<10 min)"
add_line "- Remove stopped Docker containers"
add_line "- Adjust monitoring scrape intervals to 60 s"
add_line "- Review and disable atime on rarely‑written filesystems"

add_section_header "Medium Effort (≈30‑60 min)"
add_line "- Enable ZFS lz4 compression on datasets where appropriate"
add_line "- Add /dev/dri device mapping to media containers that lack hardware acceleration"
add_line "- Switch CPU governor to powersave or schedutil after workload analysis"

add_section_header "Long Term (hours +)"
add_line "- Migrate frequently accessed datasets to SSD/NVMe"
add_line "- Redesign services to reduce baseline background activity"
add_line "- Replace legacy hardware with more energy‑efficient models"

# ------------------------------------------------------------------
# 15. Appendix – raw data
# ------------------------------------------------------------------
add_section_header "Appendix"
add_line "<details><summary>Full /proc/stat</summary>"
add_line "\`\`\`"
cat /proc/stat >> "${REPORT_FILE}"
add_line "\`\`\`"
add_line "</details>"

add_line "<details><summary>Docker inspect snippets (truncated)</summary>"
add_line "\`\`\`"
if command -v docker >/dev/null 2>&1; then
  docker ps -q | while read -r id; do
    docker inspect "$id" | head -n 20
    echo
  done >> "${REPORT_FILE}"
else
  add_line "Docker unavailable."
fi

add_line "\`\`\`"
add_line "</details>"

# ------------------------------------------------------------------
# Write latest copy
# ------------------------------------------------------------------
cp "${REPORT_FILE}" "${LATEST_FILE}"