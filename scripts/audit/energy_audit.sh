#!/usr/bin/env bash
# Energy Audit v1.4 – Read-only Bash script
# Generates a Markdown report with actionable, low-impact energy-saving recommendations.
# ------------------------------------------------------------
# 1. Configuration (adjustable without editing the script)
DOCKER_SAMPLE_COUNT=${DOCKER_SAMPLE_COUNT:-3}      # number of docker stats samples
DOCKER_SAMPLE_INTERVAL=${DOCKER_SAMPLE_INTERVAL:-3} # seconds between samples
# Idle memory: Mem% threshold with low CPU% considered "excessive idle memory"
IDLE_MEM_PCT=${IDLE_MEM_PCT:-5.0}
IDLE_MEM_CPU_PCT=${IDLE_MEM_CPU_PCT:-1.0}
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
    echo "0 B"
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

# kHz integer -> human MHz/GHz
human_khz() {
  local khz="${1:-0}"
  if ! is_int "$khz"; then
    echo "N/A"
    return
  fi
  awk -v k="$khz" 'BEGIN {
    if (k >= 1000000) printf "%.2f GHz", k/1000000
    else if (k >= 1000) printf "%.0f MHz", k/1000
    else printf "%d kHz", k
  }'
}

score_to_grade() {
  local s="${1:-0}"
  if ! is_int "$s"; then
    echo "N/A"
    return
  fi
  if (( s >= 90 )); then echo "A"
  elif (( s >= 80 )); then echo "B"
  elif (( s >= 70 )); then echo "C"
  elif (( s >= 60 )); then echo "D"
  else echo "F"
  fi
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

# Collect per-core scaling_cur_freq; prints: min_khz avg_khz max_khz count
get_cpu_freq_stats() {
  local min="" max="" sum=0 n=0 f
  for f in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_cur_freq; do
    [[ -r "$f" ]] || continue
    local v
    v=$(cat "$f" 2>/dev/null || true)
    is_int "$v" || continue
    sum=$((sum + v))
    n=$((n + 1))
    if [[ -z "$min" ]] || (( v < min )); then min=$v; fi
    if [[ -z "$max" ]] || (( v > max )); then max=$v; fi
  done
  if (( n == 0 )); then
    echo "N/A N/A N/A 0"
    return
  fi
  echo "$min $((sum / n)) $max $n"
}

# Optional package power via RAPL energy_uj delta, or turbostat
# Prints: watts source   e.g. "12.34 rapl" or "N/A none"
get_package_power_w() {
  local rapl=""
  for cand in /sys/class/powercap/intel-rapl:0/energy_uj /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj; do
    if [[ -r "$cand" ]]; then
      rapl=$cand
      break
    fi
  done
  if [[ -n "$rapl" ]]; then
    local e1 e2
    e1=$(cat "$rapl" 2>/dev/null || true)
    sleep 1
    e2=$(cat "$rapl" 2>/dev/null || true)
    if is_int "$e1" && is_int "$e2" && (( e2 >= e1 )); then
      awk -v a="$e1" -v b="$e2" 'BEGIN { printf "%.2f", (b-a)/1000000 }'
      return
    fi
  fi
  if command -v turbostat >/dev/null 2>&1; then
    local tw
    tw=$(turbostat --quiet --show PkgWatt -n 1 2>/dev/null | awk 'NR==2 && $1+0==$1 {print $1; exit}')
    if is_num "$tw"; then
      echo "$tw"
      return
    fi
  fi
  echo "N/A"
}

get_package_power_source() {
  local rapl=""
  for cand in /sys/class/powercap/intel-rapl:0/energy_uj /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj; do
    if [[ -r "$cand" ]]; then
      echo "intel_rapl"
      return
    fi
  done
  if command -v turbostat >/dev/null 2>&1; then
    echo "turbostat"
    return
  fi
  echo "none"
}

# Sample Intel GPU busy % via intel_gpu_top when available
get_intel_gpu_busy() {
  if ! command -v intel_gpu_top >/dev/null 2>&1; then
    echo "N/A"
    return
  fi
  local busy=""
  # JSON mode (newer intel_gpu_top)
  if command -v timeout >/dev/null 2>&1; then
    busy=$(timeout 3 intel_gpu_top -J -s 250 2>/dev/null \
      | tr '\n' ' ' \
      | grep -oE '"busy"[[:space:]]*:[[:space:]]*[0-9.]+' \
      | head -1 \
      | grep -oE '[0-9.]+' || true)
  fi
  if is_num "$busy"; then
    awk -v b="$busy" 'BEGIN{printf "%.1f", b}'
    return
  fi
  # Fallback: client list / summary line
  if command -v timeout >/dev/null 2>&1; then
    busy=$(timeout 2 intel_gpu_top -o - -s 500 2>/dev/null \
      | awk '/Render\/3D|Video| eng / {for(i=1;i<=NF;i++) if($i ~ /%/){gsub(/%/,"",$i); print $i; exit}}' || true)
  fi
  if is_num "$busy"; then
    awk -v b="$busy" 'BEGIN{printf "%.1f", b}'
    return
  fi
  echo "N/A"
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
  local reason=$2
  local watts=$3
  local difficulty=$4
  local risk=$5
  local confidence=$6
  local energy=${7:-""}
  local perf=${8:-""}
  add_line "### $title"
  add_line "- **Reason:** $reason"
  add_line "- **Estimated Watt Savings:** $watts"
  add_line "- **Difficulty:** $difficulty"
  add_line "- **Risk:** $risk"
  add_line "- **Confidence:** $confidence"
  if [[ -n "$energy" ]]; then
    add_line "- **Energy Impact:** $energy"
  fi
  if [[ -n "$perf" ]]; then
    add_line "- **Performance / Transcoding Impact:** $perf"
  fi
  add_line ""
  note_rec_title "$title"
}

# ------------------------------------------------------------------
# Dependency Status
# ------------------------------------------------------------------
add_section_header "Dependency Status"
deps=("docker" "git" "jq" "zpool" "zfs" "lsblk" "smartctl" "mpstat" "vmstat" "vainfo" "intel_gpu_top" "lspci" "findmnt" "turbostat" "nvidia-smi")
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
pkg_power_w=$(get_package_power_w)
pkg_power_source=$(get_package_power_source)
intel_gpu_busy=$(get_intel_gpu_busy)

governor=$(run_cmd cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor || echo "N/A")
available_governors=$(run_cmd cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors || echo "N/A")

freq_stats=$(get_cpu_freq_stats)
read_fields freq_min_khz freq_avg_khz freq_max_khz freq_core_n <<<"$freq_stats"

base_khz="N/A"
if [[ -r /sys/devices/system/cpu/cpu0/cpufreq/base_frequency ]]; then
  base_khz=$(cat /sys/devices/system/cpu/cpu0/cpufreq/base_frequency 2>/dev/null || echo "N/A")
elif [[ -r /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq ]]; then
  base_khz=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>/dev/null || echo "N/A")
