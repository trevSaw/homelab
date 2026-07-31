# Phase 11 — Homepage Migration Report

**Service:** homepage (+ homepage-images)  
**Batch:** 01  
**Final status:** READY FOR SOAK  
**Completed:** 2026-07-30T09:29:30Z

## Summary

Homepage config and images path migrated from hive to `/mnt/monarch/appdata`. Repo compose already used `${PATH_*}`; cutover was env alignment (`PATH_CONFIG`/`PATH_DATA` → `/mnt/monarch/appdata`) plus recreate from `services/homepage`.

## Paths

| Role | Path |
|------|------|
| Config source (rollback) | `/hive/config/homepage.old` |
| Images source | `/hive/data/homepage/images` (**still present** — root-owned; rename needs sudo) |
| Old compose project (rollback) | `/hive/homepage.old` |
| Config destination | `/mnt/monarch/appdata/homepage` |
| Images destination | `/mnt/monarch/appdata/homepage/images` |
| Authoritative compose | `services/homepage/compose.yaml` |
| Env (gitignored) | `services/.env` (+ symlink `services/homepage/.env` → `../.env`) |
| Env pre-cutover backup | `Validation/Phase11/homepage/proposed/services.env.pre-cutover.bak` |

## Compose / env change

No literal volume sed in compose. Effective change:

```diff
- PATH_CONFIG=/hive/config
- PATH_DATA=/hive/data
+ PATH_CONFIG=/mnt/monarch/appdata
+ PATH_DATA=/mnt/monarch/appdata
```

Resolved mounts after cutover:

- `/mnt/monarch/appdata/homepage` → `/app/config`
- `/mnt/monarch/appdata/homepage/images` → `/app/public/images`

## Execution timeline

| Step | Result |
|------|--------|
| Dry-run homepage + homepage-images | SUCCESS (approved) |
| Create `services/.env` (hive PATH_* during copy) | SUCCESS |
| Symlink `services/homepage/.env` for interpolation | SUCCESS |
| Execute homepage `--checksum` | SUCCESS — checksum match |
| Execute homepage-images `--checksum` | SUCCESS — empty tree, checksum match |
| Cutover stop + delta rsync | SUCCESS |
| Flip PATH_* → appdata + recreate | SUCCESS — healthy |
| Rename config + `/hive/homepage` → `.old` | SUCCESS |
| Rename images → `.old` | **BLOCKED** — `Permission denied` (root:root) |

## Verification

- Config: 42KB, 3 files / 2 dirs; checksum match
- Images: empty source/dest; checksum match
- Smoke: healthy + Traefik 200 — see `Smoke_Test.md`

## Outstanding operator action

```bash
sudo mv /hive/data/homepage/images /hive/data/homepage/images.old
```

Empty unused source dir; does not affect running service. Complete when convenient during soak.

## Rollback procedure

```bash
# Restore env PATH_* to hive (or restore bak)
cp -a Validation/Phase11/homepage/proposed/services.env.pre-cutover.bak services/.env
# Ensure symlink
ln -sfn ../.env services/homepage/.env

# Restore config tree name
mv /hive/config/homepage.old /hive/config/homepage

# Optional: restore old compose project and run from there
mv /hive/homepage.old /hive/homepage
(cd /hive/homepage && docker compose up -d)

# Or from repo with hive PATH_*:
(cd services/homepage && docker compose -f compose.yaml up -d)
```

Keep `.old` artifacts ≥ **7 days**. Do not delete automatically.

## Lessons learned

1. Homepage cutover is env/`PATH_*` alignment, not compose path sed.
2. Compose `${VAR}` interpolation requires `.env` beside the compose file (or `--env-file`); `env_file:` alone is insufficient.
3. Do not pre-create companion `images/` under homepage dest before homepage verify — breaks empty-dest / count checks.
4. Root-owned empty images source needs elevated privileges to rename to `.old`.

## Final decision

**READY FOR SOAK**

Leave `/hive/config/homepage.old` and `/hive/homepage.old` untouched for a minimum of seven (7) days before cleanup. Complete images `.old` rename with sudo when available.
