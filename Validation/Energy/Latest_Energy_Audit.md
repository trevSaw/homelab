# Energy Audit Report – v1.3
**Timestamp:** 2026-07-28 04:56 UTC
**Hostname:** mocha
**Ubuntu:** Ubuntu 22.04.5 LTS
**Kernel:** 6.8.0-124-generic
**Git branch:** phase10
**Git commit:** 9e60d9685100d0488e791be913dd3d19a51e3bdc

## Executive Summary

- **Overall Energy Efficiency Score:** 86 / 100
- **Overall Efficiency Rating:** B
- **Score factors:** efficient governor (+2); balanced profile (+1); low CPU utilization (+3); clocks scaled down while idle (+3); turbo enabled while idle (-5); ZFS compression enabled (+2); ZFS atime=off (+1); 3 HDD(s) (-9); 1 high-idle container(s) (-3); very large always-on container set (-6); many containers without memory limits (-5); host networking (-3); Jellyfin has /dev/dri (+4); HW transcoding likely (+1)
- **Measured Package Power:** unavailable (no RAPL/turbostat reading)
- **Potential Power Reduction:** small (estimated 1-5 W, hardware dependent)
- **Potential Improvement Areas:**
  - 3 spinning HDD(s) present (higher idle power than SSD)
  - Containers without resource limits
  - High idle CPU containers
  - Install vainfo to confirm Quick Sync
- **Top Recommendations:**
  - Turbo Boost Consideration
  - Reduce Spinning-Disk Idle Load
  - Reduce Always-On Container Footprint
  - Set Memory Limits on Containers
  - Review Host Networking Containers

## Healthy Configuration

- 6 container(s) report health=healthy
- CPU governor is powersave
- GPU render node detected (HW transcoding likely available)
- Jellyfin has /dev/dri for hardware transcoding
- Kernel power profile is balanced
- SSD/NVMe storage present
- ZFS atime=off on one or more datasets
- ZFS compression=lz4 (or on) detected
- ZFS pool hive is ONLINE


## Dependency Status

| Tool | Status |
|------|--------|
| docker | ✅ |
| git | ✅ |
| jq | ✅ |
| zpool | ✅ |
| zfs | ✅ |
| lsblk | ✅ |
| smartctl | ✅ |
| mpstat | ❌ Missing |
| vmstat | ✅ |
| vainfo | ❌ Missing |
| intel_gpu_top | ✅ |
| lspci | ✅ |
| findmnt | ✅ |
| turbostat | ✅ |
| nvidia-smi | ✅ |


## System Summary

| Item | Value |
|------|-------|
| Hostname | mocha |
| Ubuntu version | Ubuntu 22.04.5 LTS |
| Kernel version | 6.8.0-124-generic |
| Uptime | up 3 days, 14 hours, 52 minutes |
| CPU model | 11th Gen Intel(R) Core(TM) i5-11400 @ 2.60GHz |
| CPU cores | 12 |
| Total Memory | 62Gi |
| Swap | 4.0Gi |
| Load average | 0.23, 0.26, 0.16 |

## Hardware Identity

| Component | Value |
|-----------|-------|
| CPU | 11th Gen Intel(R) Core(TM) i5-11400 @ 2.60GHz |
| GPU | Intel Corporation Device 43d2 (rev 11);NVIDIA Corporation TU117GL [T400 4GB] (rev a1); |
| Kernel Power Profile | balanced |

## CPU Information

| Parameter | Value |
|-----------|-------|
| CPU Utilization (%) | 0.0 |
| Governor | powersave |
| Available Governors | performance powersave |
| Core Frequency Min | 800 MHz |
| Core Frequency Avg | 829 MHz |
| Core Frequency Max | 983 MHz |
| Base / Reference Clock | 2.60 GHz |
| Avg Freq vs Base (%) | 32 |
| Turbo Boost | Enabled |
| Package Power (W) | N/A |
| Package Power Source | turbostat |


## Measured Power Telemetry

| Meter | Value |
|-------|-------|
| Intel RAPL / turbostat package | unavailable |
| Intel GPU busy (intel_gpu_top) | unavailable |
| NVIDIA GPU utilization | 0% |
| NVIDIA GPU power draw | [N/A] W |


## Memory Overview

```
               total        used        free      shared  buff/cache   available
Mem:            62Gi        38Gi        17Gi       819Mi       6.7Gi        22Gi
Swap:          4.0Gi       2.2Gi       1.8Gi
```
- **Swappiness:** 60
- **Swap used:** 2.2 GiB of 4.0 GiB
- **Swap trend (1s sample):** stable
- **Note:** Swap is in use but not actively growing in the short sample; often leftover from earlier memory pressure or reclaim.

## GPU & Intel Quick Sync

- **/dev/dri present:** yes
- **Render node:** detected
- **vainfo:** not installed
- **intel_gpu_top:** installed
- **Intel GPU busy %:** N/A
- **i915 module:** no
- **Quick Sync / HW transcoding:** Hardware transcoding likely available
- **Jellyfin /dev/dri mapping:** (see Docker inventory)

