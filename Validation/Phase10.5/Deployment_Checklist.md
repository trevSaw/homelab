# Phase 10.5 — Deployment Checklist

Use this when you are ready to migrate **one service** on mocha.  
Phase 10.5 itself does **not** run these execute steps.

## Global (once)

- [ ] On branch `phase10.5` (or merged equivalent) on mocha checkout
- [ ] `Services/.env` has `PATH_DATA=/mnt/monarch/appdata` and `PATH_CONFIG=/mnt/monarch/appdata`
- [ ] `/mnt/monarch` mounted; `/mnt/monarch/appdata` exists
- [ ] `rsync` installed; Docker + Compose healthy
- [ ] `zpool status -x` healthy
- [ ] Read [Migration_Matrix.md](Migration_Matrix.md) and pick **one** service
- [ ] Confirm the service is **not** a keep-on-hive dataset (media/downloads/books) — except **Ollama models**, which intentionally move
- [ ] For NZBget: confirm rsync excludes leave `config/downloads` and logs on hive
- [ ] For homepage: migrate `homepage` **and** `homepage-images`, then align PATH_*/compose
- [ ] For Portainer: source `/hive/portainer` is correct (~815K); expect permission warnings on compose/49|50

## Per service

Service: _______________

### Offline / dry-run

- [ ] `./scripts/migration/inventory.sh <service>`
- [ ] `./scripts/migration/preflight.sh --dry-run <service>`
- [ ] `./scripts/migration/run-migration.sh --dry-run <service>`
- [ ] Review `Validation/Phase10.5/logs/<service>.log`
- [ ] Review `Validation/Phase10.5/proposed/<service>/compose.diff` (if any)
- [ ] `./scripts/migration/compose-path-check.sh`

### Execute copy (still no compose apply)

- [ ] Maintenance window noted
- [ ] `./scripts/migration/run-migration.sh --execute <service>`
- [ ] Confirm inspect snapshots under `Validation/Phase10.5/inspect/`
- [ ] Confirm verify JSON `status=SUCCESS` under `reports/verify-<service>.json`
- [ ] Smoke: container up, logs clean, UI reachable, expected settings present

### Apply compose (explicit)

- [ ] Review proposed diff again
- [ ] `./scripts/migration/update-compose.sh --execute --apply-compose <service>`  
  (or re-run orchestrator with `--execute --apply-compose`)
- [ ] `docker compose config` succeeded before and after (script-enforced)
- [ ] Service healthy after recreate/start

### Soak / retire source

- [ ] Run ≥ **7 days** without rollback
- [ ] Manually rename source to `*.old` (example: `mv /hive/code-server /hive/code-server.old`) — **not** automated
- [ ] Deletion of `*.old` only after you decide — **never** scripted

### Rollback (if needed)

- [ ] `./scripts/migration/rollback.sh --execute <service>`
- [ ] Confirm previous compose + data path restored
- [ ] Re-check UI / dependent routes (Traefik)

## Forbidden during any migration

- [ ] Do not `docker compose down` unrelated stacks
- [ ] Do not move `/hive/jellyfin/{tv,movie}`, `/hive/downloads`, `/hive/library`, Nextcloud data
- [ ] Ollama **is** allowed to move `/hive/ollama` → `/mnt/monarch/appdata/ollama` (config + models)
- [ ] Do not `rm -rf` old data
- [ ] Do not apply compose before verify SUCCESS