fi

freq_ratio="N/A"
if is_int "$freq_avg_khz" && is_int "$base_khz" && (( base_khz > 0 )); then
  freq_ratio=$(awk -v a="$freq_avg_khz" -v b="$base_khz" 'BEGIN { printf "%.0f", 100*a/b }')
fi

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

add_table "| Parameter | Value |\n|-----------|-------|\n| CPU Utilization (%) | ${cpu_display} |\n| Governor | ${governor} |\n| Available Governors | ${available_governors} |\n| Core Frequency Min | $(human_khz "${freq_min_khz}") |\n| Core Frequency Avg | $(human_khz "${freq_avg_khz}") |\n| Core Frequency Max | $(human_khz "${freq_max_khz}") |\n| Base / Reference Clock | $(human_khz "${base_khz}") |\n| Avg Freq vs Base (%) | ${freq_ratio} |\n| Turbo Boost | ${turbo_enabled} |\n| Package Power (W) | ${pkg_power_w} |\n| Package Power Source | ${pkg_power_source} |"

add_section_header "Measured Power Telemetry"
add_line "| Meter | Value |"
add_line "|-------|-------|"
if is_num "$pkg_power_w"; then
  add_line "| Intel RAPL / turbostat package | ${pkg_power_w} W (source: ${pkg_power_source}) |"
else
  add_line "| Intel RAPL / turbostat package | unavailable |"
fi
if is_num "$intel_gpu_busy"; then
  add_line "| Intel GPU busy (intel_gpu_top) | ${intel_gpu_busy}% |"
else
  add_line "| Intel GPU busy (intel_gpu_top) | unavailable |"
fi
if command -v nvidia-smi >/dev/null 2>&1; then
  nv_util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || true)
  nv_pwr=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || true)
  add_line "| NVIDIA GPU utilization | ${nv_util:-N/A}% |"
  add_line "| NVIDIA GPU power draw | ${nv_pwr:-N/A} W |"
else
  add_line "| NVIDIA GPU | not present / nvidia-smi unavailable |"
fi
add_line ""

if [[ "$governor" == "powersave" || "$governor" == "schedutil" ]]; then
  note_healthy "CPU governor is ${governor}"
else
  note_improve "CPU governor settings (${governor})"
fi

if [[ "$turbo_enabled" == "Disabled" ]]; then
  note_healthy "Turbo Boost is disabled"
fi

if is_num "$pkg_power_w"; then
  note_healthy "Package power measured at ${pkg_power_w} W (${pkg_power_source})"
fi

if is_num "$intel_gpu_busy"; then
  note_healthy "Intel GPU busy sampled at ${intel_gpu_busy}%"
fi

# ------------------------------------------------------------------
# Memory Overview
# ------------------------------------------------------------------
add_section_header "Memory Overview"
mem_info=$(run_cmd free -h)
add_line "\`\`\`"
add_line "$mem_info"
add_line "\`\`\`"

swappiness=$(run_cmd cat /proc/sys/vm/swappiness || echo "N/A")
swap_used_1=$(run_cmd awk '/Swap:/ {print $3}' /proc/meminfo || echo "0")
sleep 1
swap_used_2=$(run_cmd awk '/Swap:/ {print $3}' /proc/meminfo || echo "0")
# Swap: fields in /proc/meminfo are kB
swap_total_kb=$(run_cmd awk '/SwapTotal:/ {print $2}' /proc/meminfo || echo "0")
swap_free_kb=$(run_cmd awk '/SwapFree:/ {print $2}' /proc/meminfo || echo "0")
swap_used_kb=0
if is_int "$swap_total_kb" && is_int "$swap_free_kb"; then
  swap_used_kb=$((swap_total_kb - swap_free_kb))
fi
swap_trend="stable"
if is_int "$swap_used_1" && is_int "$swap_used_2"; then
  if (( swap_used_2 > swap_used_1 + 1024 )); then
    swap_trend="increasing"
  elif (( swap_used_2 + 1024 < swap_used_1 )); then
    swap_trend="decreasing"
  fi
fi