## Storage & Disk Analysis

| Device | Type | Transport | Rotational | Mountpoint | Mount Options |
|--------|------|-----------|------------|------------|---------------|
| /dev/sda | SATA SSD | sata | 0 | unmounted | N/A |
| /dev/sdb | SATA SSD | sata | 0 | unmounted | N/A |
| /dev/sdc | HDD | sata | 1 | unmounted | N/A |
| /dev/sdd | HDD | sata | 1 | unmounted | N/A |
| /dev/sde | HDD | sata | 1 | unmounted | N/A |


## ZFS Inspection

- **ARC Size:** 31.2 GiB

### Pool: hive
- Health: ONLINE
- Size: 32.7T | Allocated: 21.3T | Free: 11.4T | Capacity: 65%%
- Compression: lz4
| Dataset | compression | atime | recordsize | xattr | sync | logbias | primarycache |
|---------|--------------|-------|------------|------|------|----------|--------------|
| hive | lz4 | off | 1M | on | standard | throughput | all |


## Docker Containers

| ID | Name | Status | Restart Policy | Health | Privileged | Network | CPU (avg %) | Mem (avg %) | Mem Usage | Mem Limit | Volumes | Devices |
|----|------|--------|----------------|--------|------------|---------|-------------|------------|-----------|-----------|---------|---------|
| f503d5109e48 | code-server | Up 20 hours | unless-stopped | none | false | ollama_ollama-net | 0.2 | 0.4 | 263.3MiB | 62.67GiB | /hive/code-server/config | - |
| 3fb4f21ab7fb | n8n | Up 2 days | unless-stopped | none | false | ai-assistant | 0.2 | 0.5 | 290.6MiB | 62.67GiB | /mnt/monarch/appdata/n8n,/mnt/monarch/appdata/n8n/reports,/mnt/monarch/appdata/n8n/workflows | - |
| 55cc2677d23d | open-webui | Up 2 days (healthy) | unless-stopped | healthy | false | ai-assistant | 0.2 | 0.8 | 530.4MiB | 62.67GiB | /mnt/monarch/appdata/open-webui | - |
| 6dc505b198bf | ollama | Up 2 days | unless-stopped | none | false | ai-assistant | 0.0 | 0.2 | 26.75MiB | 12.0 GiB | /hive/ollama | - |
| a976efa8fd53 | beszel-agent | Up 2 days | unless-stopped | none | false | host | 0.0 | 0.0 | 12.16MiB | 62.67GiB | /mnt/monarch/appdata/beszel_agent/beszel_agent_data,/var/run/docker.sock | - |
| 474127a167b9 | beszel | Up 2 days | unless-stopped | none | false | homelab | 0.0 | 0.0 | 33.16MiB | 62.67GiB | /mnt/monarch/appdata/beszel/beszel_data | - |
| e75dafa8c7aa | odysseus-odysseus-1 | Up 2 days | unless-stopped | none | false | ollama_ollama-net | 0.2 | 0.3 | 194.4MiB | 62.67GiB | /mnt/monarch/appdata/odysseus/logs,/hive,/mnt/monarch,/mnt/monarch/appdata/odysseus/data/huggingface,/mnt/monarch/appdata/odysseus/data/local,/mnt/monarch/appdata/odysseus/data/ssh,/mnt/monarch/appdata/odysseus/data | - |
| 87f9e7338729 | odysseus-searxng-1 | Up 2 days (healthy) | unless-stopped | healthy | false | odysseus_default | 0.0 | 0.2 | 104.4MiB | 62.67GiB | /var/lib/docker/volumes/odysseus_searxng-data/_data,/mnt/monarch/appdata/odysseus/config/searxng/settings.yml,/var/lib/docker/volumes/916569f51cab5fb00431870b0e2ae844e22155db93f73255a65a215bfeb8d87e/_data | - |
| 632f053c5d35 | odysseus-ntfy-1 | Up 2 days | unless-stopped | none | false | odysseus_default | 0.0 | 0.0 | 24.55MiB | 62.67GiB | /var/lib/docker/volumes/odysseus_ntfy-cache/_data | - |
| a62aa3a5beb6 | odysseus-chromadb-1 | Up 2 days | unless-stopped | none | false | odysseus_default | 0.0 | 0.0 | 12.66MiB | 62.67GiB | /var/lib/docker/volumes/odysseus_chromadb-data/_data | - |
| 3b7549950c11 | honcho-deriver | Up 2 days | unless-stopped | none | false | ollama_ollama-net | 0.0 | 0.1 | 38.56MiB | 62.67GiB |  | - |
| ff4505b038a5 | honcho-api | Up 2 days | unless-stopped | none | false | ollama_ollama-net | 0.2 | 0.0 | 18.64MiB | 62.67GiB |  | - |
| cd2a7e91d708 | honcho-postgres | Up 3 days | unless-stopped | none | false | ollama_ollama-net | 0.0 | 0.0 | 33.3MiB | 62.67GiB | /mnt/monarch/appdata/honcho/postgres | - |
| b1ffe4ad6922 | honcho-redis | Up 3 days | unless-stopped | none | false | ollama_ollama-net | 0.6 | 0.0 | 2.941MiB | 62.67GiB | /mnt/monarch/appdata/honcho/redis | - |
| f929436b4a9c | hermes | Up 3 days | unless-stopped | none | false | ollama_ollama-net | 0.3 | 0.3 | 205MiB | 62.67GiB | /mnt/monarch/appdata/hermes | - |
| 7341b5c97a12 | traefik | Up 20 hours | always | none | false | proxy | 0.0 | 0.1 | 77.05MiB | 62.67GiB | /etc/localtime,/mnt/monarch/appdata/traefik/acme.json,/var/run/docker.sock | - |
| 4f375bb12652 | prowlarr | Up 3 days | unless-stopped | none | false | hotio_default | 0.2 | 1.6 | 182.8MiB | 11.3 GiB | /DATA/AppData/config | - |
| 77e9ae45a755 | byparr-byparr-1 | Up 2 days (healthy) | unless-stopped | healthy | false | hotio_default | 0.2 | 1.0 | 612.3MiB | 62.67GiB |  | - |
| 05c202b59278 | jellyfin | Up 3 days | unless-stopped | none | false | proxy | 0.1 | 1.0 | 616.9MiB | 62.67GiB | /hive/jellyfin/config,/hive/jellyfin/movie,/hive/jellyfin/tv | /dev/dri |
| a1e89388d9ed | calibre | Up 3 days | unless-stopped | none | false | proxy | 2.6 | 1.2 | 747.2MiB | 62.67GiB | /hive/library/Kavita/browser_cache,/hive/library/Kavita/fanfic/novelas,/hive/calibre/config | - |
| a54bf5093d7b | calibre-web | Up 3 days | unless-stopped | none | false | proxy | 0.0 | 0.2 | 163.1MiB | 62.67GiB | /hive/library/Kavita/fanfic/novelas,/hive/calibre-web/config | - |
| 94c960b7d344 | kavita | Up 2 days (healthy) | unless-stopped | healthy | false | proxy | 0.6 | 0.6 | 376.4MiB | 62.67GiB | /hive/library/Kavita/Books,/hive/library/Kavita/Comics,/hive/library/Kavita/fanfic,/ssd/appdata/kavita/config,/hive/library/Kavita/Manga | - |
| 7f9359b94ed4 | nextcloud-db | Up 2 days | unless-stopped | none | false | cloud_nextcloud_net | 0.0 | 0.0 | 33.6MiB | 62.67GiB | /mnt/monarch/databases/nextcloud-mariadb | - |
| a628a5f8406a | homepage | Up 2 days (healthy) | always | healthy | false | proxy | 0.0 | 0.2 | 99.57MiB | 62.67GiB | /hive/config/homepage,/hive/data/homepage/images | - |
| c77af0514b4b | nextcloud | Up 2 days | unless-stopped | none | false | cloud_nextcloud_net | 0.0 | 0.1 | 91.34MiB | 62.67GiB | /hive/cloud/nextcloud,/hive/cloud/config,/hive/cloud/apps,/hive/cloud/data,/hive/cloud/theme | - |
| 906fe3093bc3 | portainer | Up 2 days | always | none | false | portainer_network | 0.0 | 0.1 | 54.1MiB | 62.67GiB | /hive/portainer,/var/run/docker.sock | - |
| 266edc433d21 | actual-server | Up 2 days | unless-stopped | none | false | big-bear-actual-server_default | 0.0 | 0.1 | 37.94MiB | 62.67GiB | /DATA/AppData/big-bear-actual-server | - |
| f3feef78096e | jellyseerr | Up 3 days | unless-stopped | none | false | bridge | 0.0 | 0.3 | 206.7MiB | 62.7 GiB | /DATA/AppData/jellyseerr/config | - |
| dfabc78adb12 | nzbget | Up 3 days | unless-stopped | none | false | container:7a88dfbcbf07df9c107d1105ac67f1cbbc7ba00c4db54bb9e5d40c5189b8ee65 | 0.0 | 0.1 | 20.01MiB | 24.8 GiB | /hive/NZBget/config,/hive/downloads,/hive/NZBget/config/scripts | - |
| 97df3db91ae6 | radarr | Up 3 days | unless-stopped | none | false | hotio_default | 1.6 | 35.4 | 181.5MiB | 512.0 MiB | /DATA/AppData/radarr/config,/hive/downloads,/hive/jellyfin/movie | - |
| e6231a2d1069 | readarr | Up 3 days | unless-stopped | none | false | hotio_default | 0.1 | 0.2 | 134.6MiB | 62.67GiB | /hive/cloud/data/fatherfranku/files/Kavita/Books,/hive/readarr,/hive/downloads/completed/Readarr | - |
| 7a88dfbcbf07 | qbittorrent | Up 3 days | unless-stopped | none | false | hotio_default | 0.1 | 0.4 | 64.43MiB | 17.2 GiB | /hive/Hotio/config,/hive/downloads/completed | - |
| 790040db9af0 | linuxserver-lazylibrarian-app-1 | Up 3 days | unless-stopped | none | false | linuxserver-lazylibrarian_default | 0.0 | 0.1 | 89.36MiB | 62.67GiB | /DATA/AppData/lazylibrarian/books,/DATA/AppData/lazylibrarian/config,/DATA/AppData/lazylibrarian/downloads | - |
| 590a710b4c3f | big-bear-crafty | Up 2 days | unless-stopped | none | false | big-bear-crafty | 0.2 | 0.9 | 140.9MiB | 16.0 GiB | /DATA/AppData/big-bear-crafty/data/config,/DATA/AppData/big-bear-crafty/data/backups,/DATA/AppData/big-bear-crafty/data/import,/DATA/AppData/big-bear-crafty/data/logs,/DATA/AppData/big-bear-crafty/data/servers | - |
| 07ffdc3eb204 | linuxserver-mariadb-app-1 | Up 3 days | unless-stopped | none | false | linuxserver-mariadb_default | 0.0 | 0.5 | 20.55MiB | 4.0 GiB | /DATA/AppData/mariadb/config | - |
| 150c9e438449 | uptimekuma | Up 2 days (healthy) | unless-stopped | healthy | false | bridge | 0.5 | 0.2 | 123.2MiB | 62.67GiB | /DATA/AppData/uptimekuma/app/data | - |
| c4ba61176c15 | bazarr | Up 3 days | unless-stopped | none | false | bridge | 0.1 | 2.4 | 204.3MiB | 8.2 GiB | /DATA/AppData/bazarr/config,/hive/jellyfin/movie,/hive/jellyfin/tv | - |


