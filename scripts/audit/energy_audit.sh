#!/usr/bin/env bash
# Energy Audit v1.1 – Read-only Bash script
# Generates a Markdown report with actionable, low-impact energy-saving recommendations.
# ------------------------------------------------------------
# 1. Configuration (adjustable without editing the script)
DOCKER_SAMPLE_COUNT=${DOCKER_SAMPLE_COUNT:-3}      # number of docker stats samples
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

is_num() {
  [[ "$1" =~ ^[0-9]+([.][0-9]+)?$ ]]
}

# Convert raw bytes (integer) to human-readable KiB/MiB/GiB
human_bytes() {
  local bytes="${1:-0}"
  if ! is_int "$bytes"; then
    echo "N/A"
    return
  fi
  if (( bytes == 0 )); then
    echo "unlimited/none"
    return
  fi
  awk -v b="$bytes" 'BEGIN {
    if (b >= 1073741824) printf "%.1f GiB", b/1073741824
    else if (b >= 1048576) printf "%.1f MiB", b/1048576
    else if (b >= 1024) printf "%.1f KiB", b/1024
    else printf "%d B", b
  }'
}

format_pct() {
  local v="${1:-}"
  if ! is_num "$v"; then
    echo "N/A"
    return
  fi
  awk -v n="$v" 'BEGIN { printf "%.1f", n }'
}

# Space-safe field read (global IFS excludes space)
read_fields() {
  local __ifs=$IFS
  IFS=$' \t'
  # shellcheck disable=SC2162
  read -r "$@"
  local __rc=$?
  IFS=$__ifs
  return $__rc
}

# ------------------------------------------------------------------
# CPU utilization: mpstat → /proc/stat delta → top -bn1
# ------------------------------------------------------------------
get_cpu_util() {
  local util=""

  if command -v mpstat >/dev/null 2>&1; then
    util=$(mpstat 1 1 2>/dev/null | awk '/Average:/ && $2 ~ /[Aa][Ll][Ll]/ { printf "%.0f", 100 - $NF; exit }')
    if is_num "$util"; then
      echo "$util"
      return
    fi
  fi

  # /proc/stat delta over 1s (current utilization, not lifetime average)
  local line1 line2
  line1=$(awk '/^cpu / {print; exit}' /proc/stat 2>/dev/null || true)
  sleep 1
  line2=$(awk '/^cpu / {print; exit}' /proc/stat 2>/dev/null || true)
  if [[ -n "$line1" && -n "$line2" ]]; then
    local _u1 n1 s1 i1 io1 irq1 soft1 st1
    local _u2 n2 s2 i2 io2 irq2 soft2 st2
    read_fields _ _u1 n1 s1 i1 io1 irq1 soft1 st1 _ _ <<<"$line1"
    read_fields _ _u2 n2 s2 i2 io2 irq2 soft2 st2 _ _ <<<"$line2"
    if is_int "${_u1:-}" && is_int "${_u2:-}"; then
      local idle1 idle2 total1 total2 busy_d total_d
      idle1=$((i1 + io1))
      idle2=$((i2 + io2))
      total1=$((_u1 + n1 + s1 + i1 + io1 + irq1 + soft1 + st1))
      total2=$((_u2 + n2 + s2 + i2 + io2 + irq2 + soft2 + st2))
      busy_d=$(( (total2 - idle2) - (total1 - idle1) ))
      total_d=$(( total2 - total1 ))
      if (( total_d > 0 )); then
        util=$(( 100 * busy_d / total_d ))
        echo "$util"
        return
      fi
    fi
  fi

  if command -v top >/dev/null 2>&1; then
    util=$(top -bn1 2>/dev/null | awk -F'[, ]+' '/Cpu\(s\)|%Cpu/ {
      for (i=1;i<=NF;i++) if ($i ~ /id/) { gsub(/[^0-9.]/,"",$(i-1)); printf "%.0f", 100-$(i-1); exit }
    }')
    if is_num "$util"; then
      echo "$util"
      return
    fi
  fi

  echo "N/A"
}

has_atime_mounts() {
  awk '{
    opts=$4
    if ((opts ~ /(^|,)atime(,|$)/ || opts ~ /(^|,)strictatime(,|$)/) && opts !~ /noatime/) found=1
  } END { exit !found }' /proc/mounts 2>/dev/null
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

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
BODY_FILE="${TMP_DIR}/body.md"
HEALTHY_FILE="${TMP_DIR}/healthy.txt"
IMPROVE_FILE="${TMP_DIR}/improve.txt"
REC_TITLES_FILE="${TMP_DIR}/rec_titles.txt"
DOCKER_STATS_FILE="${TMP_DIR}/docker_stats.tsv"
: > "$BODY_FILE"
: > "$HEALTHY_FILE"
: > "$IMPROVE_FILE"
: > "$REC_TITLES_FILE"
: > "$DOCKER_STATS_FILE"

