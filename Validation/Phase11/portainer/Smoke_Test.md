# Phase 11 — Portainer Smoke Test

**Timestamp:** 2026-07-30T09:12:00Z  
**Result:** PASS (functional) with pre-existing healthcheck caveat

## Checks

| Check | Result |
|-------|--------|
| Container status | `running` |
| Data mount | `/mnt/monarch/appdata/portainer` → `/data` |
| Compose project file | `services/portainer/compose.yaml` |
| HTTP `:9000/api/status` | 200 — `Version=2.33.6`, InstanceID preserved |
| HTTP `:9000/api/system/status` | 200 |
| HTTPS `:9445/api/status` | 200 |
| Startup logs | Clean INF startup; no ERROR |
| Deprecated `/status` WRN | Expected (Portainer deprecation notice) |

## Docker healthcheck

Docker reports **unhealthy** because the repo healthcheck uses `CMD-SHELL` / `wget`, and `portainer/portainer-ce:lts` has no `/bin/sh`:

```text
OCI runtime exec failed: ... exec: "/bin/sh": stat /bin/sh: no such file or directory
```

This is a **pre-existing compose healthcheck incompatibility**, not a migration regression. Live hive compose had no healthcheck. Functional smoke (API/UI endpoints) passed.

## Recommendation

Track a follow-up to replace the Portainer healthcheck with a host-side or distroless-compatible probe. Do not block soak on this.