- **Jellyfin /dev/dri mapping:** yes

## Highest Idle CPU Consumers

| Container | CPU % |
|-----------|-------|
| calibre | 2.6 |
| radarr | 1.6 |
| honcho-redis | 0.6 |
| kavita | 0.6 |
| uptimekuma | 0.5 |


## Highest Memory Consumers

| Container | Mem % | Mem Usage | Mem Limit |
|-----------|-------|-----------|-----------|
| radarr | 35.4 | 181.5MiB | 512.0 MiB |
| bazarr | 2.4 | 204.3MiB | 8.2 GiB |
| prowlarr | 1.6 | 182.8MiB | 11.3 GiB |
| calibre | 1.2 | 747.2MiB | 62.67GiB |
| byparr-byparr-1 | 1.0 | 612.3MiB | 62.67GiB |


## Largest Continuous Power Consumers

Relative ranking of continuous draw sources (heuristic; not a watt meter).

| Rank | Source | Signal | Notes |
|------|--------|--------|-------|
| 1 | Storage | 3 HDD(s); SSD/NVMe=yes | Spinning disks dominate idle storage power |
| 2 | Containers | 8.2% combined container CPU | 37 running; top=calibre 2.6% |
| 3 | CPU | 0.0% util; avg freq 829 MHz | Governor=powersave; Turbo=Enabled |
| 4 | GPU | 0% util | Quick Sync level=likely |