add_line() {
  echo "$1" >> "${BODY_FILE}"
}

add_section_header() {
  add_line ""
  add_line "## $1"
  add_line ""
}

add_table() {
  printf "%b\n\n" "$1" >> "${BODY_FILE}"
}

note_healthy() {
  echo "$1" >> "$HEALTHY_FILE"
}

note_improve() {
  echo "$1" >> "$IMPROVE_FILE"
}

note_rec_title() {
  echo "$1" >> "$REC_TITLES_FILE"
}

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
  note_rec_title "$title"
}

# ------------------------------------------------------------------
# Dependency Status
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
# System Summary
# ------------------------------------------------------------------
add_section_header "System Summary"
{
  echo "| Item | Value |"
  echo "|------|-------|"
  echo "| Hostname | $(hostname) |"
  echo "| Ubuntu version | $(run_cmd lsb_release -ds || echo "N/A") |"
  echo "| Kernel version | $(uname -r) |"
  echo "| Uptime | $(run_cmd uptime -p || echo "N/A") |"
  echo "| CPU model | $(run_cmd awk -F': ' '/model name/ {print $2; exit}' /proc/cpuinfo || echo "N/A") |"
  echo "| CPU cores | $(nproc) |"
  echo "| Total Memory | $(run_cmd free -h | awk '/Mem:/ {print $2}') |"
  echo "| Swap | $(run_cmd free -h | awk '/Swap:/ {print $2}') |"
  echo "| Load average | $(run_cmd cat /proc/loadavg | awk '{print $1", "$2", "$3}') |"
} >> "${BODY_FILE}"

# ------------------------------------------------------------------
# Hardware Identity
# ------------------------------------------------------------------
add_section_header "Hardware Identity"
power_profile=$(powerprofilesctl get 2>/dev/null || echo "N/A")
{
  echo "| Component | Value |"
  echo "|-----------|-------|"
  echo "| CPU | $(lscpu 2>/dev/null | awk -F: '/Model name/ {print $2}' | xargs) |"
  echo "| GPU | $(lspci 2>/dev/null | grep -Ei 'vga|3d|display' | sed 's/.*: //' | tr '\n' '; ') |"
  echo "| Kernel Power Profile | ${power_profile} |"
} >> "${BODY_FILE}"

if [[ "$power_profile" == "balanced" || "$power_profile" == "power-saver" ]]; then
  note_healthy "Kernel power profile is ${power_profile}"
fi

# ------------------------------------------------------------------
# CPU Collection & Analysis
# ------------------------------------------------------------------
add_section_header "CPU Information"

cpu_util=$(get_cpu_util)

governor=$(run_cmd cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor || echo "N/A")
available_governors=$(run_cmd cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors || echo "N/A")
current_freq=$(run_cmd cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null || echo "N/A")

turbo_enabled="Undetectable"
if [[ -f /sys/devices/system/cpu/intel_pstate/no_turbo ]]; then
  no_turbo=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || true)
  if is_int "$no_turbo"; then
    if [[ "$no_turbo" -eq 0 ]]; then
      turbo_enabled="Enabled"
    else
      turbo_enabled="Disabled"
    fi
  fi
fi

cpu_display="$cpu_util"
if is_num "$cpu_util"; then
  cpu_display=$(format_pct "$cpu_util")
fi

add_table "| Parameter | Value |\n|-----------|-------|\n| CPU Utilization (%) | ${cpu_display} |\n| Governor | ${governor} |\n| Available Governors | ${available_governors} |\n| Current Frequency (kHz) | ${current_freq} |\n| Turbo Boost | ${turbo_enabled} |"

if [[ "$governor" == "powersave" || "$governor" == "schedutil" ]]; then
  note_healthy "CPU governor is ${governor}"
else
  note_improve "CPU governor settings (${governor})"
fi

if [[ "$turbo_enabled" == "Disabled" ]]; then
  note_healthy "Turbo Boost is disabled"
fi

# ------------------------------------------------------------------
# Memory Overview
# ------------------------------------------------------------------
add_section_header "Memory Overview"
mem_info=$(run_cmd free -h)
add_line "\`\`\`"
add_line "$mem_info"
add_line "\`\`\`"