add_line "- **Swappiness:** ${swappiness}"
add_line "- **Swap used:** $(human_bytes $((swap_used_kb * 1024))) of $(human_bytes $(( ${swap_total_kb:-0} * 1024 )))"
add_line "- **Swap trend (1s sample):** ${swap_trend}"
if [[ "$swap_trend" == "increasing" ]]; then
  add_line "- **Note:** Swap usage increased during sampling — memory pressure may be elevating disk I/O power."
  note_improve "Active swap growth (memory pressure)"
elif is_int "$swap_used_kb" && (( swap_used_kb > 0 )); then
  add_line "- **Note:** Swap is in use but not actively growing in the short sample; often leftover from earlier memory pressure or reclaim."
fi

# ------------------------------------------------------------------
# GPU / Intel Quick Sync detection
# ------------------------------------------------------------------
add_section_header "GPU & Intel Quick Sync"

dri_dir_exists="no"
render_node="not detected"
vainfo_state="not installed"
igt_state="not installed"
qs_conclusion="Hardware transcoding unavailable"
qs_level="unavailable"

if [[ -d /dev/dri ]]; then
  dri_dir_exists="yes"
fi
if [[ -d /dev/dri ]] && ls /dev/dri/renderD* >/dev/null 2>&1; then
  render_node="detected"
  qs_level="likely"
  qs_conclusion="Hardware transcoding likely available"
fi

if command -v vainfo >/dev/null 2>&1; then
  vainfo_state="installed"
  if vainfo 2>/dev/null | grep -Ei 'VAProfile|iHD|i965|Intel' >/dev/null; then
    qs_level="confirmed"
    qs_conclusion="Hardware transcoding confirmed via vainfo"
  elif [[ "$render_node" == "detected" ]]; then
    qs_conclusion="Hardware transcoding likely available (vainfo present but no Intel VA profiles reported)"
  else
    qs_level="unavailable"
    qs_conclusion="Hardware transcoding unavailable (vainfo installed, no usable profiles)"
  fi
fi

if command -v intel_gpu_top >/dev/null 2>&1; then
  igt_state="installed"
fi

i915_loaded="no"
if lsmod 2>/dev/null | grep -qi '^i915'; then
  i915_loaded="yes"
fi

add_line "- **/dev/dri present:** ${dri_dir_exists}"
add_line "- **Render node:** ${render_node}"
add_line "- **vainfo:** ${vainfo_state}"
add_line "- **intel_gpu_top:** ${igt_state}"
add_line "- **Intel GPU busy %:** ${intel_gpu_busy}"
add_line "- **i915 module:** ${i915_loaded}"
add_line "- **Quick Sync / HW transcoding:** ${qs_conclusion}"
add_line "- **Jellyfin /dev/dri mapping:** (see Docker inventory)"

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
disk_table="| Device | Type | Transport | Rotational | Mountpoint | Mount Options |\n|--------|------|-----------|------------|------------|---------------|"
ssd_found=0
hdd_count=0
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  # NAME ROTA TRAN TYPE
  read_fields dev rot tran dtype <<<"$line"
  [[ -z "$dev" ]] && continue
  case "$dev" in
    loop*|ram*|zram*)
      continue
      ;;
  esac
  # skip partitions if TYPE=part (lsblk -dn should be disks only)
  [[ "${dtype:-}" == "part" ]] && continue
  dev_path="/dev/${dev}"
  type="Unknown"
  if [[ "$dev" == nvme* ]] || [[ "${tran:-}" == "nvme" ]]; then
    type="NVMe SSD"
    ssd_found=1
  elif is_int "${rot:-}" && [[ "$rot" -eq 0 ]]; then
    if [[ "${tran:-}" == "sata" ]] || [[ "${tran:-}" == "ata" ]]; then
      type="SATA SSD"
    elif [[ "${tran:-}" == "usb" ]]; then
      type="USB SSD"
    else
      type="SSD"
    fi
    ssd_found=1
    if run_cmd smartctl -i "${dev_path}" | grep -iq "NVMe"; then
      type="NVMe SSD"
    fi
  elif is_int "${rot:-}" && [[ "$rot" -eq 1 ]]; then
    type="HDD"
    hdd_count=$((hdd_count + 1))
  fi
  mount_info=$(run_cmd findmnt -no TARGET,OPTIONS -S "${dev_path}" || run_cmd findmnt -no TARGET,OPTIONS -M "${dev_path}" || echo "")
  mountpoint=$(awk '{print $1}' <<<"${mount_info:-}")
  opts=$(awk '{print $2}' <<<"${mount_info:-}")
  mountpoint=${mountpoint:-"unmounted"}
  opts=${opts:-"N/A"}
  disk_table="${disk_table}\n| ${dev_path} | ${type} | ${tran:-N/A} | ${rot:-N/A} | ${mountpoint} | ${opts} |"
done < <(command -v lsblk >/dev/null && lsblk -dn -o NAME,ROTA,TRAN,TYPE 2>/dev/null || true)
add_table "$disk_table"

if (( ssd_found > 0 )); then
  note_healthy "SSD/NVMe storage present"
