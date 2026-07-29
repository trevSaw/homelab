# Energy Audit Report – v1.4 (Sample)

**Timestamp:** 2026-07-29 12:00 UTC  
**Hostname:** mocha  
**Ubuntu:** Ubuntu 22.04.5 LTS  
**Kernel:** 6.8.0-60-generic  
**Git branch:** phase10  
**Git commit:** abcdef1234567890

## Executive Summary

- **Overall Energy Efficiency Score:** 78 / 100
- **Overall Efficiency Rating:** C
- **Score factors:** efficient governor (+2); low CPU utilization (+3); 2 high-idle-memory container(s) (-4); many containers without memory limits (-5)
- **Measured Package Power:** 28.4 W (source: RAPL)
- **Potential Power Reduction:** modest (estimated; hardware dependent)
- **Potential Improvement Areas:**
  - Containers with excessive idle memory
  - many containers without memory limits
- **Top Recommendations:**
  - Review Idle Memory in ollama
  - Set Memory Limits on Unbounded Containers
  - Investigate Idle CPU in beszel-agent

## Healthy Configuration

- CPU governor is powersave
- ZFS pool tank is ONLINE
- SSD/NVMe storage present
- Jellyfin has /dev/dri

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
| jq | ✅ |

## System Summary
| Item | Value |
|------|-------|
| Hostname | mocha |
| Ubuntu version | Ubuntu 22.04.5 LTS |
| Kernel version | 6.8.0-60-generic |
| Uptime | 12 days, 3 hours |
| CPU model | Intel(R) Core(TM) i7-11700K CPU @ 3.60GHz |
| CPU cores | 8 |
| Total Memory | 64 GiB |
| Swap | 8 GiB |
| Load average | 0.40, 0.35, 0.30 |

## CPU Information
| Parameter | Value |
|-----------|-------|
| CPU Utilization (%) | 4 |
| Governor | powersave |
| Available Governors | powersave performance |
| Core Frequency Avg | 1.20 GHz |
| Turbo Boost | Enabled |
| Package Power (W) | 28.4 |
| Package Power Source | RAPL |

## Measured Power Telemetry
| Meter | Value |
|-------|-------|
| Intel RAPL / turbostat package | 28.4 W (source: RAPL) |
| Intel GPU busy (intel_gpu_top) | unavailable |

## Memory Overview
```
              total        used        free      shared  buff/cache   available
Mem:           62Gi        18Gi        8.0Gi       200Mi        36Gi        42Gi
Swap:         8.0Gi          0B       8.0Gi
```
- **Swappiness:** 60
- **Swap used:** 0 B of 8.0 GiB

## GPU & Intel Quick Sync
- **/dev/dri present:** yes
- **vainfo:** not installed
- **Quick Sync / HW transcoding:** likely

## Storage & Disk Analysis
| Device | Type | Rotational | Mountpoint | Mount Options |
|--------|------|------------|------------|---------------|
| /dev/nvme0n1 | NVMe SSD | 0 | /mnt/monarch | defaults,noatime |
| /dev/sda | HDD | 1 | /hive | defaults,relatime |

## ZFS Inspection
### Pool: tank
- Health: ONLINE
- Size: 32.7T | Allocated: 21.3T | Free: 11.4T | Capacity: 65%
- Compression: lz4

| Dataset | compression | atime | recordsize | xattr | sync | logbias | primarycache |
|---------|--------------|-------|------------|------|------|----------|--------------|
| tank | lz4 | off | 128K | on | standard | latency | all |

## Docker Containers
| ID | Name | Status | Restart Policy | Health | Privileged | Network | CPU (avg %) | Mem (avg %) | Mem Usage | Mem Limit | Volumes | Devices |
|----|------|--------|----------------|--------|------------|---------|-------------|------------|-----------|-----------|---------|---------|
| a1b2c3d4e5f6 | ollama | Up 2 days | unless-stopped | healthy | false | bridge | 0.2 | 12.5 | 8.1 GiB | Unlimited | /hive/ollama | - |
| 7f8e9d0c1b2a | jellyfin | Up 5 days | unless-stopped | healthy | false | bridge | 1.1 | 3.2 | 2.0 GiB | Unlimited | /hive/jellyfin/config | /dev/dri |

## Highest Idle CPU Consumers
| Container | CPU % |
|-----------|-------|
| beszel-agent | 2.4 |
| traefik | 1.1 |
| jellyfin | 1.1 |

## Highest Memory Consumers
| Container | Mem % | Mem Usage | Mem Limit |
|-----------|-------|-----------|-----------|
| ollama | 12.5 | 8.1 GiB | Unlimited |
| open-webui | 4.0 | 2.5 GiB | Unlimited |
| jellyfin | 3.2 | 2.0 GiB | Unlimited |

## Excessive Idle Memory
Containers averaging ≥5.0% host memory with ≤1.0% CPU during sampling.

| Container | Mem % | CPU % | Mem Usage | Mem Limit |
|-----------|-------|-------|-----------|-----------|
| ollama | 12.5 | 0.2 | 8.1 GiB | Unlimited |

## Recommendations
### Review Idle Memory in ollama
- **Energy Impact:** Medium
- **Reason:** Container ollama held 12.5% host memory (8.1 GiB) while averaging 0.2% CPU during sampling.
- **Estimated Impact:** ~0-2 W (indirect via reclaim / cold-start tradeoff)

### Investigate Idle CPU in beszel-agent
- **Energy Impact:** Medium
- **Reason:** Container beszel-agent averaged 2.4% CPU during sampling on a likely-idle host.

## Quick Wins (<10 min)
- Remove 2 stopped Docker container(s)
- Review monitoring scrape intervals

## Medium Effort (≈30-60 min)
- Set memory limits on 14 unbounded container(s)
- Review 1 container(s) with high idle memory footprint
- Install vainfo to confirm Intel Quick Sync

## Long Term (hours+)
- Migrate frequently accessed datasets to SSD/NVMe (when 1 HDD(s) dominate idle storage power)
- Redesign services to reduce baseline background activity
- Replace legacy hardware with more energy-efficient models

## Appendix
<details><summary>Full /proc/stat</summary>

```
(sample truncated in documentation example)
```
</details>
