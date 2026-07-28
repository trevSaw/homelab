# Energy Audit Report – v1.1
**Timestamp:** 2026-07-28 00:23 UTC
**Hostname:** GM0YEF8V
**Ubuntu:** Debian GNU/Linux 13 (trixie)
**Kernel:** 6.12.96+deb13-amd64
**Git branch:** phase10
**Git commit:** a5d0a4b3510e448db62303d42602b98ae3e0db23

## Executive Summary

- **Overall Energy Efficiency Score:** 97 / 100
- **Score factors:** turbo enabled while idle (-5); efficient governor (+2)
- **Measured Power:** unavailable (no hardware power meter)
- **Potential Power Reduction:** small (estimated 1-5 W, hardware dependent)
- **Potential Improvement Areas:**
  - Install vainfo to confirm Quick Sync
- **Top Recommendations:**
  - Turbo Boost Consideration
  - Install vainfo to Confirm Quick Sync

## Healthy Configuration

- CPU governor is powersave
- GPU render node detected (HW transcoding likely available)
- Kernel power profile is balanced
- SSD/NVMe storage present


## Dependency Status

| Tool | Status |
|------|--------|
| docker | ✅ |
| git | ✅ |
| jq | ✅ |
| zpool | ❌ Missing |
| zfs | ❌ Missing |
| lsblk | ✅ |
| smartctl | ❌ Missing |
| mpstat | ✅ |
| vmstat | ✅ |
| vainfo | ❌ Missing |
| intel_gpu_top | ❌ Missing |
| lspci | ✅ |
| findmnt | ✅ |


## System Summary

| Item | Value |
|------|-------|
| Hostname | GM0YEF8V |
| Ubuntu version | Debian GNU/Linux 13 (trixie) |
| Kernel version | 6.12.96+deb13-amd64 |
| Uptime | up 1 day, 55 minutes |
| CPU model | Intel(R) Core(TM) Ultra 7 155U |
| CPU cores | 14 |
| Total Memory | 30Gi |
| Swap | 14Gi |
| Load average | 1.19, 1.47, 1.61 |

## Hardware Identity

| Component | Value |
|-----------|-------|
| CPU | Intel(R) Core(TM) Ultra 7 155U |
| GPU | Intel Corporation Meteor Lake-P [Intel Graphics] (rev 08); |
| Kernel Power Profile | balanced |

## CPU Information

| Parameter | Value |
|-----------|-------|
| CPU Utilization (%) | 8.0 |
| Governor | powersave |
| Available Governors | performance powersave |
| Current Frequency (kHz) | 2089831 |
| Turbo Boost | Enabled |


## Memory Overview

```
               total        used        free      shared  buff/cache   available
Mem:            30Gi        19Gi       945Mi       2.2Gi        13Gi        11Gi
Swap:           14Gi          0B        14Gi
```

## GPU & Intel Quick Sync

- **Render node:** detected
- **vainfo:** not installed
- **i915 module:** no
- **Quick Sync / HW transcoding:** Hardware transcoding likely available

## Storage & Disk Analysis

| Device | Type | Rotational | Mountpoint | Mount Options |
|--------|------|------------|------------|---------------|
| /dev/nvme0n1 | SATA SSD | 0 | unmounted | N/A |


## ZFS Inspection

_ZFS tools not installed or ZFS not present._

## Docker Containers

_No Docker containers found._

## Recommendations

### Turbo Boost Consideration
- **Energy Impact:** Medium
- **Performance / Transcoding Impact:** Reduced burst performance
- **Reason:** Turbo Boost is enabled while host CPU utilization is only 8.0%.
- **Estimated Impact:** ★★★
- **Difficulty:** ★
- **Risk:** Low
- **Confidence:** Medium

### Install vainfo to Confirm Quick Sync
- **Energy Impact:** Low
- **Performance / Transcoding Impact:** None
- **Reason:** A render node is present but vainfo is not installed, so HW transcoding cannot be confirmed.
- **Estimated Impact:** ★★
- **Difficulty:** ★
- **Risk:** Low
- **Confidence:** High


## Quick Wins (<10 min)

- Remove stopped Docker containers
- Review monitoring scrape intervals
- Review and disable atime on rarely-written filesystems

## Medium Effort (≈30-60 min)

- Enable ZFS lz4/zstd compression where appropriate
- Add /dev/dri device mapping to media containers that lack hardware acceleration
- Set memory limits on unbounded containers
- Switch CPU governor to powersave or schedutil after workload analysis

## Long Term (hours+)

- Migrate frequently accessed datasets to SSD/NVMe
- Redesign services to reduce baseline background activity
- Replace legacy hardware with more energy-efficient models

## Appendix

<details><summary>Full /proc/stat</summary>
```
cpu  1752915 215 400148 36501839 133134 0 9156 0 0 0
cpu0 278635 23 28070 2434379 3206 0 1457 0 0 0
cpu1 108455 16 9144 2657130 2154 0 457 0 0 0
cpu2 334139 38 31602 2374501 3452 0 209 0 0 0
cpu3 95373 31 7182 2675813 1813 0 122 0 0 0
cpu4 154142 26 50340 2544494 25403 0 3839 0 0 0
cpu5 144182 12 47306 2562984 24998 0 176 0 0 0
cpu6 119486 6 41070 2594556 23276 0 170 0 0 0
cpu7 103818 6 37973 2613186 13439 0 164 0 0 0
cpu8 100348 14 33534 2629894 9885 0 160 0 0 0
cpu9 95212 10 33657 2636198 8880 0 178 0 0 0
cpu10 93503 10 32314 2641119 6329 0 697 0 0 0
cpu11 90955 14 31190 2646966 5106 0 176 0 0 0
cpu12 20036 3 8692 2744606 2566 0 224 0 0 0
cpu13 14626 1 8068 2746007 2620 0 1122 0 0 0
intr 114247454 0 64 0 0 0 0 0 0 0 38800 0 0 189 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 960 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1255 1249 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1203 1197 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1387144 0 0 0 0 0 0 0 37 518796 0 0 0 0 0 0 0 1 79 22290 10279 32498 15014 17084 12085 10976 13142 8425 8602 8270 7551 777 5140533 566 252914 14998 15666 11313 11303 11959 13575 11867 13722 14185 14645 15608 16095 14655 43166 17 3066 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
ctxt 302401891
btime 1785108472
processes 637844
procs_running 3
procs_blocked 0
softirq 65451160 1354081 5564711 317997 760113 477 0 2449565 30563177 101 24440938
```
</details>
<details><summary>Docker inspect snippets (truncated)</summary>
```
```
</details>