# ------------------------------------------------------------------
# GPU / Intel Quick Sync detection
# ------------------------------------------------------------------
add_section_header "GPU & Intel Quick Sync"

render_node="not detected"
vainfo_state="not installed"
qs_conclusion="Hardware transcoding unavailable"
qs_level="unavailable"

if [[ -d /dev/dri ]] && ls /dev/dri/renderD* >/dev/null 2>&1; then
  render_node="detected"
  qs_level="likely"
  qs_conclusion="Hardware transcoding likely available"
fi

if command -v vainfo >/dev/null 2>&1; then
  vainfo_state="installed"
  if vainfo 2>/dev/null | grep -Ei 'VAProfile|iHD|i965|Intel' >/dev/null; then
    qs_level="confirmed"
    qs_conclusion="Hardware transcoding confirmed"
  elif [[ "$render_node" == "detected" ]]; then
    qs_conclusion="Hardware transcoding likely available (vainfo present but no Intel VA profiles reported)"
  else
    qs_level="unavailable"
    qs_conclusion="Hardware transcoding unavailable (vainfo installed, no usable profiles)"
  fi
fi

i915_loaded="no"
if lsmod 2>/dev/null | grep -qi '^i915'; then
  i915_loaded="yes"
fi

add_line "- **Render node:** ${render_node}"
add_line "- **vainfo:** ${vainfo_state}"
add_line "- **i915 module:** ${i915_loaded}"
add_line "- **Quick Sync / HW transcoding:** ${qs_conclusion}"

if [[ "$qs_level" == "confirmed" ]]; then
  note_healthy "Intel Quick Sync / HW transcoding confirmed"
elif [[ "$qs_level" == "likely" ]]; then
  note_healthy "GPU render node detected (HW transcoding likely available)"
  if [[ "$vainfo_state" == "not installed" ]]; then
    note_improve "Install vainfo to confirm Quick Sync"
  fi
fi

# ------------------------------------------------------------------
# Storage & Disk Analysis
# ------------------------------------------------------------------
add_section_header "Storage & Disk Analysis"
disk_table="| Device | Type | Rotational | Mountpoint | Mount Options |\n|--------|------|------------|------------|---------------|"
ssd_found=0
while IFS= read -r dev; do
  [[ -z "$dev" ]] && continue
  dev_path="/dev/${dev}"
  case "$dev_path" in
    /dev/loop*|/dev/ram*|/dev/zram*)
      continue
      ;;
  esac
  rot="N/A"
  type="Unknown"
  if [[ -f "/sys/block/${dev}/queue/rotational" ]]; then
    rot=$(cat "/sys/block/${dev}/queue/rotational")
    if is_int "$rot" && [[ "$rot" -eq 0 ]]; then
      if run_cmd smartctl -i "${dev_path}" | grep -iq "NVMe"; then
        type="NVMe SSD"
      else
        type="SATA SSD"
      fi
      ssd_found=1
    elif is_int "$rot" && [[ "$rot" -eq 1 ]]; then
      type="HDD"
    fi
  fi
  mount_info=$(run_cmd findmnt -no TARGET,OPTIONS -S "${dev_path}" || run_cmd findmnt -no TARGET,OPTIONS -M "${dev_path}" || echo "")
  mountpoint=$(awk '{print $1}' <<<"${mount_info:-}")
  opts=$(awk '{print $2}' <<<"${mount_info:-}")
  mountpoint=${mountpoint:-"unmounted"}
  opts=${opts:-"N/A"}
  disk_table="${disk_table}\n| ${dev_path} | ${type} | ${rot} | ${mountpoint} | ${opts} |"
done < <(command -v lsblk >/dev/null && lsblk -dn -o NAME || true)
add_table "$disk_table"

if (( ssd_found > 0 )); then
  note_healthy "SSD/NVMe storage present"
fi

# ------------------------------------------------------------------
# ZFS Inspection
# ------------------------------------------------------------------
add_section_header "ZFS Inspection"
zfs_present=0
zfs_lz4_ok=0
zfs_atime_off=0
arc_human="N/A"

