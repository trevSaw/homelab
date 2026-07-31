# Phase 11 — code-server Smoke Test

**Timestamp:** 2026-07-30T09:37:30Z  
**Result:** PASS

## Checks

| Check | Result |
|-------|--------|
| Container status | `running` |
| Config mount | `/mnt/monarch/appdata/code-server` → `/config` |
| Workspace RO mounts | `/hive` → `/config/workspace/hive`; `/mnt/monarch/appdata` → `/config/workspcae/monarch` |
| Compose project | `services/code-server/compose.yml` |
| Startup logs | code-server 4.128.0 listening on `:8443`; auth enabled via `$PASSWORD` |
| Traefik `https://code.fatherfankscloud.uk/` | 302 (login redirect — expected) |

## Notes

- No Docker healthcheck defined for this service (`Health=n/a`) — functional smoke used instead.
- Orchestrator smoke re-verify after post-copy hive restart initially failed: new `workspcae/monarch` mountpoint dir appeared on source. Resolved by stop + delta rsync + checksum re-verify while stopped before apply.
