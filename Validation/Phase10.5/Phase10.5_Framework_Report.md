# Phase 10.5 — Framework Report (hardened after mocha dry-run)

**Branch:** `phase10.5`  
**Host dry-run:** mocha · 2026-07-30  
**Live migrations executed:** **none**

## Verdict

Phase 10.5 remains a **framework-only** deliverable. The first live-host dry-run drove hardening: quieter output, classified compose errors, operator summaries, Portainer/homepage/NZBget accuracy, safer inventory stats, richer JSON.

## Improvements in this hardening pass

1. **Silent abort fixed** — `find` permission denied no longer kills inventory/preflight via pipefail  
2. **Operator summary block** on every major script  
3. **Compose failure classification** (env / secrets / network / file / syntax)  
4. **rsync excludes** column in `services.conf` (NZBget downloads + logs; Portainer unreadable dirs)  
5. **Homepage live drift** recorded — migrate `/hive/config` + `/hive/data` paths  
6. **Quiet dry-run rsync** (`--info=stats2`, no file flood)  
7. **JSON schema** expanded (timestamp, phase, dry_run, warnings[], errors[], …)  
8. **Expected-warning messaging** (git dirty, dry-run pending verify, shared sock, non-empty verify targets)  
9. **Preflight** clearer: commands, mounts, migratable size estimate, ownership  
10. **Docs** updated with assumptions, limitations, prerequisites  

## Policy (final)

- Config → `/mnt/monarch/appdata`
- Large datasets → `/hive`
- **Ollama exception:** config + models → `/mnt/monarch/appdata/ollama` (edit `services.conf` to relocate later)

## Remaining known limitations

- Homepage needs two migration keys + compose/env realignment after copy  
- NZBget app-internal paths must be confirmed after excluded copy  
- Authentik may not be running from repo compose on mocha yet  
- `docker compose config` still needs real `.env` before execute/apply  
- Untracked Kavita/Nextcloud remain blocked until `services/` compose exists  
- Size estimates with excludes are approximate  

## Recommendations before Phase 11 (live migration)

1. Commit Phase 10.5 framework on `phase10.5` after review  
2. Create missing `.env` files from `.env.example`  
3. Dry-run again: `code-server`, then `portainer`, then `homepage` + `homepage-images`  
4. Confirm NZBget excludes leave downloads on hive; check free space for ollama (~64GB+)  
5. Migrate **one** low-risk service first (portainer or code-server) with `--execute` but **without** `--apply-compose`, smoke, then apply  
6. Never delete `.old` until ≥7 day soak  

## Explicit non-goals (still)

No Traefik/network redesign, no media/books/Nextcloud-data moves, no host-port removal, no live execute in this hardening pass.