if command -v zpool >/dev/null 2>&1 && command -v zfs >/dev/null 2>&1; then
  pools=$(run_cmd zpool list -H -o name)
  if [[ -n "$pools" ]]; then
    zfs_present=1
    if [[ -f /proc/spl/kstat/zfs/arcstats ]]; then
      arc_bytes=$(awk '$1 == "size" { print $3; exit }' /proc/spl/kstat/zfs/arcstats 2>/dev/null || true)
      if ! is_int "${arc_bytes:-}"; then
        arc_bytes=$(awk '$1 == "size" { print $2; exit }' /proc/spl/kstat/zfs/arcstats 2>/dev/null || true)
      fi
      if is_int "${arc_bytes:-}"; then
        arc_human=$(human_bytes "$arc_bytes")
      fi
    fi
    add_line "- **ARC Size:** ${arc_human}"
    add_line ""

    for pool in $pools; do
      pool_health=$(run_cmd zpool status "$pool" | awk '/state:/ {print $2; exit}')
      pool_comp=$(run_cmd zfs get -H -o value compression "$pool" 2>/dev/null || echo "N/A")
      add_line "### Pool: ${pool}"
      add_line "- Health: ${pool_health:-N/A}"
      add_line "- Compression: ${pool_comp}"
      if [[ "$pool_health" == "ONLINE" ]]; then
        note_healthy "ZFS pool ${pool} is ONLINE"
      fi
      if [[ "$pool_comp" == "lz4" || "$pool_comp" == "on" ]]; then
        zfs_lz4_ok=1
      fi

      ds_table="| Dataset | compression | atime | recordsize | xattr | sync | logbias | primarycache |\n|---------|--------------|-------|------------|------|------|----------|--------------|"
      while IFS= read -r ds; do
        [[ -z "$ds" ]] && continue
        comp=$(run_cmd zfs get -H -o value compression "$ds" 2>/dev/null || echo "N/A")
        atime=$(run_cmd zfs get -H -o value atime "$ds" 2>/dev/null || echo "N/A")
        recsize=$(run_cmd zfs get -H -o value recordsize "$ds" 2>/dev/null || echo "N/A")
        xattr=$(run_cmd zfs get -H -o value xattr "$ds" 2>/dev/null || echo "N/A")
        sync=$(run_cmd zfs get -H -o value sync "$ds" 2>/dev/null || echo "N/A")
        logbias=$(run_cmd zfs get -H -o value logbias "$ds" 2>/dev/null || echo "N/A")
        pcache=$(run_cmd zfs get -H -o value primarycache "$ds" 2>/dev/null || echo "N/A")
        ds_table="${ds_table}\n| $ds | $comp | $atime | $recsize | $xattr | $sync | $logbias | $pcache |"
        if [[ "$comp" == "lz4" || "$comp" == "on" ]]; then
          zfs_lz4_ok=1
        fi
        if [[ "$atime" == "off" ]]; then
          zfs_atime_off=1
        fi
      done < <(zfs list -H -o name -r "$pool" 2>/dev/null || true)
      add_table "$ds_table"
    done

    if (( zfs_lz4_ok > 0 )); then
      note_healthy "ZFS compression=lz4 (or on) detected"
    else
      note_improve "ZFS compression not set to lz4 on some datasets"
    fi
    if (( zfs_atime_off > 0 )); then
      note_healthy "ZFS atime=off on one or more datasets"
    fi
  else
    add_line "_No ZFS pools found._"
  fi
else
  add_line "_ZFS tools not installed or ZFS not present._"
fi

# ------------------------------------------------------------------
# Docker Container Inventory
# ------------------------------------------------------------------
add_section_header "Docker Containers"

docker_available=0
no_limit_count=0
host_net_count=0
priv_count=0
no_health_count=0
no_restart_count=0
healthy_count=0
jellyfin_has_dri=0

