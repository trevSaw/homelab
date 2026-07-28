# Energy Audit Report – v1.3
**Timestamp:** 2026-07-28 04:53 UTC
**Hostname:** GM0YEF8V
**Ubuntu:** Debian GNU/Linux 13 (trixie)
**Kernel:** 6.12.96+deb13-amd64
**Git branch:** phase10
**Git commit:** 5cac600f6ed1221bd5970cfca509aef90461db73

## Executive Summary

- **Overall Energy Efficiency Score:** 96 / 100
- **Overall Efficiency Rating:** A
- **Score factors:** efficient governor (+2); balanced profile (+1); low CPU utilization (+3); high clock vs base while idle (-6); turbo enabled while idle (-5); HW transcoding likely (+1)
- **Measured Package Power:** unavailable (no RAPL/turbostat reading)
- **Potential Power Reduction:** small (estimated 1-5 W, hardware dependent)
- **Potential Improvement Areas:**
  - Install vainfo to confirm Quick Sync
- **Top Recommendations:**
  - Turbo Boost Consideration
  - Review High Clock While Idle
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
| turbostat | ❌ Missing |
| nvidia-smi | ❌ Missing |


## System Summary

| Item | Value |
|------|-------|
| Hostname | GM0YEF8V |
| Ubuntu version | Debian GNU/Linux 13 (trixie) |
| Kernel version | 6.12.96+deb13-amd64 |
| Uptime | up 1 day, 5 hours, 25 minutes |
| CPU model | Intel(R) Core(TM) Ultra 7 155U |
| CPU cores | 14 |
| Total Memory | 30Gi |
| Swap | 14Gi |
| Load average | 2.69, 2.61, 2.15 |

## Hardware Identity

| Component | Value |
|-----------|-------|
| CPU | Intel(R) Core(TM) Ultra 7 155U |
| GPU | Intel Corporation Meteor Lake-P [Intel Graphics] (rev 08); |
| Kernel Power Profile | balanced |

## CPU Information

| Parameter | Value |
|-----------|-------|
| CPU Utilization (%) | 6.0 |
| Governor | powersave |
| Available Governors | performance powersave |
| Core Frequency Min | 400 MHz |
| Core Frequency Avg | 2.34 GHz |
| Core Frequency Max | 3.40 GHz |
| Base / Reference Clock | 1.70 GHz |
| Avg Freq vs Base (%) | 137 |
| Turbo Boost | Enabled |
| Package Power (W) | N/A |
| Package Power Source | none |


## Measured Power Telemetry

| Meter | Value |
|-------|-------|
| Intel RAPL / turbostat package | N/A W (source: none) |
| Intel GPU busy (intel_gpu_top) | N/A% |
| NVIDIA GPU | not present / nvidia-smi unavailable |


## Memory Overview

```
               total        used        free      shared  buff/cache   available
Mem:            30Gi        21Gi       1.1Gi       2.4Gi        11Gi       9.0Gi
Swap:           14Gi       768Ki        14Gi
```
- **Swappiness:** 60
- **Swap used:** 768.0 KiB of 14.9 GiB
- **Swap trend (1s sample):** stable
- **Note:** Swap is in use but not actively growing in the short sample; often leftover from earlier memory pressure or reclaim.

## GPU & Intel Quick Sync

- **/dev/dri present:** yes
- **Render node:** detected
- **vainfo:** not installed
- **intel_gpu_top:** not installed
- **Intel GPU busy %:** N/A
- **i915 module:** no
- **Quick Sync / HW transcoding:** Hardware transcoding likely available
- **Jellyfin /dev/dri mapping:** (see Docker inventory)

## Storage & Disk Analysis

| Device | Type | Transport | Rotational | Mountpoint | Mount Options |
|--------|------|-----------|------------|------------|---------------|
| /dev/nvme0n1 | NVMe SSD | nvme | 0 | unmounted | N/A |


## ZFS Inspection

_ZFS tools not installed or ZFS not present._

## Docker Containers

_No Docker containers found._

## Largest Continuous Power Consumers

Relative ranking of continuous draw sources (heuristic; not a watt meter).

| Rank | Source | Signal | Notes |
|------|--------|--------|-------|
| 1 | CPU | 6.0% util; avg freq 2.34 GHz; high clock while idle | Governor=powersave; Turbo=Enabled |
| 2 | GPU | Intel render node present (idle power typically low) | Quick Sync level=likely |
| 3 | Storage | 0 HDD(s); SSD/NVMe=yes | Spinning disks dominate idle storage power |
| 4 | Containers | 0% combined container CPU | 0 running; top=N/A 0% |


## Recommendations

### Turbo Boost Consideration
- **Reason:** Turbo Boost is enabled while host CPU utilization is only 6.0%.
- **Estimated Watt Savings:** ~1-3 W when idle bursts are rare
- **Difficulty:** Low
- **Risk:** Low
- **Confidence:** Medium
- **Energy Impact:** Medium
- **Performance / Transcoding Impact:** Reduced burst performance

### Review High Clock While Idle
- **Reason:** Average core frequency is 137% of base/reference while CPU util is 6.0%.
- **Estimated Watt Savings:** ~1-4 W
- **Difficulty:** Medium
- **Risk:** Low
- **Confidence:** Medium
- **Energy Impact:** Medium
- **Performance / Transcoding Impact:** May reduce single-thread burst speed

### Install vainfo to Confirm Quick Sync
- **Reason:** A render node is present but vainfo is not installed, so HW transcoding cannot be confirmed.
- **Estimated Watt Savings:** ~0 W (verification only)
- **Difficulty:** Low
- **Risk:** Low
- **Confidence:** High
- **Energy Impact:** Low
- **Performance / Transcoding Impact:** None


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
cpu  2658492 240 618960 51781233 162612 0 12979 0 0 0
cpu0 417051 26 43418 3440692 4025 0 2058 0 0 0
cpu1 165014 18 14112 3770163 2666 0 656 0 0 0
cpu2 498197 39 48430 3353778 4279 0 377 0 0 0
cpu3 147507 35 11291 3797319 2177 0 186 0 0 0
cpu4 231144 29 77263 3610141 30945 0 5172 0 0 0
cpu5 217542 13 72689 3636810 30421 0 243 0 0 0
cpu6 183151 8 63664 3681072 28362 0 257 0 0 0
cpu7 159894 8 58965 3706150 16396 0 268 0 0 0
cpu8 155077 14 52914 3729279 12110 0 230 0 0 0
cpu9 147274 12 52608 3738757 11075 0 282 0 0 0
cpu10 144323 11 50722 3745550 7853 0 1205 0 0 0
cpu11 140524 16 49087 3752987 6421 0 261 0 0 0
cpu12 29622 4 12301 3907760 2909 0 339 0 0 0
cpu13 22168 1 11490 3910766 2968 0 1440 0 0 0
intr 166356624 0 4824 0 0 0 0 0 0 0 58590 0 0 2855 0 51160 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1572290 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1821 1813 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1747 1737 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1850846 0 0 0 0 0 0 0 36 629222 0 0 0 0 0 0 0 51160 75 4257 1329 4301 1869 5442 4214 4271 7089 3956 3409 2896 3337 65 7455804 316 417747 20101 20416 24115 17254 16532 18719 18663 20446 19752 20925 26387 22843 21173 60757 25 3434 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
ctxt 436109711
btime 1785108472
processes 901312
procs_running 2
procs_blocked 0
softirq 94659913 1717573 7864709 428160 1154383 698 0 3258195 44563696 126 35672373
```
</details>
<details><summary>Docker inspect snippets (truncated)</summary>
```
```
</details>
