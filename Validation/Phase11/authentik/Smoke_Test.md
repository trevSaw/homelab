# Phase 11 — Authentik Smoke Test

**Timestamp:** 2026-07-30T10:41:30Z  
**Result:** PASS

## Checks

| Check | Result |
|-------|--------|
| authentik-db | healthy; mount `/mnt/monarch/appdata/authentik/db` |
| authentik-redis | healthy; mount `.../redis` |
| authentik-server | healthy (after healthcheck fix); mounts media/templates on appdata |
| authentik-worker | healthy |
| `https://sso.fatherfankscloud.uk/-/health/live/` | 200 |
| `https://sso.fatherfankscloud.uk/` | 302 → authentication flow (`x-powered-by: authentik`) |
| Startup logs | Migrations applied (none pending); gunicorn listening; outpost connected |

## Notes

- Initial Docker healthcheck used `wget` (not in image) → `unhealthy` → **Traefik filtered the container** → SSO 404.
- Fixed `services/authentic/compose.yaml` healthcheck to Python urllib probe; Traefik routing restored.
- Functional IdP state preserved (DB migrated with uid 70).
