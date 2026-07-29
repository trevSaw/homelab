# Phase 10 Remaining Risks

## Deferred by design (out of scoped Phase 10)

| Risk / Item | Why deferred | Suggested next phase |
|-------------|--------------|----------------------|
| Storage modernization / bind-mount moves | Would migrate live data | Phase 11+ with explicit migration plan |
| Networking topology / remove host ports | Could break LAN clients (Jellyfin, n8n, Beszel, Portainer, CosmoOS, Hotio) | Phase 11 after inventory of consumers |
| Image tag pinning (`:latest`) | Behavior/version drift risk if pinned wrong | Controlled upgrade waves |
| Full DockerStandard directory layout (`compose/<domain>/`) | Rename/move = operational disruption | Dedicated migration phase |
| Reduce privileged CosmoOS / Hotio NET_ADMIN | Required by current app design | ADR + alternative design |
| Phase 9.4 F10-1 … F10-6 | Governance metadata enrichment, not runtime | Phase 11 docs/governance |

## Known limitations from Phase 10 changes

| Item | Severity | Notes |
|------|----------|-------|
| Secrets still in Git history | High | Removing from HEAD is not enough — rotate on mocha |
| `.env` required before recreate | High | Stacks fail to interpolate without local `.env` |
| Healthcheck tool assumptions | Medium | Images without `curl`/`wget` may show `unhealthy` |
| Memory limits | Medium | Generous limits; under host pressure Docker OOM may kill containers |
| beszel-agent / hermes / code-server / calibre / CosmoOS healthchecks | Low | Deferred where not obvious/safe |
| Traefik `--ping=true` | Low | New flag; should be harmless; verify dashboard still works |
| EchoOS `echoos_net` name declaration | Low | Aligns compose with named network; confirm on host if stack is live |

## Compatibility notes

- Hotio VPN stack and NZBget `network_mode: container:qbittorrent` unchanged
- Authentic worker still mounts Docker socket (pre-existing)
- Portainer still publishes 9000/9445
- CosmoOS remains privileged with host mounts

## Recommended follow-ups (not claimed complete)

1. Rotate all Phase 10-extracted secrets
2. Live `docker compose up -d` validation per stack on mocha during a maintenance window
3. Confirm healthcheck status with `docker ps` after recreate
4. Pin critical images after soak testing
5. Resolve duplicate Governance Metadata (F10-1) in service docs
