# readarr

Phase 10.75 repository import of the live deployment.

## Purpose
Book manager (Readarr develop)

## Lifecycle
State: **Deprecated** — Readarr was retired upstream (June 2025); its metadata
servers are dead and it can no longer reliably search/match books. Container is
stopped. **Do not start.** Replaced by `services/chaptarr` (see ADR-0009).

## Runtime
- Container(s): `readarr` (stopped)
- Compose: `services/readarr/compose.yaml`
- Former source of truth: Portainer/hive compose (see Diff.md)

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.
Legacy `/books` mount points at the stale, empty path
`/hive/cloud/data/fatherfranku/files/Kavita/Books`; eBooks now live at
`/hive/library/Kavita/Books`.

## Operations
```bash
cd services/readarr
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not start. Retired upstream; use services/chaptarr.
```

## Documentation
See `Documentation/services/readarr/`.
