# Energy Audit v1.0

## Purpose
`energy_audit.sh` is a **read‑only** Bash script that inspects a Homelab Governance repository and produces a single Markdown report summarizing the system’s current energy‑consumption characteristics and offering practical, prioritized recommendations to reduce idle and average power usage.

## Requirements
- **Platform:** Ubuntu Server 24.04 LTS (or any recent Linux distro)  
- **Tools:** `git`, `docker`, `zpool`/`zfs` (optional), `lsblk`, `smartctl`, `mpstat`, `vmstat`, `vainfo` (optional), `intel_gpu_top` (optional), `lspci`, `findmnt`.  
- No elevated privileges are required; the script never modifies configuration, restarts services, or changes kernel parameters.

## Usage
```bash
# Clone the repository (if not already)
git clone https://github.com/your-org/homelab-governance.git
cd homelab-governance

# Make the script executable (once)
chmod +x scripts/audit/energy_audit.sh

# Run the audit (read‑only)
./scripts/audit/energy_audit.sh
```

The script will:
1. Detect the Git repository root (or fall back to the current directory).  
2. Gather information about the system, CPU, memory, GPU, storage, ZFS (if present), Docker containers, and monitoring stack.  
3. Analyse the data and generate **one** Markdown report in  
   ```
   <repo_root>/Validation/Energy/Energy_Audit_<YYYY-MM-DD_HH-MM>.md
   ```  
   A symlink/ copy named `Latest_Energy_Audit.md` always points to the newest report.

## Output Example
A sample report can be found at `scripts/audit/sample_energy_report.md`. The real report contains live data from your host.

## Known Limitations
- The script only *reads* system state; it cannot modify CPU governors, ZFS properties, Docker configurations, or any other setting.  
- Power‑usage numbers are **estimated** based on heuristics; actual wattage will vary per hardware.  
- If required commands are missing, the script notes the omission and continues gracefully.  
- No JSON or historical data export is provided in v1.0.

## Future Enhancements (out of scope for v1.0)
- Export data in JSON for downstream processing.  
- Historical trend analysis across multiple audit runs.  
- Integration with an AI model to automatically generate custom recommendations.  
- Automated alerting when energy‑inefficient configurations are detected.  
- Support for additional platforms (e.g., Debian, Rocky Linux).  

---

*The script is deliberately modular so that future versions can expand without breaking the current interface.*