fi
if (( hdd_count > 0 )); then
  note_improve "${hdd_count} spinning HDD(s) present (higher idle power than SSD)"
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
      pool_health=$(run_cmd zpool list -H -o health "$pool" || echo "N/A")
      pool_size=$(run_cmd zpool list -H -o size "$pool" || echo "N/A")
      pool_alloc=$(run_cmd zpool list -H -o alloc "$pool" || echo "N/A")
      pool_free=$(run_cmd zpool list -H -o free "$pool" || echo "N/A")
      pool_cap=$(run_cmd zpool list -H -o capacity "$pool" || echo "N/A")
      # zpool capacity often includes a trailing %; strip all % then add exactly one
      pool_cap=$(printf '%s' "$pool_cap" | tr -d '% \r\t')
      pool_comp=$(run_cmd zfs get -H -o value compression "$pool" 2>/dev/null || echo "N/A")
      add_line "### Pool: ${pool}"
      add_line "- Health: ${pool_health:-N/A}"
      if [[ "$pool_cap" == "N/A" || -z "$pool_cap" ]]; then
        add_line "- Size: ${pool_size} | Allocated: ${pool_alloc} | Free: ${pool_free} | Capacity: N/A"
      else
        add_line "- Size: ${pool_size} | Allocated: ${pool_alloc} | Free: ${pool_free} | Capacity: ${pool_cap}%"
      fi
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
running_container_count=0
container_cpu_sum=0
idle_mem_count=0
top_container_name="N/A"
top_container_cpu="0"