if command -v docker >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  docker_available=1
  mapfile -t all_containers < <(docker ps -a --format '{{.ID}}\t{{.Names}}\t{{.Status}}' 2>/dev/null || true)

  if [[ ${#all_containers[@]} -eq 0 ]]; then
    add_line "_No Docker containers found._"
  else
    mapfile -t running_ids < <(docker ps -q 2>/dev/null || true)
    declare -A cpu_sum mem_sum sample_n
    if [[ ${#running_ids[@]} -gt 0 ]]; then
      for ((i = 0; i < DOCKER_SAMPLE_COUNT; i++)); do
        while IFS=$'\t' read -r sid scpu smem; do
          [[ -z "$sid" ]] && continue
          scpu=${scpu%%%}
          smem=${smem%%%}
          if is_num "$scpu"; then
            cpu_sum[$sid]=$(awk -v a="${cpu_sum[$sid]:-0}" -v b="$scpu" 'BEGIN{print a+b}')
          fi
          if is_num "$smem"; then
            mem_sum[$sid]=$(awk -v a="${mem_sum[$sid]:-0}" -v b="$smem" 'BEGIN{print a+b}')
          fi
          sample_n[$sid]=$(( ${sample_n[$sid]:-0} + 1 ))
        done < <(docker stats --no-stream --format '{{.ID}}\t{{.CPUPerc}}\t{{.MemPerc}}' 2>/dev/null || true)
        if (( i < DOCKER_SAMPLE_COUNT - 1 )); then
          sleep "$DOCKER_SAMPLE_INTERVAL"
        fi
      done
    fi

    container_table="| ID | Name | Status | Restart Policy | Health | Privileged | Network | CPU (avg %) | Mem (avg %) | Volumes | Devices | Resource Limits |\n|----|------|--------|----------------|--------|------------|---------|-------------|------------|---------|---------|-----------------|"

    for line in "${all_containers[@]}"; do
      cid=$(printf '%s' "$line" | cut -f1)
      cname=$(printf '%s' "$line" | cut -f2)
      status=$(printf '%s' "$line" | cut -f3-)
      [[ -z "$cid" ]] && continue

      inspect=$(docker inspect "$cid" 2>/dev/null || echo "[]")
      restart_policy=$(echo "$inspect" | jq -r '.[0].HostConfig.RestartPolicy.Name // "no"')
      health=$(echo "$inspect" | jq -r '.[0].State.Health.Status // "none"')
      privileged=$(echo "$inspect" | jq -r '.[0].HostConfig.Privileged // false')
      netmode=$(echo "$inspect" | jq -r '.[0].HostConfig.NetworkMode // "default"')
      devices=$(echo "$inspect" | jq -r '.[0].HostConfig.Devices // [] | map(.PathOnHost) | join(",")')
      volumes=$(echo "$inspect" | jq -r '.[0].Mounts // [] | map(.Source) | join(",")')
      nano_cpus=$(echo "$inspect" | jq -r '.[0].HostConfig.NanoCpus // 0')
      mem_limit=$(echo "$inspect" | jq -r '.[0].HostConfig.Memory // 0')
      running=$(echo "$inspect" | jq -r '.[0].State.Running // false')

      limit_parts=()
      if is_int "$nano_cpus" && (( nano_cpus > 0 )); then
        cpu_cores=$(awk -v n="$nano_cpus" 'BEGIN{printf "%.2f", n/1000000000}')
        limit_parts+=("CPU:${cpu_cores} cores")
      else
        limit_parts+=("CPU:none")
      fi
      if is_int "$mem_limit" && (( mem_limit > 0 )); then
        limit_parts+=("Mem:$(human_bytes "$mem_limit")")
      else
        limit_parts+=("Mem:none")
        if [[ "$running" == "true" ]]; then
          no_limit_count=$((no_limit_count + 1))
        fi
      fi
      local_ifs=$IFS
      IFS=', '
      limits="${limit_parts[*]}"
      IFS=$local_ifs

      avg_cpu="N/A"
      avg_mem="N/A"
      if [[ "$running" == "true" && ${sample_n[$cid]:-0} -gt 0 ]]; then
        avg_cpu=$(awk -v s="${cpu_sum[$cid]:-0}" -v n="${sample_n[$cid]}" 'BEGIN{printf "%.1f", s/n}')
        avg_mem=$(awk -v s="${mem_sum[$cid]:-0}" -v n="${sample_n[$cid]}" 'BEGIN{printf "%.1f", s/n}')
        printf '%s\t%s\t%s\n' "$cname" "$avg_cpu" "$avg_mem" >> "$DOCKER_STATS_FILE"
      fi

      volumes_esc=${volumes//|/\\|}
      devices_esc=${devices:--}
      [[ -z "$devices" ]] && devices_esc="-"

      container_table="${container_table}\n| ${cid:0:12} | $cname | $status | $restart_policy | $health | $privileged | $netmode | $avg_cpu | $avg_mem | $volumes_esc | $devices_esc | $limits |"

      if [[ "$netmode" == "host" ]]; then
        host_net_count=$((host_net_count + 1))
      fi
      if [[ "$privileged" == "true" ]]; then
        priv_count=$((priv_count + 1))
      fi
      if [[ "$health" == "none" && "$running" == "true" ]]; then
        no_health_count=$((no_health_count + 1))
      fi
      if [[ "$restart_policy" == "no" || -z "$restart_policy" ]]; then
        no_restart_count=$((no_restart_count + 1))
      fi
      if [[ "$health" == "healthy" ]]; then
        healthy_count=$((healthy_count + 1))
      fi
      if echo "$cname" | grep -qi 'jellyfin'; then
        if echo "$devices" | grep -q '/dev/dri'; then
          jellyfin_has_dri=1
        fi
      fi
    done

    add_table "$container_table"

    if (( healthy_count > 0 )); then
      note_healthy "${healthy_count} container(s) report health=healthy"
    fi
    if (( jellyfin_has_dri > 0 )); then
      note_healthy "Jellyfin has /dev/dri for hardware transcoding"
    fi

    if [[ -s "$DOCKER_STATS_FILE" ]]; then
      add_section_header "Highest Idle CPU Consumers"
      add_line "| Container | CPU % |"
      add_line "|-----------|-------|"
      sort -t$'\t' -k2,2nr "$DOCKER_STATS_FILE" | head -n 5 | while IFS=$'\t' read -r cn cp _; do
        echo "| $cn | $cp |" >> "${BODY_FILE}"
      done
      add_line ""
    fi
  fi
else
  add_line "_Docker not installed or not reachable._"
fi

# ------------------------------------------------------------------
# Recommendations Engine
# ------------------------------------------------------------------
add_section_header "Recommendations"

if [[ "$governor" != "powersave" && "$governor" != "schedutil" ]] && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 20)}'; then
  add_recommendation "CPU Governor Evaluation" "Medium" "Possible responsiveness reduction" "Current governor is ${governor} while system utilization is ${cpu_display}%." "★★★★" "★" "Low" "High"
  note_improve "CPU governor settings"
fi

if [[ "$turbo_enabled" == "Enabled" ]] && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 10)}'; then
  add_recommendation "Turbo Boost Consideration" "Medium" "Reduced burst performance" "Turbo Boost is enabled while host CPU utilization is only ${cpu_display}%." "★★★" "★" "Low" "Medium"
fi

if has_atime_mounts; then
  add_recommendation "Review atime Mount Options" "Low" "Negligible" "Some filesystems are mounted with atime, which can cause extra metadata writes." "★★" "★" "Low" "High"
  note_improve "Unnecessary atime mounts"
fi

if (( zfs_present > 0 )) && command -v zfs >/dev/null 2>&1; then
  uncomp=0
  while IFS= read -r ds; do
    [[ -z "$ds" ]] && continue
    c=$(zfs get -H -o value compression "$ds" 2>/dev/null || echo "off")
    case "$c" in
      lz4|on|zstd|gzip*) ;;
      *) uncomp=$((uncomp + 1)) ;;
    esac
  done < <(zfs list -H -o name 2>/dev/null || true)
  if (( uncomp > 0 )); then
    add_recommendation "Enable ZFS Compression" "Low-Medium" "Minimal impact" "${uncomp} ZFS dataset(s) lack efficient compression (lz4/zstd)." "★★★" "★★" "Low" "Medium"
    note_improve "ZFS compression settings"
  fi
fi

if (( docker_available > 0 )); then
  stopped=$( { docker ps -a -f status=exited -q 2>/dev/null || true; } | wc -l | tr -d ' ')
  if is_int "$stopped" && (( stopped > 0 )); then
    add_recommendation "Remove Stopped Docker Containers" "Low" "None" "There are ${stopped} stopped container(s) occupying disk space." "★★" "★" "Low" "High"
    note_improve "Stopped Docker containers"
  fi

  if (( no_limit_count > 0 )); then
    add_recommendation "Set Memory Limits on Containers" "Medium" "Can prevent noisy-neighbor OOM" "${no_limit_count} running container(s) have no memory limit set." "★★★" "★★" "Low" "High"
    note_improve "Containers without resource limits"
  fi

  if (( host_net_count > 0 )); then
    add_recommendation "Review Host Networking Containers" "Low-Medium" "Depends on service needs" "${host_net_count} container(s) use host networking, which can increase attack surface and reduce isolation." "★★" "★★" "Medium" "High"
  fi

  if (( priv_count > 0 )); then
    add_recommendation "Review Privileged Containers" "Low" "May break hardware-dependent services" "${priv_count} privileged container(s) detected; privileged mode increases risk and can keep devices awake." "★★" "★★★" "Medium" "High"
  fi

  if (( no_health_count > 0 )); then
    add_recommendation "Add Health Checks to Containers" "Low" "None" "${no_health_count} running container(s) have no Docker health check configured." "★★" "★★" "Low" "Medium"
  fi

  if (( no_restart_count > 0 )); then
    add_recommendation "Set Restart Policies" "Low" "None" "${no_restart_count} container(s) use restart policy 'no'; prefer unless-stopped or on-failure for long-running services." "★" "★" "Low" "High"
  fi

  if [[ -s "$DOCKER_STATS_FILE" ]]; then
    while IFS=$'\t' read -r cn cp _; do
      if is_num "$cp" && awk -v c="$cp" 'BEGIN{exit !(c > 2.0)}'; then
        add_recommendation "Investigate Idle CPU in ${cn}" "Medium" "Potentially lower performance if throttled" "Container ${cn} averaged ${cp}% CPU during sampling on a likely-idle host." "★★★" "★★" "Low" "Medium"
        note_improve "High idle CPU containers"
      fi
    done < <(sort -t$'\t' -k2,2nr "$DOCKER_STATS_FILE" | head -n 5)
  fi

  media_containers=("jellyfin" "emby" "plex" "plexmediaserver")
  for mc in "${media_containers[@]}"; do
    while IFS= read -r mname; do
      [[ -z "$mname" ]] && continue
      dri=$(docker inspect "$mname" 2>/dev/null | jq -r '.[0].HostConfig.Devices // [] | map(.PathOnHost) | join(" ")')
      if [[ "$qs_level" == "confirmed" || "$qs_level" == "likely" ]]; then
        if ! echo "$dri" | grep -q '/dev/dri'; then
          add_recommendation "Expose /dev/dri to ${mname}" "Low" "High (hardware transcoding)" "${mname} lacks /dev/dri while HW transcoding appears ${qs_level}." "★★★★" "★★" "Low" "Medium"
          note_improve "Media containers without GPU access"
        fi
      fi
    done < <(docker ps --format '{{.Names}}' 2>/dev/null | grep -i "$mc" || true)
  done

  if [[ "$qs_level" == "likely" && "$vainfo_state" == "not installed" ]]; then
    add_recommendation "Install vainfo to Confirm Quick Sync" "Low" "None" "A render node is present but vainfo is not installed, so HW transcoding cannot be confirmed." "★★" "★" "Low" "High"
  fi

  if docker ps --format '{{.Names}}' 2>/dev/null | grep -Eqi '(prometheus|grafana|beszel)'; then
    add_recommendation "Adjust Monitoring Scrape Intervals" "Low-Medium" "Reduced granularity" "A monitoring stack is present; default short scrape intervals may be excessive on an idle host." "★★" "★" "Low" "Medium"
  fi
fi

if [[ ! -s "$REC_TITLES_FILE" ]]; then
  add_line "_No specific recommendations generated from current telemetry._"
  add_line ""
fi

# ------------------------------------------------------------------
# Quick Wins / Medium / Long Term
# ------------------------------------------------------------------
add_section_header "Quick Wins (<10 min)"
add_line "- Remove stopped Docker containers"
add_line "- Review monitoring scrape intervals"
add_line "- Review and disable atime on rarely-written filesystems"

add_section_header "Medium Effort (≈30-60 min)"
add_line "- Enable ZFS lz4/zstd compression where appropriate"
add_line "- Add /dev/dri device mapping to media containers that lack hardware acceleration"
add_line "- Set memory limits on unbounded containers"
add_line "- Switch CPU governor to powersave or schedutil after workload analysis"

add_section_header "Long Term (hours+)"
add_line "- Migrate frequently accessed datasets to SSD/NVMe"
add_line "- Redesign services to reduce baseline background activity"
add_line "- Replace legacy hardware with more energy-efficient models"

# ------------------------------------------------------------------
# Appendix
# ------------------------------------------------------------------
add_section_header "Appendix"
add_line "<details><summary>Full /proc/stat</summary>"
add_line "\`\`\`"
cat /proc/stat >> "${BODY_FILE}"
add_line "\`\`\`"
add_line "</details>"

add_line "<details><summary>Docker inspect snippets (truncated)</summary>"
add_line "\`\`\`"
if command -v docker >/dev/null 2>&1; then
  while IFS= read -r id; do
    [[ -z "$id" ]] && continue
    docker inspect "$id" 2>/dev/null | head -n 20 || true
    echo
  done < <(docker ps -q 2>/dev/null || true) >> "${BODY_FILE}"
else
  add_line "Docker unavailable."
fi
add_line "\`\`\`"
add_line "</details>"

# ------------------------------------------------------------------
# Calculate energy efficiency score
# ------------------------------------------------------------------
score=100
score_notes=()

if [[ "$governor" != "powersave" && "$governor" != "schedutil" ]]; then
  score=$((score - 10))
  score_notes+=("governor not powersave/schedutil (-10)")
fi
if [[ "$turbo_enabled" == "Enabled" ]] && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 10)}'; then
  score=$((score - 5))
  score_notes+=("turbo enabled while idle (-5)")
