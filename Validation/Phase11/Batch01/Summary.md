# Phase 11 — Batch 01 Summary

**Batch:** 01 (first live migration)  
**Branch:** `phase10.5`  
**Executed:** 2026-07-30  
**Overall status:** READY FOR 7-DAY SOAK  
**Batch 02:** Do not proceed until soak criteria are met (or operator explicitly overrides)

## Services migrated (order)

| # | Service | Final status | New path | Rollback `.old` |
|---|---------|--------------|----------|-----------------|
| 1 | Portainer | READY FOR SOAK | `/mnt/monarch/appdata/portainer` | `/hive/portainer.old` |
| 2 | Homepage (+ images) | READY FOR SOAK | `/mnt/monarch/appdata/homepage` (+ `/images`) | `/hive/config/homepage.old`, `/hive/homepage.old` |
| 3 | code-server | READY FOR SOAK | `/mnt/monarch/appdata/code-server` | `/hive/code-server.old` |

## Execution order rationale

Low-risk wave from Phase 10.5 matrix: Portainer → Homepage → code-server. Each service completed through READY FOR SOAK before the next began.

## Migration timings (approx, wall clock)

| Service | Copy size | Notes |
|---------|-----------|-------|
| Portainer | ~2.6MB | Brief; blocked initially on appdata permissions |
| Homepage | ~42KB + empty images | Env/`PATH_*` cutover |
| code-server | ~3.0GB / 41k files | Longest rsync + checksum |

## Issues encountered and resolutions

1. **`/mnt/monarch/appdata` not writable** (Portainer first execute)  
   - Resolved: ownership writable by `fatherfrank`; Batch 01 dest dirs created.

2. **Portainer Docker healthcheck unhealthy**  
   - Cause: distroless image lacks `/bin/sh` for `CMD-SHELL` wget probe.  
   - Functional API smoke passed (HTTP/HTTPS 200). Track healthcheck fix separately.

3. **Homepage compose uses `PATH_*` (no literal sed)**  
   - Cutover via gitignored `services/.env` + symlink `services/homepage/.env`.  
   - Learned: Compose interpolation needs `.env` beside compose file.

4. **Homepage images `.old` rename blocked**  
   - `/hive/data/homepage/images` is `root:root` empty dir.  
   - Operator: `sudo mv /hive/data/homepage/images /hive/data/homepage/images.old`

5. **code-server orchestrator smoke re-verify false fail**  
   - Post-copy restart on old path created `workspcae/monarch` mountpoint under source.  
   - Resolved: stop → delta rsync → checksum verify → apply compose.

6. **Always cutover-sync before apply**  
   - Orchestrator restarts on old paths when compose not yet applied; delta rsync before `--apply-compose` is required for correctness.

## Outstanding warnings

- Portainer compose healthcheck incompatible with image (pre-existing).
- Homepage images source not yet renamed to `.old` (needs sudo).
- Typo `workspcae` remains in code-server compose workspace mount (pre-existing; not changed this batch).
- Gitignored `.env` files created locally (`services/.env`, `services/code-server/.env`) — do not commit.

## Rollback summary

| Service | Helper / method |
|---------|-----------------|
| Portainer | Restore `compose.yaml.pre-migrate.bak`; `mv /hive/portainer.old /hive/portainer`; recreate |
| Homepage | Restore `services.env.pre-cutover.bak` PATH_*; restore `.old` config/project dirs |
| code-server | Restore `compose.yml.pre-migrate.bak`; `mv /hive/code-server.old /hive/code-server`; recreate |

Framework helper remains available: `./scripts/migration/rollback.sh --execute --phase-dir Validation/Phase11/<service> <key>`

## Recommended next services (after soak)

From Phase 10.5 low/medium wave (operator choice): remaining verify/already-migrated checks, then medium-risk (e.g. authentik verify, or next required=yes candidates such as calibre / ollama only with explicit window). **Do not start Batch 02 until Batch 01 soak completes unless explicitly approved.**

## Operator notes

- Soak recommendation: **≥ 7 days** before deleting any `.old` trees.
- Cleanup is **not** part of Batch 01; follow Phase 11 §11 after soak.
- Evidence roots: `Validation/Phase11/{portainer,homepage,code-server}/` and this `Batch01/` folder.
- No original data was deleted.

## Operator summary

- **Succeeded:** Portainer, Homepage, code-server — all **READY FOR SOAK**
- **Failed:** none (one transient verify fail on code-server smoke re-check, resolved before cutover)
- **Batch soak:** **Yes — ready for 7-day soak**
- **Phase 11 Batch 02:** **Do not proceed yet**