if command -v docker >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  docker_available=1
  # Sort by name for deterministic Markdown across runs
  mapfile -t all_containers < <(docker ps -a --format '{{.ID}}\t{{.Names}}\t{{.Status}}' 2>/dev/null | sort -t$'\t' -k2,2 || true)

  if [[ ${#all_containers[@]} -eq 0 ]]; then
    add_line "_No Docker containers found._"
  else
    mapfile -t running_ids < <(docker ps -q 2>/dev/null || true)
    running_container_count=${#running_ids[@]}
    declare -A cpu_sum mem_sum sample_n mem_usage_last
    if [[ ${#running_ids[@]} -gt 0 ]]; then
      for ((i = 0; i < DOCKER_SAMPLE_COUNT; i++)); do
        while IFS=$'\t' read -r sid scpu smem smemuse; do
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
          if [[ -n "$smemuse" ]]; then
            mem_usage_last[$sid]=$smemuse
          fi
        done < <(docker stats --no-stream --format '{{.ID}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.MemUsage}}' 2>/dev/null || true)
        if (( i < DOCKER_SAMPLE_COUNT - 1 )); then
          sleep "$DOCKER_SAMPLE_INTERVAL"
        fi
      done
    fi

    container_table="| ID | Name | Status | Restart Policy | Health | Privileged | Network | CPU (avg %) | Mem (avg %) | Mem Usage | Mem Limit | Volumes | Devices |\n|----|------|--------|----------------|--------|------------|---------|-------------|------------|-----------|-----------|---------|---------|"

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
      mem_limit=$(echo "$inspect" | jq -r '.[0].HostConfig.Memory // 0')
      running=$(echo "$inspect" | jq -r '.[0].State.Running // false')

      mem_limit_h="Unlimited"
      has_mem_limit=0
      if is_int "$mem_limit" && (( mem_limit > 0 )); then
        mem_limit_h=$(human_bytes "$mem_limit")
        has_mem_limit=1
      else
        if [[ "$running" == "true" ]]; then
          no_limit_count=$((no_limit_count + 1))
        fi
      fi

      avg_cpu="N/A"
      avg_mem="N/A"
      mem_usage_h="N/A"
      if [[ "$running" == "true" && ${sample_n[$cid]:-0} -gt 0 ]]; then
        avg_cpu=$(awk -v s="${cpu_sum[$cid]:-0}" -v n="${sample_n[$cid]}" 'BEGIN{printf "%.1f", s/n}')
        avg_mem=$(awk -v s="${mem_sum[$cid]:-0}" -v n="${sample_n[$cid]}" 'BEGIN{printf "%.1f", s/n}')
        # MemUsage looks like "123.4MiB / 2GiB" — usage only; do not treat host RAM as a limit
        raw_mu=${mem_usage_last[$cid]:-}
        if [[ -n "$raw_mu" ]]; then
          mem_usage_h=$(printf '%s' "$raw_mu" | awk -F'/' '{gsub(/^ +| +$/,"",$1); print $1}')
        fi
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$cname" "$avg_cpu" "$avg_mem" "$mem_usage_h" "$mem_limit_h" "$has_mem_limit" >> "$DOCKER_STATS_FILE"
      fi

      volumes_esc=${volumes//|/\\|}
      devices_esc=${devices:--}
      [[ -z "$devices" ]] && devices_esc="-"

      container_table="${container_table}\n| ${cid:0:12} | $cname | $status | $restart_policy | $health | $privileged | $netmode | $avg_cpu | $avg_mem | $mem_usage_h | $mem_limit_h | $volumes_esc | $devices_esc |"

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
      # Annotate QS status in body
      add_line ""
      add_line "- **Jellyfin /dev/dri mapping:** yes"
    else
      if docker ps --format '{{.Names}}' 2>/dev/null | grep -qi jellyfin; then
        add_line ""
        add_line "- **Jellyfin /dev/dri mapping:** no"
      fi
    fi

    if [[ -s "$DOCKER_STATS_FILE" ]]; then
      container_cpu_sum=$(awk -F'\t' '{s+=$2} END{printf "%.1f", s+0}' "$DOCKER_STATS_FILE")
      read_fields top_container_name top_container_cpu _ < <(sort -t$'\t' -k2,2nr -k1,1 "$DOCKER_STATS_FILE" | head -n 1)

      add_section_header "Highest Idle CPU Consumers"
      add_line "| Container | CPU % |"
      add_line "|-----------|-------|"
      sort -t$'\t' -k2,2nr -k1,1 "$DOCKER_STATS_FILE" | head -n 5 | while IFS=$'\t' read -r cn cp _; do
        echo "| $cn | $cp |" >> "${BODY_FILE}"
      done
      add_line ""

      add_section_header "Highest Memory Consumers"
      add_line "| Container | Mem % | Mem Usage | Mem Limit |"
      add_line "|-----------|-------|-----------|-----------|"
      sort -t$'\t' -k3,3nr -k1,1 "$DOCKER_STATS_FILE" | head -n 5 | while IFS=$'\t' read -r cn _ mp mu ml _; do
        echo "| $cn | $mp | ${mu:-N/A} | ${ml:-N/A} |" >> "${BODY_FILE}"
      done
      add_line ""

      # Excessive idle memory: high Mem% with very low CPU on a likely-idle host
      add_section_header "Excessive Idle Memory"
      add_line "Containers averaging ≥${IDLE_MEM_PCT}% host memory with ≤${IDLE_MEM_CPU_PCT}% CPU during sampling."
      add_line ""
      add_line "| Container | Mem % | CPU % | Mem Usage | Mem Limit |"
      add_line "|-----------|-------|-------|-----------|-----------|"
      idle_mem_rows=0
      while IFS=$'\t' read -r cn cp mp mu ml _; do
        if is_num "$cp" && is_num "$mp" && \
           awk -v m="$mp" -v t="$IDLE_MEM_PCT" -v c="$cp" -v ct="$IDLE_MEM_CPU_PCT" \
             'BEGIN{exit !(m+0 >= t+0 && c+0 <= ct+0)}'; then
          echo "| $cn | $mp | $cp | ${mu:-N/A} | ${ml:-N/A} |" >> "${BODY_FILE}"
          idle_mem_rows=$((idle_mem_rows + 1))
        fi
      done < <(sort -t$'\t' -k3,3nr -k1,1 "$DOCKER_STATS_FILE")
      idle_mem_count=$idle_mem_rows
      if (( idle_mem_rows == 0 )); then
        add_line "| _(none at current thresholds)_ | - | - | - | - |"
      fi
      add_line ""
    fi
  fi
else
  add_line "_Docker not installed or not reachable._"
fi

# ------------------------------------------------------------------
# Largest Continuous Power Consumers (heuristic ranking)
# ------------------------------------------------------------------
add_section_header "Largest Continuous Power Consumers"
add_line "Relative ranking of continuous draw sources (heuristic; not a watt meter)."
add_line ""
add_line "| Rank | Source | Signal | Notes |"
add_line "|------|--------|--------|-------|"

# Build sortable score file: score\tsource\tsignal\tnotes
POWER_RANK_FILE="${TMP_DIR}/power_rank.tsv"
: > "$POWER_RANK_FILE"

# Containers: sum of sampled CPU%
cont_signal="${container_cpu_sum:-0}% combined container CPU"
cont_score=$(awk -v c="${container_cpu_sum:-0}" -v n="${running_container_count:-0}" 'BEGIN{print int(c*2 + n*0.5)}')
echo -e "${cont_score}\tContainers\t${cont_signal}\t${running_container_count} running; top=${top_container_name:-N/A} ${top_container_cpu:-0}%" >> "$POWER_RANK_FILE"

# CPU host util
cpu_score=0
cpu_signal="${cpu_display}% util; avg freq $(human_khz "${freq_avg_khz:-0}")"
if is_num "$cpu_util"; then
  cpu_score=$(awk -v u="$cpu_util" 'BEGIN{print int(u*3)}')
fi
if is_int "${freq_ratio:-}" && (( freq_ratio > 80 )) && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 15)}'; then
  cpu_score=$((cpu_score + 15))
  cpu_signal="${cpu_signal}; high clock while idle"
fi
echo -e "${cpu_score}\tCPU\t${cpu_signal}\tGovernor=${governor}; Turbo=${turbo_enabled}" >> "$POWER_RANK_FILE"

# GPU
gpu_score=5
gpu_signal="idle/unknown"
if command -v nvidia-smi >/dev/null 2>&1; then
  gpu_util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  gpu_pwr=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  if is_num "$gpu_util"; then
    gpu_score=$(awk -v u="$gpu_util" 'BEGIN{print int(u*2)}')
    gpu_signal="${gpu_util}% util"
  fi
  if is_num "$gpu_pwr"; then
    gpu_signal="${gpu_signal}; ${gpu_pwr} W draw"
    gpu_score=$(awk -v s="$gpu_score" -v p="$gpu_pwr" 'BEGIN{print int(s + p)}')
  fi
elif is_num "${intel_gpu_busy:-}"; then
  gpu_score=$(awk -v u="$intel_gpu_busy" 'BEGIN{print int(u*2 + 5)}')
  gpu_signal="Intel GPU busy ${intel_gpu_busy}%"
elif [[ "$render_node" == "detected" ]]; then
  gpu_score=8
  gpu_signal="Intel render node present (idle power typically low)"
fi
echo -e "${gpu_score}\tGPU\t${gpu_signal}\tQuick Sync level=${qs_level}" >> "$POWER_RANK_FILE"

# Storage
stor_score=$((hdd_count * 12))
if (( ssd_found > 0 )); then
  stor_score=$((stor_score + 3))
fi
stor_signal="${hdd_count} HDD(s); SSD/NVMe=$([[ $ssd_found -gt 0 ]] && echo yes || echo no)"
echo -e "${stor_score}\tStorage\t${stor_signal}\tSpinning disks dominate idle storage power" >> "$POWER_RANK_FILE"

rank=1
sort -t$'\t' -k1,1nr "$POWER_RANK_FILE" | while IFS=$'\t' read -r sc src sig notes; do
  echo "| ${rank} | ${src} | ${sig} | ${notes} |" >> "${BODY_FILE}"
  rank=$((rank + 1))
done
add_line ""

# ------------------------------------------------------------------
# Recommendations Engine
# ------------------------------------------------------------------
add_section_header "Recommendations"

if [[ "$governor" != "powersave" && "$governor" != "schedutil" ]] && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 20)}'; then
  add_recommendation "CPU Governor Evaluation" \
    "Current governor is ${governor} while system utilization is ${cpu_display}%." \
    "~1-5 W (workload dependent)" "Low" "Low" "High" \
    "Medium" "Possible responsiveness reduction"
  note_improve "CPU governor settings"
fi

if [[ "$turbo_enabled" == "Enabled" ]] && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 10)}'; then
  add_recommendation "Turbo Boost Consideration" \
    "Turbo Boost is enabled while host CPU utilization is only ${cpu_display}%." \
    "~1-3 W when idle bursts are rare" "Low" "Low" "Medium" \
    "Medium" "Reduced burst performance"
fi

if is_int "${freq_ratio:-}" && (( freq_ratio > 70 )) && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 15)}'; then
  add_recommendation "Review High Clock While Idle" \
    "Average core frequency is ${freq_ratio}% of base/reference while CPU util is ${cpu_display}%." \
    "~1-4 W" "Medium" "Low" "Medium" \
    "Medium" "May reduce single-thread burst speed"