## Recommendations

### Turbo Boost Consideration
- **Reason:** Turbo Boost is enabled while host CPU utilization is only 0.0%.
- **Estimated Watt Savings:** ~1-3 W when idle bursts are rare
- **Difficulty:** Low
- **Risk:** Low
- **Confidence:** Medium
- **Energy Impact:** Medium
- **Performance / Transcoding Impact:** Reduced burst performance

### Reduce Spinning-Disk Idle Load
- **Reason:** 3 HDD(s) detected; spinning media typically dominate storage idle power.
- **Estimated Watt Savings:** ~3-8 W per always-spinning HDD (hardware dependent)
- **Difficulty:** High
- **Risk:** Low
- **Confidence:** Medium
- **Energy Impact:** Medium
- **Performance / Transcoding Impact:** Migrate hot data to SSD where practical

### Reduce Always-On Container Footprint
- **Reason:** 37 containers are running; each adds baseline CPU/memory wakeups.
- **Estimated Watt Savings:** ~2-10 W depending on services parked
- **Difficulty:** Medium
- **Risk:** Low
- **Confidence:** Medium
- **Energy Impact:** Medium
- **Performance / Transcoding Impact:** Park unused stacks on a schedule

### Set Memory Limits on Containers
- **Reason:** 28 running container(s) have no memory limit set.
- **Estimated Watt Savings:** ~0-3 W (indirect via preventing runaway load)
- **Difficulty:** Medium
- **Risk:** Low
- **Confidence:** High
- **Energy Impact:** Medium
- **Performance / Transcoding Impact:** Can prevent noisy-neighbor OOM

