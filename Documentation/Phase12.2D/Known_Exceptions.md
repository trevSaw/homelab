# Phase 12.2D Known Exceptions

| Exception | Reason | Risk | Mitigation |
|---|---|---|---|
| Sonarr app URLs use host LAN `192.168.50.44` | Sonarr still `network_mode: host` | Low | Keep until Sonarr dual-home; then switch to Docker DNS |
| Host port `9696` still published | Transitional with Traefik | Low | Remove after hostname confirmed |
| Legacy `/DATA/AppData/config` left in place | Rollback / forensics | Low | Not mounted after cutover |
| Former CasaOS generic path `/DATA/AppData/config` | Historical | Low | Appdata now service-specific |