fi

if has_atime_mounts; then
  add_recommendation "Review atime Mount Options" \
    "Some filesystems are mounted with atime, which can cause extra metadata writes." \
    "~0.5-2 W on write-heavy mounts" "Low" "Low" "High" \
    "Low" "Negligible performance impact"
  note_improve "Unnecessary atime mounts"
fi

if [[ "$swap_trend" == "increasing" ]]; then
  add_recommendation "Investigate Memory Pressure / Swap Growth" \
    "Swap usage increased during the audit sample window." \
    "~1-5 W from extra disk I/O under pressure" "Medium" "Low" "Medium" \
    "Medium" "Addressing pressure can improve latency"
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
    add_recommendation "Enable ZFS Compression" \
      "${uncomp} ZFS dataset(s) lack efficient compression (lz4/zstd)." \
      "~0.5-2 W via reduced disk I/O" "Medium" "Low" "Medium" \
      "Low-Medium" "Minimal CPU cost for lz4"
    note_improve "ZFS compression settings"
  fi
fi

if (( hdd_count > 0 )); then
  add_recommendation "Reduce Spinning-Disk Idle Load" \
    "${hdd_count} HDD(s) detected; spinning media typically dominate storage idle power." \
    "~3-8 W per always-spinning HDD (hardware dependent)" "High" "Low" "Medium" \
    "Medium" "Migrate hot data to SSD where practical"
fi

