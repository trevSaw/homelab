# Incident Report — Host Reboot Loop & Wings/AMP Service Crash Loop

- **Date:** 2026-10-07
- **Host:** `mocha` (Ubuntu 22.04.5, kernel `6.8.0-138-generic`, Intel i5-11400, NVIDIA T400 4GB)
- **Status:** Service loop resolved; host reset cause mitigated (monitoring added)
- **Related:** Phase 19 (Technitium DNS migration)

---

## 1. Summary

Two distinct problems were conflated as one "crash loop":

1. **A service crash loop** — `wings.service` (Pterodactyl) was restarting every ~30s (restart counter reached **1681**), alongside failing AMP (`amptasks`/`ampfirewall`) timers. This is what was visibly "looping".
2. **Unclean host reboots** — the machine reset repeatedly (Oct 6–7) with **no clean-shutdown records**. These are consistent with hard resets (power/hardware), not a software reboot.

A system-wide DNS outage (systemd-resolved / Technitium migration) was the trigger for the wings loop.

---

## 2. Timeline (observed boots)

```
Oct 06 12:24, 13:18, 16:24, 16:44, 20:04, 21:05, 21:28, 21:41, 22:00, 22:15
Oct 07 12:15, 12:18, 12:23, 12:27  (short ~2–3 min runtimes)
```

- `Oct 06 12:22:13` — `igc 0000:06:00.0 enp6s0: NETDEV WATCHDOG: transmit queue 0 timed out 5721 ms` (2 min before a reboot).
- `Oct 07 12:44:15` — wings/AMP units stopped and removed (loop ends).
- Stable since `Oct 07 12:27` boot.

---

## 3. Findings

### 3.1 Service crash loop (root cause: DNS + unit misconfiguration)

- `wings.service` exited `status=1` because it could not reach its panel API:
  `Get "https://ptero.fatherfankscloud.uk/api/remote/servers...": dial tcp: lookup ... on 127.0.0.53:53: no such host`.
- `Restart=on-failure` relaunched it endlessly. The rate limits (`StartLimitInterval=180`, `StartLimitBurst=30`) were placed in `[Service]` instead of `[Unit]`, so modern systemd **ignored** them → unbounded restarts.
- `amptasks.timer` (every 1 min) and `ampfirewall.timer` (every 5 min) fired continuously and failed (`DOTNET_BUNDLE_EXTRACT_BASE_DIR` / `/home/amp` missing).
- DNS was failing system-wide: `ntpd`, `dockerd` (ACME), and `playitd` all logged resolution timeouts against `127.0.0.53`. Tied to the Phase 19 Technitium DNS cutover.

### 3.2 Host reboots (unclean / hardware-level)

Evidence the reboots were **not** software-initiated:

- **No clean shutdown anywhere** — no `systemd-shutdown`, `Shutting down`, `Reached target Shutdown`, or `Powering off` entries for any of the resets. Journal/kernel logs end mid-stream.
- **No kernel panic/oops, no OOM, no lockups** logged.
- **`BERT: [Hardware Error]: Total records found: 1`** on every boot — firmware's Boot Error Record Table holds a hardware fault from the prior boot.
- **No hardware watchdog** (`/dev/watchdog` absent, `/sys/class/watchdog/` empty) and no userspace watchdog → not watchdog-triggered.
- **No auto-reboot config**: `unattended-upgrades` `Automatic-Reboot "false"`; no cron/at/systemd-timer/script issuing reboot.
- **Storage healthy**: all 5 disks SMART PASSED; ZFS pool `hive` ONLINE, 0 errors; no I/O/EXT4/ZFS errors.
- **No UPS** present, so power-loss events go unrecorded.

**Assessment:** resets are consistent with **power/PSU or hardware fault** (BERT), possibly aggravated by the flaky Intel `igc` 2.5GbE NIC (fw `1057:8754`). No server BMC available (consumer hardware).

### 3.3 `llama-server` at ~590% CPU (by configuration, not a fault)

- Runs in the `ollama` container: `qwen3:8b` (6.7 GB), context 16384.
- Compose sets `CUDA_VISIBLE_DEVICES: ${CUDA_VISIBLE_DEVICES:--1}` → resolves to **`-1` = GPU disabled**; `ollama ps` shows `100% CPU`, logs `reason=cpu`.
- `n_threads = 6` on a 12-core CPU ⇒ ~600%. Request was a 22,613-token prompt truncated to 16,384, processed at ~18–34 tok/s on CPU.
- The T400 (4 GB) cannot hold the 6.7 GB model, hence CPU-only.

### 3.4 APT warnings (cleanup)

Stale/expired repo entries caused `apt update` warnings — unrelated to reboots.