fi
if has_atime_mounts; then
  score=$((score - 5))
  score_notes+=("atime mounts (-5)")
fi
if (( zfs_present > 0 && zfs_lz4_ok == 0 )); then
  score=$((score - 5))
  score_notes+=("ZFS without efficient compression (-5)")
fi
if [[ -s "$DOCKER_STATS_FILE" ]]; then
  high_idle=$(awk -F'\t' '$2+0 > 2.0 {c++} END{print c+0}' "$DOCKER_STATS_FILE")
  if (( high_idle > 0 )); then
    ded=$(( high_idle * 3 ))
    (( ded > 15 )) && ded=15
    score=$((score - ded))
    score_notes+=("${high_idle} high-idle container(s) (-${ded})")
  fi
fi
if (( docker_available > 0 )); then
  if (( no_limit_count > 3 )); then
    score=$((score - 5))
    score_notes+=("many containers without memory limits (-5)")
  fi
  if (( priv_count > 0 )); then
    score=$((score - 5))
    score_notes+=("privileged containers (-5)")
  fi
  if (( host_net_count > 0 )); then
    score=$((score - 3))
    score_notes+=("host networking (-3)")
  fi
  if (( jellyfin_has_dri == 0 )); then
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -qi jellyfin; then
      if [[ "$qs_level" == "confirmed" || "$qs_level" == "likely" ]]; then
        score=$((score - 8))
        score_notes+=("Jellyfin without /dev/dri (-8)")
      fi
    fi
  fi