if (( docker_available > 0 )); then
  stopped=$( { docker ps -a -f status=exited -q 2>/dev/null || true; } | wc -l | tr -d ' ')
  if is_int "$stopped" && (( stopped > 0 )); then
    add_recommendation "Remove Stopped Docker Containers" \
      "There are ${stopped} stopped container(s) occupying disk space." \
      "~0 W directly (storage reclaim)" "Low" "Low" "High" \
      "Low" "None"
    note_improve "Stopped Docker containers"
  fi

  if (( running_container_count > 25 )); then
    add_recommendation "Reduce Always-On Container Footprint" \
      "${running_container_count} containers are running; each adds baseline CPU/memory wakeups." \
      "~2-10 W depending on services parked" "Medium" "Low" "Medium" \
      "Medium" "Park unused stacks on a schedule"
  fi

  if (( no_limit_count > 0 )); then
    add_recommendation "Set Memory Limits on Containers" \
      "${no_limit_count} running container(s) have no memory limit set." \
      "~0-3 W (indirect via preventing runaway load)" "Medium" "Low" "High" \
      "Medium" "Can prevent noisy-neighbor OOM"
    note_improve "Containers without resource limits"
  fi

  if (( host_net_count > 0 )); then
    add_recommendation "Review Host Networking Containers" \
      "${host_net_count} container(s) use host networking, which can increase attack surface and reduce isolation." \
      "~0-1 W" "Medium" "Medium" "High" \
      "Low-Medium" "Depends on service needs"
  fi

  if (( priv_count > 0 )); then
    add_recommendation "Review Privileged Containers" \
      "${priv_count} privileged container(s) detected; privileged mode increases risk and can keep devices awake." \
      "~0-2 W" "Hard" "Medium" "High" \
      "Low" "May break hardware-dependent services"
  fi

  if (( no_health_count > 0 )); then
    add_recommendation "Add Health Checks to Containers" \
      "${no_health_count} running container(s) have no Docker health check configured." \
      "~0 W (reliability, not watts)" "Medium" "Low" "Medium" \
      "Low" "None"
  fi

  if (( no_restart_count > 0 )); then
    add_recommendation "Set Restart Policies" \
      "${no_restart_count} container(s) use restart policy 'no'; prefer unless-stopped or on-failure for long-running services." \
      "~0 W" "Low" "Low" "High" \
      "Low" "None"
  fi

  if [[ -s "$DOCKER_STATS_FILE" ]]; then
    while IFS=$'\t' read -r cn cp _; do
      if is_num "$cp" && awk -v c="$cp" 'BEGIN{exit !(c > 2.0)}'; then
        est=$(awk -v c="$cp" 'BEGIN{printf "~%.1f-%.1f W", c*0.3, c*0.8}')
        add_recommendation "Investigate Idle CPU in ${cn}" \
          "Container ${cn} averaged ${cp}% CPU during sampling on a likely-idle host." \
          "$est" "Medium" "Low" "Medium" \
          "Medium" "Potentially lower performance if throttled"
        note_improve "High idle CPU containers"
      fi
    done < <(sort -t$'\t' -k2,2nr -k1,1 "$DOCKER_STATS_FILE" | head -n 5)

    while IFS=$'\t' read -r cn cp mp mu ml _; do
      if is_num "$cp" && is_num "$mp" && \
         awk -v m="$mp" -v t="$IDLE_MEM_PCT" -v c="$cp" -v ct="$IDLE_MEM_CPU_PCT" \
           'BEGIN{exit !(m+0 >= t+0 && c+0 <= ct+0)}'; then
        add_recommendation "Review Idle Memory in ${cn}" \
          "Container ${cn} held ${mp}% host memory (${mu:-unknown}) while averaging ${cp}% CPU during sampling." \
          "~0-2 W (indirect via reclaim / cold-start tradeoff)" "Medium" "Low" "Medium" \
          "Medium" "May increase restart latency if memory is reduced"
        note_improve "Containers with excessive idle memory"
      fi
    done < <(sort -t$'\t' -k3,3nr -k1,1 "$DOCKER_STATS_FILE" | head -n 8)
  fi

  if (( idle_mem_count > 0 )); then
    note_improve "${idle_mem_count} container(s) with high idle memory"
  fi

  media_containers=("jellyfin" "emby" "plex" "plexmediaserver")
  for mc in "${media_containers[@]}"; do
    while IFS= read -r mname; do
      [[ -z "$mname" ]] && continue
      dri=$(docker inspect "$mname" 2>/dev/null | jq -r '.[0].HostConfig.Devices // [] | map(.PathOnHost) | join(" ")')
      if [[ "$qs_level" == "confirmed" || "$qs_level" == "likely" ]]; then
        if ! echo "$dri" | grep -q '/dev/dri'; then
          add_recommendation "Expose /dev/dri to ${mname}" \
            "${mname} lacks /dev/dri while HW transcoding appears ${qs_level}." \
            "~5-20 W during transcodes vs CPU encode" "Medium" "Low" "Medium" \
            "Low" "High (hardware transcoding)"
          note_improve "Media containers without GPU access"
        fi
      fi
    done < <(docker ps --format '{{.Names}}' 2>/dev/null | grep -i "$mc" || true)
  done

  if [[ "$qs_level" == "likely" && "$vainfo_state" == "not installed" ]]; then
    add_recommendation "Install vainfo to Confirm Quick Sync" \
      "A render node is present but vainfo is not installed, so HW transcoding cannot be confirmed." \
      "~0 W (verification only)" "Low" "Low" "High" \
      "Low" "None"
  fi

  if docker ps --format '{{.Names}}' 2>/dev/null | grep -Eqi '(prometheus|grafana|beszel)'; then
    add_recommendation "Adjust Monitoring Scrape Intervals" \
      "A monitoring stack is present; default short scrape intervals may be excessive on an idle host." \
      "~0.5-2 W" "Low" "Low" "Medium" \
      "Low-Medium" "Reduced granularity"
  fi
fi

if [[ ! -s "$REC_TITLES_FILE" ]]; then
  add_line "_No specific recommendations generated from current telemetry._"
  add_line ""
fi

# ------------------------------------------------------------------
# Quick Wins / Medium / Long Term (derived from findings; not static filler)
# ------------------------------------------------------------------
add_section_header "Quick Wins (<10 min)"
qw_count=0
if (( docker_available > 0 )); then
  stopped_qw=$( { docker ps -a -f status=exited -q 2>/dev/null || true; } | wc -l | tr -d ' ')
  if is_int "$stopped_qw" && (( stopped_qw > 0 )); then
    add_line "- Remove ${stopped_qw} stopped Docker container(s)"
    qw_count=$((qw_count + 1))
  fi
fi
if has_atime_mounts; then
  add_line "- Review and disable atime on rarely-written filesystems"
  qw_count=$((qw_count + 1))
fi
if docker ps --format '{{.Names}}' 2>/dev/null | grep -Eqi '(prometheus|grafana|beszel)'; then
  add_line "- Review monitoring scrape intervals"
  qw_count=$((qw_count + 1))
fi
if [[ "$qs_level" == "likely" && "$vainfo_state" == "not installed" ]]; then
  add_line "- Install vainfo to confirm Intel Quick Sync"
  qw_count=$((qw_count + 1))
fi
if (( qw_count == 0 )); then
  add_line "- No quick wins identified from current telemetry"
fi

add_section_header "Medium Effort (≈30-60 min)"
me_count=0
if (( zfs_present > 0 && zfs_lz4_ok == 0 )); then
  add_line "- Enable ZFS lz4/zstd compression where appropriate"
  me_count=$((me_count + 1))
fi
if (( jellyfin_has_dri == 0 )) && docker ps --format '{{.Names}}' 2>/dev/null | grep -qi jellyfin; then
  add_line "- Add /dev/dri device mapping to media containers that lack hardware acceleration"
  me_count=$((me_count + 1))
fi
if (( no_limit_count > 0 )); then
  add_line "- Set memory limits on ${no_limit_count} unbounded container(s)"
  me_count=$((me_count + 1))
fi
if (( idle_mem_count > 0 )); then
  add_line "- Review ${idle_mem_count} container(s) with high idle memory footprint"
  me_count=$((me_count + 1))