### Review Host Networking Containers
- **Reason:** 1 container(s) use host networking, which can increase attack surface and reduce isolation.
- **Estimated Watt Savings:** ~0-1 W
- **Difficulty:** Medium
- **Risk:** Medium
- **Confidence:** High
- **Energy Impact:** Low-Medium
- **Performance / Transcoding Impact:** Depends on service needs

### Add Health Checks to Containers
- **Reason:** 31 running container(s) have no Docker health check configured.
- **Estimated Watt Savings:** ~0 W (reliability, not watts)
- **Difficulty:** Medium
- **Risk:** Low
- **Confidence:** Medium
- **Energy Impact:** Low
- **Performance / Transcoding Impact:** None

### Investigate Idle CPU in calibre
- **Reason:** Container calibre averaged 2.6% CPU during sampling on a likely-idle host.
- **Estimated Watt Savings:** ~0.8-2.1 W
- **Difficulty:** Medium
- **Risk:** Low
- **Confidence:** Medium
- **Energy Impact:** Medium
- **Performance / Transcoding Impact:** Potentially lower performance if throttled

### Install vainfo to Confirm Quick Sync
- **Reason:** A render node is present but vainfo is not installed, so HW transcoding cannot be confirmed.
- **Estimated Watt Savings:** ~0 W (verification only)
- **Difficulty:** Low
- **Risk:** Low
- **Confidence:** High
- **Energy Impact:** Low
- **Performance / Transcoding Impact:** None