fi
if [[ "$qs_level" == "confirmed" ]]; then
  score=$((score + 3))
  score_notes+=("Quick Sync confirmed (+3)")
fi
if [[ "$governor" == "powersave" || "$governor" == "schedutil" ]]; then
  score=$((score + 2))
  score_notes+=("efficient governor (+2)")
fi

(( score > 100 )) && score=100
(( score < 0 )) && score=0

potential="small (estimated 1-5 W, hardware dependent)"
if (( score < 60 )); then
  potential="moderate (estimated 5-15 W, hardware dependent)"
elif (( score < 80 )); then
  potential="small-moderate (estimated 2-8 W, hardware dependent)"
fi

# ------------------------------------------------------------------
# Assemble final report
# ------------------------------------------------------------------
{
  echo "# Energy Audit Report – v1.1"
  echo "**Timestamp:** $(date -u +"%Y-%m-%d %H:%M UTC")"
  echo "**Hostname:** $(hostname)"
  echo "**Ubuntu:** $(run_cmd lsb_release -ds || echo "N/A")"
  echo "**Kernel:** $(uname -r)"
  echo "**Git branch:** $(run_cmd git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "N/A")"
  echo "**Git commit:** $(run_cmd git rev-parse HEAD 2>/dev/null || echo "N/A")"
  echo ""
  echo "## Executive Summary"
  echo ""
  echo "- **Overall Energy Efficiency Score:** ${score} / 100"
  if [[ ${#score_notes[@]} -gt 0 ]]; then
    score_factors=$(printf '%s; ' "${score_notes[@]}")
    score_factors=${score_factors%; }
    echo "- **Score factors:** ${score_factors}"
  fi
  echo "- **Measured Power:** unavailable (no hardware power meter)"
  echo "- **Potential Power Reduction:** ${potential}"
  echo "- **Potential Improvement Areas:**"
  if [[ -s "$IMPROVE_FILE" ]]; then
    sort -u "$IMPROVE_FILE" | while IFS= read -r item; do
      echo "  - $item"
    done
  else
    echo "  - None identified from current telemetry"
  fi
  echo "- **Top Recommendations:**"
  if [[ -s "$REC_TITLES_FILE" ]]; then
    head -n 5 "$REC_TITLES_FILE" | while IFS= read -r t; do
      echo "  - $t"
    done
  else
    echo "  - None"
  fi
  echo ""
  echo "## Healthy Configuration"
  echo ""
  if [[ -s "$HEALTHY_FILE" ]]; then
    sort -u "$HEALTHY_FILE" | while IFS= read -r item; do
      echo "- $item"
    done
  else
    echo "- No notable best practices detected from current telemetry"
  fi
  echo ""
  cat "$BODY_FILE"
} > "${REPORT_FILE}"

cp "${REPORT_FILE}" "${LATEST_FILE}"
echo "Report written to: ${REPORT_FILE}"
echo "Latest copy: ${LATEST_FILE}"
