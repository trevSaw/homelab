# Energy Audit v1.4

## Purpose
`energy_audit.sh` is a **read-only** Bash script that inspects the host running this personal Homelab repository and produces a single Markdown report summarizing energy-related characteristics with prioritized recommendations.

## Requirements
- **Platform:** Ubuntu Server 22.04 / 24.04 LTS (or any recent Linux distro)
- **Tools:** `git`, `docker`, `jq` (for Docker section), `zpool`/`zfs` (optional), `lsblk`, `smartctl`, `mpstat`, `vmstat`, `vainfo` (optional), `intel_gpu_top` (optional), `lspci`, `findmnt`
- No elevated privileges are required for core reporting; the script never modifies configuration, restarts services, or changes kernel parameters

## Usage
```bash
cd /path/to/homelab
chmod +x Scripts/audit/energy_audit.sh   # once
./Scripts/audit/energy_audit.sh
```

Optional tuning via environment variables:

| Variable | Default | Meaning |
|----------|---------|---------|
| `DOCKER_SAMPLE_COUNT` | `3` | Number of `docker stats` samples |
| `DOCKER_SAMPLE_INTERVAL` | `3` | Seconds between samples |
| `IDLE_MEM_PCT` | `5.0` | Mem% threshold for excessive idle memory |
| `IDLE_MEM_CPU_PCT` | `1.0` | Max CPU% to treat a container as idle |

## Output
1. Detects the Git repository root (or falls back to the current directory)
2. Gathers CPU, memory, GPU, storage, ZFS, Docker, and monitoring signals
3. Writes one Markdown report to:
   ```
   <repo_root>/Validation/Energy/Energy_Audit_<YYYY-MM-DD_HH-MM>.md
   ```
4. Copies/overwrites `Validation/Energy/Latest_Energy_Audit.md`

## Report sections (v1.4)
- Executive Summary (score, letter grade, score factors, measured package power, improvement areas, top recommendations)
- Healthy Configuration
- Dependency Status, System Summary, CPU, Measured Power, Memory, GPU/Quick Sync, Storage, ZFS
- Docker inventory with Mem Usage / Mem Limit (`Unlimited` when no Docker memory limit is set)
- Highest Idle CPU Consumers / Highest Memory Consumers / Excessive Idle Memory
- Relative Continuous Power Ranking
- Recommendations (including idle CPU and idle memory reviews)
- Quick Wins / Medium Effort / Long Term (derived from live findings)
- Appendix

## Output Example
See `Scripts/audit/sample_energy_report.md` for a representative v1.4-shaped sample.

## Known Limitations
- Read-only: cannot change governors, ZFS properties, Docker configs, or kernel parameters
- Power numbers are estimated/heuristic unless RAPL/turbostat package power is available
- Missing optional commands are noted; the script continues
- No JSON export or historical trend analysis in v1.4

## Related
- Validation artefacts: `Validation/Energy/`
- Repository validation: `Scripts/validate.sh`

---

*Version 1.4 — Homelab Governance Phase 10*