### Adjust Monitoring Scrape Intervals
- **Reason:** A monitoring stack is present; default short scrape intervals may be excessive on an idle host.
- **Estimated Watt Savings:** ~0.5-2 W
- **Difficulty:** Low
- **Risk:** Low
- **Confidence:** Medium
- **Energy Impact:** Low-Medium
- **Performance / Transcoding Impact:** Reduced granularity


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
cpu  3509240 8154 1517369 368618096 501427 0 50571 0 0 0
cpu0 301770 899 135473 30662082 31593 0 1637 0 0 0
cpu1 285673 784 133555 30706097 33308 0 20329 0 0 0
cpu2 296586 778 127690 30731114 33211 0 824 0 0 0
cpu3 296753 352 128053 30727829 37375 0 871 0 0 0
cpu4 288651 483 126868 30686912 79200 0 4633 0 0 0
cpu5 298391 787 125939 30691297 74896 0 891 0 0 0
cpu6 283444 790 112367 30750459 40825 0 899 0 0 0
cpu7 294017 602 122625 30738016 38413 0 832 0 0 0
cpu8 292255 1128 126745 30736774 35899 0 1610 0 0 0
cpu9 289462 566 124282 30714247 31592 0 14648 0 0 0
cpu10 299306 532 126594 30730816 33558 0 1598 0 0 0
cpu11 282926 448 127172 30742448 31552 0 1795 0 0 0
intr 638433014 56 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 6 337 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 6603702 7113 2410797 1 5401160 4830148 16802996 5526748 330686 49 8 0 0 0 0 0 0 0 0 0 0 0 0 2 842 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
ctxt 1123539958
btime 1784901851
processes 3625235
procs_running 1
procs_blocked 0
softirq 328888710 221 25673838 279199 53184148 8241655 0 767922 140601665 2824923 97315139
```
</details>
<details><summary>Docker inspect snippets (truncated)</summary>
```
[
    {
        "Id": "f503d5109e48bafa65616080c31b9ecd78b75b889a48627cad8383a9d231b12e",
        "Created": "2026-07-21T13:02:07.499591161Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 2782600,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-27T09:21:46.39331957Z",
            "FinishedAt": "2026-07-27T09:21:46.228673176Z"
        },
        "Image": "sha256:f55d5183ae473b6cca88c1defcc71b5687384ac8ad98541eab1fcf7723d5255c",

[
    {
        "Id": "3fb4f21ab7fbe3d8a09474df93bbf8718394cbd17723684445955ce728d17454",
        "Created": "2026-06-25T13:34:22.901606978Z",
        "Path": "tini",
        "Args": [
            "--",
            "/docker-entrypoint.sh"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 761265,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:33.440390865Z",

[
    {
        "Id": "55cc2677d23ddcb0e5953aaad634a682e260448ad972c5261c59b2bdd8a8aac6",
        "Created": "2026-06-25T10:19:06.704558956Z",
        "Path": "bash",
        "Args": [
            "start.sh"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 762000,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:33.668160511Z",
            "FinishedAt": "2026-07-25T08:11:21.817471176Z",

[
    {
        "Id": "6dc505b198bf43bcc761f46396b2906986e348149940c003d8a395d3405c08c4",
        "Created": "2026-06-25T10:19:06.663596169Z",
        "Path": "/bin/ollama",
        "Args": [
            "serve"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 761649,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:33.562832009Z",
            "FinishedAt": "2026-07-25T08:11:21.39531163Z"

[
    {
        "Id": "a976efa8fd53b580d981da79535afd4b14a9fb2979f4fbf48d32a3eedc701fc0",
        "Created": "2026-06-24T13:21:54.400755941Z",
        "Path": "/agent",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757079,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:24.885936589Z",
            "FinishedAt": "2026-07-25T08:11:21.306007895Z"
        },
        "Image": "sha256:3be93b5c1b63f84c88757141da72b774f5aced9512a7752bd98b3eae148bcf14",

[
    {
        "Id": "474127a167b958c37f6b4bd7df1941467f6490dacf10263077e00f9ece539aae",
        "Created": "2026-06-24T10:25:17.598874528Z",
        "Path": "/beszel",
        "Args": [
            "serve",
            "--http=0.0.0.0:8090"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757270,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:25.19294324Z",

[
    {
        "Id": "e75dafa8c7aa24605422dd4d354416c318e809bc31d8cd82d1e79e6d9cc1573e",
        "Created": "2026-06-23T11:54:16.105476785Z",
        "Path": "/usr/local/bin/entrypoint.sh",
        "Args": [
            "uvicorn",
            "app:app",
            "--host",
            "0.0.0.0",
            "--port",
            "7000"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,

[
    {
        "Id": "87f9e733872992b752bba36a2e5f18c57957138142373eb0b72d521df6da859b",
        "Created": "2026-06-23T11:54:16.051829764Z",
        "Path": "/bin/sh",
        "Args": [
            "-c",
            "set -eu\nif [ ! -s /etc/searxng/settings.yml ] || grep -q 'odysseus-local-searxng-json-2026-05-30\\|__SEARXNG_SECRET__' /etc/searxng/settings.yml; then\n  secret=\"${SEARXNG_SECRET:-}\"\n  if [ -z \"$secret\" ]; then\n    secret=\"$(python -c 'import secrets; print(secrets.token_urlsafe(48))')\"\n  fi\n  sed \"s|__SEARXNG_SECRET__|$secret|g\" /tmp/searxng-settings.yml.template > /etc/searxng/settings.yml\nfi\nexec /usr/local/searxng/entrypoint.sh\n"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757159,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:25.012091055Z",

[
    {
        "Id": "632f053c5d35753d7c99ab05c7b2c47fd683c0e0edcea83f5249ffc3548541df",
        "Created": "2026-06-23T11:54:16.051669294Z",
        "Path": "ntfy",
        "Args": [
            "serve"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757443,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:25.42632123Z",
            "FinishedAt": "2026-07-25T08:11:21.622874293Z"

[
    {
        "Id": "a62aa3a5beb666c07d2bbeabe9c6667da367fea9b328d9b8fade4f3ae937a90a",
        "Created": "2026-06-23T11:54:16.051649644Z",
        "Path": "dumb-init",
        "Args": [
            "--",
            "chroma",
            "run",
            "/config.yaml"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 760165,
            "ExitCode": 0,

[
    {
        "Id": "3b7549950c111570c39525c0a92da57578a726d0a4788be7820aeaf899fa5bd0",
        "Created": "2026-06-20T05:05:27.605708039Z",
        "Path": "/app/.venv/bin/python",
        "Args": [
            "-m",
            "src.deriver"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757347,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:25.247883748Z",

[
    {
        "Id": "ff4505b038a52b945417cc21ac3a5f50739e565cf70db0a4a1ab6f031bd71782",
        "Created": "2026-06-20T05:05:27.584553564Z",
        "Path": "sh",
        "Args": [
            "docker/entrypoint.sh"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 761368,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:33.458950007Z",
            "FinishedAt": "2026-07-25T08:11:21.723317119Z"

[
    {
        "Id": "cd2a7e91d7080b2c3f84f0a404d8f0bae859156eaeb0cedea9c074c54017713e",
        "Created": "2026-06-20T05:05:27.536939718Z",
        "Path": "docker-entrypoint.sh",
        "Args": [
            "postgres"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 5232,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.387648087Z",
            "FinishedAt": "2026-07-24T12:15:32.911262379Z"

[
    {
        "Id": "b1ffe4ad6922a09db42ffecb88618ff2a2f5cc3f8832edfc319eb1d4204d391c",
        "Created": "2026-06-20T05:05:27.536826055Z",
        "Path": "docker-entrypoint.sh",
        "Args": [
            "redis-server"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 4858,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.346921672Z",
            "FinishedAt": "2026-07-24T12:15:33.05376935Z"

[
    {
        "Id": "f929436b4a9c2798bed50cc3610c8901704e8062dfd65a4ff5dcbdd91a549bbd",
        "Created": "2026-06-20T05:04:12.043551796Z",
        "Path": "/init",
        "Args": [
            "/opt/hermes/docker/main-wrapper.sh",
            "gateway",
            "run"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 5356,
            "ExitCode": 0,
            "Error": "",

[
    {
        "Id": "7341b5c97a12a5a89a114284fef182129a9604126c75fcb23554da447fcdee6e",
        "Created": "2026-06-08T12:50:57.37457483Z",
        "Path": "/entrypoint.sh",
        "Args": [
            "--global.checknewversion=true",
            "--global.sendanonymoususage=false",
            "--log.level=DEBUG",
            "--api.dashboard=true",
            "--api.insecure=false",
            "--providers.docker=true",
            "--providers.docker.exposedbydefault=false",
            "--providers.docker.network=proxy",
            "--entrypoints.web.address=:80",
            "--entrypoints.web.http.redirections.entrypoint.to=websecure",
            "--entrypoints.web.http.redirections.entrypoint.scheme=https",
            "--entrypoints.websecure.address=:443",
            "--certificatesresolvers.le.acme.email=tsawyerm@gmail.com",
            "--certificatesresolvers.le.acme.storage=/etc/traefik/acme.json",

[
    {
        "Id": "4f375bb12652646ce73a692e416d030eae3d846a210a1abfbea600b72a4701b3",
        "Created": "2026-04-28T23:45:27.798946895Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 5210,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.382725294Z",
            "FinishedAt": "2026-07-24T12:15:37.043556415Z"
        },
        "Image": "sha256:27c5c18f8673e38e0cf339514b9bf84f8446f3befeb262ef24637772504aca77",

[
    {
        "Id": "77e9ae45a755b76e491379c5db668f0efda8a2575f9b7a51436cd3f47e8e75b8",
        "Created": "2026-04-28T23:36:52.465392545Z",
        "Path": "uv",
        "Args": [
            "run",
            "main.py"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757166,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:25.017126264Z",

[
    {
        "Id": "05c202b59278709a6fd78e3bc6eb5b5e89ea370ef17db560cb57eb600de6401a",
        "Created": "2026-04-02T02:19:29.738368709Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 4805,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.302715778Z",
            "FinishedAt": "2026-07-24T12:15:36.723207055Z"
        },
        "Image": "sha256:96c9f0951b384edca3a5d72b3cd2d480e587feaafef6fc3da34c8cc88c66d0fe",

[
    {
        "Id": "a1e89388d9ed4b62557b4c9edaf469a4d8ffeeb463f29319185c107f087e699e",
        "Created": "2026-03-29T11:53:42.041857498Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 5260,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.395950837Z",
            "FinishedAt": "2026-07-24T12:15:41.12924396Z"
        },
        "Image": "sha256:b91d595bc98f9ad3556e9992f2c4c13262dc81b319529b781930e782a152381d",

[
    {
        "Id": "a54bf5093d7bdf183e4a35e0b592e518856b76a5b2def65bb8a775a24400ff96",
        "Created": "2026-03-29T11:53:42.041773749Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 5327,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.394114239Z",
            "FinishedAt": "2026-07-24T12:15:40.67754042Z"
        },
        "Image": "sha256:3f30432ce1cb1a99947012194bdc785aa3e620847283ba074b5b63b912423234",

[
    {
        "Id": "94c960b7d3445745728ef8623d2f86e1e37372e112bb5787191b898f07674ed7",
        "Created": "2026-03-29T11:30:22.14408667Z",
        "Path": "/bin/bash",
        "Args": [
            "/entrypoint.sh"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757948,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:26.411676177Z",
            "FinishedAt": "2026-07-25T08:11:21.598329316Z",

[
    {
        "Id": "7f9359b94ed4b924db4df53faff6c11eaa72a9d625e94d5e9949f6bdd15b5df1",
        "Created": "2026-02-13T12:42:40.173731805Z",
        "Path": "docker-entrypoint.sh",
        "Args": [
            "--transaction-isolation=READ-COMMITTED",
            "--binlog-format=ROW"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 761128,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:33.396589066Z",

[
    {
        "Id": "a628a5f8406a99331a0bbc16ddcdfc9bb4e16ef057992e960e7fbd1422ecc5e5",
        "Created": "2026-02-08T03:59:19.616121286Z",
        "Path": "docker-entrypoint.sh",
        "Args": [
            "node",
            "server.js"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 760280,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:33.04470179Z",

[
    {
        "Id": "c77af0514b4b77e0ae04749b793f7c79ac3f74931d616f23f32359231f6653f4",
        "Created": "2026-01-29T14:24:33.487089654Z",
        "Path": "/entrypoint.sh",
        "Args": [
            "apache2-foreground"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 761832,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:33.613694221Z",
            "FinishedAt": "2026-07-25T08:11:21.407571357Z"

[
    {
        "Id": "906fe3093bc3f8c93b96169bd0c5c11aff445d0d747674acf2c4c781c9e640c7",
        "Created": "2026-01-13T11:38:44.833380564Z",
        "Path": "/portainer",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757877,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:26.319148124Z",
            "FinishedAt": "2026-07-25T08:11:21.536036881Z"
        },
        "Image": "sha256:2622931a6f420d9c80c84f6b17cce4b0fb5a0d67b23eb2baf44eae774ff5a9ac",

[
    {
        "Id": "266edc433d21ac0853300aa0a9292bb613f4e7f2013b11c9866fde11a318c06a",
        "Created": "2025-11-08T09:00:39.847003156Z",
        "Path": "/usr/bin/tini",
        "Args": [
            "-g",
            "--",
            "node",
            "app.js"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757752,
            "ExitCode": 0,

[
    {
        "Id": "f3feef78096e71986a0c8e90df2a7740ecbd6189b71a7d03266af72654e4e424",
        "Created": "2025-11-05T11:11:58.375965745Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 4453,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.280207489Z",
            "FinishedAt": "2026-07-24T12:15:37.166691705Z"
        },
        "Image": "sha256:c94414ec1c7fbfefb0529923603d27c7e0dd2b3e5e9a544071459cbc739bae1c",

[
    {
        "Id": "dfabc78adb12b24dbab4d03cf7efc93fac4d3c6eec7d3a4e7062e0832694fe62",
        "Created": "2025-07-04T20:41:36.823720101Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 7344,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:50.716040003Z",
            "FinishedAt": "2026-07-24T12:15:36.935270237Z"
        },
        "Image": "sha256:38ddfd1994b77bdf407996dff8aad216be35beef4f56fd7ef3618d57eb87d197",

[
    {
        "Id": "97df3db91ae62f752080bcdadb119bf8421d988c865c772a1f84cc68d780464e",
        "Created": "2025-04-26T23:19:15.365210792Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 5216,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.385242587Z",
            "FinishedAt": "2026-07-24T12:15:36.856792374Z"
        },
        "Image": "sha256:bc84c25570e376590e0d0197b5ad2ba606230200192beee21a669676e0debe4b",

[
    {
        "Id": "e6231a2d1069bd1f408c034d445a6f3b993f71ac331b740098aaa738131fca98",
        "Created": "2025-04-26T20:03:42.433204023Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 5376,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.467261893Z",
            "FinishedAt": "2026-07-24T12:15:36.914730506Z"
        },
        "Image": "sha256:8f2f140837377d99cf42660618313bf5dce149d0503215d1f4c47bef8f0c0378",

[
    {
        "Id": "7a88dfbcbf07df9c107d1105ac67f1cbbc7ba00c4db54bb9e5d40c5189b8ee65",
        "Created": "2025-03-04T04:47:00.139642133Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 5202,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.400185131Z",
            "FinishedAt": "2026-07-24T12:15:38.719843757Z"
        },
        "Image": "sha256:8a03e26f67253b48a996d0e244697c9064b5c860a5fa69827e54ac83715afd5f",

[
    {
        "Id": "790040db9af0868de228009c4bfa37ec13bddc1b4c737f880a130c6a309dfc09",
        "Created": "2025-01-11T23:19:24.24631107Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 5217,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.372082084Z",
            "FinishedAt": "2026-07-24T12:15:42.839663782Z"
        },
        "Image": "sha256:c177cbe258107a060567a964ec94d1a997d38211e63e688c6bff2708c7c564e0",

[
    {
        "Id": "590a710b4c3f08b4cadb0dc7b0976f68e83ffc7d5e2c9c63c6ed33e6e4d89b17",
        "Created": "2024-12-29T04:36:59.738467714Z",
        "Path": "/crafty/docker_launcher.sh",
        "Args": [
            "-d",
            "-i"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 759555,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-25T08:11:32.61825832Z",

[
    {
        "Id": "07ffdc3eb2041880aa08ded8988daf0dac04a5c837432f28313a7da9a05e7dc5",
        "Created": "2024-12-06T18:30:43.367745857Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 4070,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.131264449Z",
            "FinishedAt": "2026-07-24T12:15:36.202486274Z"
        },
        "Image": "sha256:e4c88bb5ec3d628d636eadca3b96d461c0122da30518088fc1d0ead754e946ec",

[
    {
        "Id": "150c9e4384497a0ddd78cb45f095c42a5ec1998eeff2242df0b5eb65b197a065",
        "Created": "2024-03-11T21:00:34.858823297Z",
        "Path": "/usr/bin/dumb-init",
        "Args": [
            "--",
            "extra/entrypoint.sh",
            "node",
            "server/server.js"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 757526,
            "ExitCode": 0,

[
    {
        "Id": "c4ba61176c1570522ceaadf0628821b9730722dc5972d59e78cf7b8b324dcaa9",
        "Created": "2024-03-10T01:48:09.542752926Z",
        "Path": "/init",
        "Args": [],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": true,
            "Dead": false,
            "Pid": 4157,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2026-07-24T14:04:49.242388474Z",
            "FinishedAt": "2026-07-24T12:15:38.649143821Z"
        },
        "Image": "sha256:2b42f2b7a2ebcd335ca3ea57f9117951e4ca244492d6b7235d3569f80cf224be",

```
</details>