---

## 4. Actions Taken

### 4.1 Removed Pterodactyl Wings + CubeCoders AMP

```bash
sudo systemctl stop   wings.service ampinstmgr.service amptasks.service amptasks.timer ampfirewall.service ampfirewall.timer
sudo systemctl disable wings.service ampinstmgr.service amptasks.service amptasks.timer ampfirewall.service ampfirewall.timer
sudo rm -f /etc/systemd/system/{wings.service,ampinstmgr.service,amptasks.service,amptasks.timer,ampfirewall.service,ampfirewall.timer}
sudo systemctl daemon-reload && sudo systemctl reset-failed

# purge package (maintainer scripts patched to no-op first, since /opt/cubecoders was removed)
sudo dpkg --purge ampinstmgr

# purge files / users
sudo rm -f /usr/local/bin/wings
sudo rm -rf /etc/pterodactyl /opt/cubecoders /var/run/wings /var/log/wings /home/amp
sudo userdel amp; sudo userdel pterodactyl
```

### 4.2 APT cleanup

```bash
sudo rm -f /etc/apt/sources.list.d/mariadb.list.old_1          # invalid filename extension
sudo apt-get purge -y ampinstmgr                               # orphan package
sudo rm -f /etc/apt/sources.list.d/repo.cubecoders.com.list /usr/share/keyrings/repo.cubecoders.com.gpg
curl -sL https://repo.chia.net/FD39E6D3.pubkey.asc | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/chia.gpg
sudo sed -i '/maxscale\/latest\/apt/s/^/#/' /etc/apt/sources.list.d/mariadb.list   # MaxScale not installed
sudo gpg --batch --yes --no-default-keyring --keyring /etc/apt/trusted.gpg \
  --export 2009837CBFFD68F45BC180471F4F90DE2A9B4BF8 | sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/sonarr.gpg
sudo sed -i 's|^deb |deb [signed-by=/etc/apt/keyrings/sonarr.gpg] |' /etc/apt/sources.list.d/sonarr.list
```

### 4.3 Hardware error monitoring

```bash
sudo apt-get install -y rasdaemon
sudo systemctl enable --now rasdaemon
```

`rasdaemon` now records MCE / PCIe AER / EDAC / extlog events to `/var/lib/rasdaemon/ras-mc_event.db`.

---

## 5. Verification

- `systemctl list-unit-files | grep -Ei 'amp|wings'` → no units.
- `systemctl --failed` → empty.
- `apt-get update` → **no warnings/errors**; `dpkg --audit` clean.
- Host stable since the `12:27` boot; all Docker services up and healthy.

---

## 6. Follow-ups / Recommendations (consumer-hardware friendly)

| Priority | Action | Notes |
|---|---|---|
| High | Add a consumer UPS (APC/CyberPower 600–650VA, USB) + NUT/`apcupsd` | Only way to confirm/deny power-loss resets; no UPS today |
| High | Check `rasdaemon` after the next event | `sudo ras-mc-ctl --summary` / `--errors` should decode the BERT/MCE cause |
| Medium | Update motherboard BIOS/UEFI | Frequently fixes Intel `igc` (I225/I226) TX hangs |
| Medium | Run Memtest86+ overnight | Rule out RAM faults behind BERT resets |
| Low | Optional mainline kernel | Test `igc` behavior; current 6.8 is newest HWE in Ubuntu repos |
| Low | `kdump-tools` | Likely won't catch these resets (no panic), lower value |

### How to check for hardware errors going forward

```bash
sudo ras-mc-ctl --summary
sudo ras-mc-ctl --errors
sudo journalctl -u rasdaemon -e
```

---

## 7. Quick Reference — Diagnosing a "reboot loop"

```bash
last -x reboot | head                       # boot history / runlevels
journalctl --list-boots                     # persistent boot list
sudo journalctl -b -1 --no-pager | tail     # end of previous boot
journalctl -b -1 | grep -iE "systemd-shutdown|Shutting down|Reached target (Reboot|Shutdown)|Kernel panic|oom"
dmesg -T | grep -iE "BERT|Hardware Error|MCE|NETDEV WATCHDOG|igc"
docker inspect $(docker ps -aq) --format '{{.Name}} restarts={{.RestartCount}}' | sort
systemctl --failed
```

Rules of thumb:
- Clean shutdown markers present → someone/something issued a reboot.
- Logs end abruptly + no shutdown markers + `BERT` → power/hardware reset.
- `NETDEV WATCHDOG` / `igc` timeouts → flaky Intel 2.5GbE NIC, check BIOS/kernel.
- Service "loops" (high `RestartCount`) are separate from host reboots.
