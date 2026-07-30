# Phase 10.75 — Missing / Skipped Services

## Sonarr — intentionally skipped

- **Status:** No `sonarr` container exists on the host (`docker ps -a` empty for sonarr).  
- **Hive remnant:** `/hive/Hotio/sonarr` directory exists historically but is not a live deployment.  
- **Action:** Do not invent a compose import. If Sonarr is desired later, deploy fresh under `services/sonarr/` in a future phase.

## Stale CasaOS app directories (not running)

These exist under `/var/lib/casaos/apps/` but have no matching running container sourced from them (or were superseded):

Examples observed: `adoring_davide`, `dockersocket`, `empowering_max`, `energetic_raphael`, `epic_michelle`, `festive_eric`, `jubilant_tyler`, `marvelous_jesus`, `peaceful_danilo`, `successful_edwin`, `wireguard`, `linuxserver-qdirstat`, `open-webui`, `portainer`, `nextcloud`, `nextcloud-app-1`, `kavita` (stale vs hive compose).

**Action:** Cleanup/retirement of unused CasaOS app definitions is operator-led and out of Phase 10.75 import scope.

## Out of scope by design

- Storage migration to `/mnt/monarch/appdata`  
- Traefik/governance modernization for imported *arr apps  
- Recreating containers to cut over from CasaOS to repo compose
