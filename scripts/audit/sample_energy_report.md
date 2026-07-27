# Energy Audit Report – v1.0 (Sample)

**Timestamp:** 2023-09-15 12:00 UTC  
**Hostname:** homelab‑server  
**Ubuntu:** Ubuntu 24.04 LTS  
**Kernel:** 6.8.0‑31‑generic  
**Git branch:** main  
**Git commit:** a1b2c3d4e5f6g7h8i9j0

## Dependency Status
| Tool | Status |
|------|--------|
| docker | ✅ |
| git | ✅ |
| zpool | ✅ |
| zfs | ✅ |
| lsblk | ✅ |
| smartctl | ✅ |
| mpstat | ✅ |
| vmstat | ✅ |
| vainfo | ❌ Missing |
| intel_gpu_top | ❌ Missing |
| lspci | ✅ |
| findmnt | ✅ |

## Executive Summary
- **Overall Energy Efficiency Score:** 85  
- **Measured Power:** unavailable (mocked)  
- **Potential Power Reduction:** small (estimated 1‑5 W, hardware dependent)  
- **Potential Improvement Areas:**  
  - CPU governor settings  
  - Unnecessary atime mounts  
  - Stopped Docker containers  
- **Top Five Recommendations:** (see below after analysis)

## Healthy Configuration
- (none detected yet, will be populated after data collection)

## System Summary
| Item | Value |
|------|-------|
| Hostname | homelab‑server |
| Ubuntu version | Ubuntu 24.04 LTS |
| Kernel version | 6.8.0‑31‑generic |
| Uptime | 3 days, 4 hours, 12 minutes |
| CPU model | Intel(R) Core(TM) i7‑11700K CPU @ 3.60GHz |
| CPU cores | 8 |
| Total Memory | 32 GiB |
| Swap | 4 GiB |
| Load average | 0.12, 0.08, 0.06 |

## CPU Information
| Parameter | Value |
|-----------|-------|
| CPU Utilization (%) | 3% |
| Governor | powersave |
| Available Governors | powersave performance |
| Current Frequency (kHz) | 1200000 |
| Turbo Boost | Disabled |

## Memory Overview
```
              total        used        free      shared  buff/cache   available
Mem:           31Gi       4.2Gi        24Gi       160Mi       2.8Gi        26Gi
Swap:          4.0Gi          0B       4.0Gi
```

## GPU & Intel Quick Sync
- **Quick Sync Availability:** Undetectable

## Storage & Disk Analysis
| Device | Type | Rotational | Mountpoint | Mount Options |
|--------|------|------------|------------|---------------|
| /dev/sda | HDD | 1 | / | defaults,relatime |
| /dev/sdb | SATA SSD | 0 | /var/lib/docker | defaults,noatime |
| /dev/nvme0n1 | NVMe SSD | 0 | /mnt/data | defaults,noatime |

## ZFS Inspection
### Pool: tank
- Health: ONLINE
- Compression: lz4
- ARC size: 2.1GiB

| Dataset | compression | atime | recordsize | xattr | sync | logbias | primarycache |
|---------|--------------|-------|------------|------|------|----------|--------------|
| tank/home | lz4 | on | 128K | on | standard | latency | all |
| tank/docker | off | off | 64K | off | async | latency | metadata |

## Docker Containers
| ID | Name | Status | Restart Policy | Health | Privileged | Network | CPU (avg %) | Mem (avg %) | Volumes | Devices | Resource Limits |
|----|------|--------|----------------|--------|------------|---------|-------------|------------|---------|---------|-----------------|
| 1a2b3c4d5e6f | jellyfin | Up 5 days | always | healthy | false | bridge | 2.3 | 1.8 | /var/lib/jellyfin |  | CPU:0 Nano, Mem:0 B |
| 7f8e9d0c1b2a | nextcloud | Exited (0) 2h ago | no | N/A | false | bridge | N/A | N/A | /var/lib/nextcloud |  | CPU:0 Nano, Mem:0 B |

## Recommendations
### CPU Governor Evaluation
- **Energy Impact:** Medium  
- **Performance / Transcoding Impact:** Possible responsiveness reduction  
- **Reason:** Current governor is `powersave` while system is mostly idle.  
- **Estimated Impact:** ★★★★  
- **Difficulty:** ★  
- **Risk:** Low  
- **Confidence:** High  

### Review atime Mount Options
- **Energy Impact:** Low  
- **Performance / Transcoding Impact:** Negligible  
- **Reason:** Some filesystems are mounted with `atime` which can cause extra writes.  
- **Estimated Impact:** ★★  
- **Difficulty:** ★  
- **Risk:** Low  
- **Confidence:** High  

### Remove Stopped Docker Containers
- **Energy Impact:** Low  
- **Performance / Transcoding Impact:** None  
- **Reason:** There are 2 stopped containers occupying disk space.  
- **Estimated Impact:** ★★  
- **Difficulty:** ★  
- **Risk:** Low  
- **Confidence:** High  

### Enable ZFS lz4 Compression (if not already)
- **Energy Impact:** Low‑Medium  
- **Performance / Transcoding Impact:** Minimal  
- **Reason:** Some datasets lack `lz4` compression.  
- **Estimated Impact:** ★★★  
- **Difficulty:** ★★  
- **Risk:** Low  
- **Confidence:** Medium  

### Adjust Monitoring Scrape Intervals
- **Energy Impact:** Low‑Medium  
- **Performance / Transcoding Impact:** Reduced granularity  
- **Reason:** Monitoring stack defaults to 15‑s intervals which may be excessive on an idle host.  
- **Estimated Impact:** ★★  
- **Difficulty:** ★  
- **Risk:** Low  
- **Confidence:** High  

## Quick Wins (<10 min)
- Remove stopped Docker containers  
- Adjust monitoring scrape intervals to 60 s  
- Review and disable `atime` on rarely‑written filesystems  

## Medium Effort (≈30‑60 min)
- Enable ZFS lz4 compression on appropriate datasets  
- Add `/dev/dri` device mapping to media containers lacking hardware acceleration  
- Switch CPU governor to `powersave` or `schedutil` after workload analysis  

## Long Term (hours +)
- Migrate frequently accessed datasets to SSD/NVMe  
- Redesign services to reduce baseline background activity  
- Replace legacy hardware with more energy‑efficient models  

## Appendix
<details><summary>Full /proc/stat</summary>
```
cpu  12345678 0 1234567 987654321 0 0 0 0 0 0
...
```
</details>

<details><summary>Docker inspect snippets (truncated)</summary>
```
{
  "Id": "1a2b3c4d5e6f...",
  "Name": "/jellyfin",
  ...
}
```
</details>