fi
if [[ "$governor" != "powersave" && "$governor" != "schedutil" ]]; then
  add_line "- Switch CPU governor to powersave or schedutil after workload analysis"
  me_count=$((me_count + 1))
fi
if (( me_count == 0 )); then
  add_line "- No medium-effort items identified from current telemetry"
fi

add_section_header "Long Term (hours+)"
add_line "- Migrate frequently accessed datasets to SSD/NVMe (when ${hdd_count:-0} HDD(s) dominate idle storage power)"
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
elif [[ "$governor" == "powersave" || "$governor" == "schedutil" ]]; then
  score=$((score + 2))
  score_notes+=("efficient governor (+2)")
fi

if [[ "$power_profile" == "performance" ]]; then
  score=$((score - 8))
  score_notes+=("power profile performance (-8)")
elif [[ "$power_profile" == "power-saver" ]]; then
  score=$((score + 3))
  score_notes+=("power-saver profile (+3)")
elif [[ "$power_profile" == "balanced" ]]; then
  score=$((score + 1))
  score_notes+=("balanced profile (+1)")
fi

if is_num "$cpu_util"; then
  if awk -v u="$cpu_util" 'BEGIN{exit !(u > 40)}'; then
    score=$((score - 8))
    score_notes+=("high CPU utilization (-8)")
  elif awk -v u="$cpu_util" 'BEGIN{exit !(u < 10)}'; then
    score=$((score + 3))
    score_notes+=("low CPU utilization (+3)")
  fi
fi

if is_int "${freq_ratio:-}" && (( freq_ratio > 70 )) && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 15)}'; then
  score=$((score - 6))
  score_notes+=("high clock vs base while idle (-6)")
elif is_int "${freq_ratio:-}" && (( freq_ratio < 40 )) && is_num "$cpu_util" && awk -v u="$cpu_util" 'BEGIN{exit !(u < 15)}'; then
  score=$((score + 3))
  score_notes+=("clocks scaled down while idle (+3)")
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
elif (( zfs_present > 0 && zfs_lz4_ok > 0 )); then
  score=$((score + 2))
  score_notes+=("ZFS compression enabled (+2)")
fi

if (( zfs_atime_off > 0 )); then
  score=$((score + 1))
  score_notes+=("ZFS atime=off (+1)")
fi

if (( hdd_count > 0 )); then
  ded=$((hdd_count * 3))
  (( ded > 12 )) && ded=12
  score=$((score - ded))
  score_notes+=("${hdd_count} HDD(s) (-${ded})")
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
  if (( running_container_count > 30 )); then
    score=$((score - 6))
    score_notes+=("very large always-on container set (-6)")
  elif (( running_container_count > 20 )); then
    score=$((score - 3))
    score_notes+=("large always-on container set (-3)")
  fi
  if (( no_limit_count > 3 )); then
    score=$((score - 5))
    score_notes+=("many containers without memory limits (-5)")
  fi
  if (( idle_mem_count > 0 )); then
    ded=$((idle_mem_count * 2))
    (( ded > 10 )) && ded=10
    score=$((score - ded))
    score_notes+=("${idle_mem_count} high-idle-memory container(s) (-${ded})")
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
  elif (( jellyfin_has_dri > 0 )); then
    score=$((score + 4))
    score_notes+=("Jellyfin has /dev/dri (+4)")
  fi
fi

if [[ "$qs_level" == "confirmed" ]]; then
  score=$((score + 3))
  score_notes+=("Quick Sync confirmed (+3)")
elif [[ "$qs_level" == "likely" ]]; then
  score=$((score + 1))
  score_notes+=("HW transcoding likely (+1)")
fi

if is_num "$pkg_power_w"; then
  # Soft signal only — absolute watts vary by platform
  if awk -v p="$pkg_power_w" 'BEGIN{exit !(p > 35)}'; then
    score=$((score - 4))
    score_notes+=("elevated package power ${pkg_power_w}W (-4)")
  elif awk -v p="$pkg_power_w" 'BEGIN{exit !(p < 15)}'; then
    score=$((score + 2))
    score_notes+=("low package power ${pkg_power_w}W (+2)")
  fi
fi

(( score > 100 )) && score=100
(( score < 0 )) && score=0
letter_grade=$(score_to_grade "$score")

potential="small (estimated 1-5 W, hardware dependent)"
if (( score < 60 )); then
  potential="moderate (estimated 5-15 W, hardware dependent)"
elif (( score < 80 )); then
  potential="small-moderate (estimated 2-8 W, hardware dependent)"
fi

measured_power_line="unavailable (no RAPL/turbostat reading)"
if is_num "$pkg_power_w"; then
  measured_power_line="${pkg_power_w} W package via ${pkg_power_source}"
fi
if is_num "${intel_gpu_busy:-}"; then
  measured_power_line="${measured_power_line}; Intel GPU busy ${intel_gpu_busy}%"
fi

# ------------------------------------------------------------------
# Assemble final report
# ------------------------------------------------------------------
{
  echo "# Energy Audit Report – v1.4"
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
  echo "- **Overall Efficiency Rating:** ${letter_grade}"
  if [[ ${#score_notes[@]} -gt 0 ]]; then
    score_factors=$(printf '%s; ' "${score_notes[@]}")
    score_factors=${score_factors%; }
    echo "- **Score factors:** ${score_factors}"
  fi
  echo "- **Measured Package Power:** ${measured_power_line}"
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
echo "Score: ${score}/100 (grade ${letter_grade})"
