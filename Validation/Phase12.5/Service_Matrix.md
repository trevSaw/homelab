# Service Matrix — Phase 12.5

| Service | Platform | Phase 12 SoT? | Appdata? | proxy | hotio | Traefik | Compliance |
|---|---|---|---|---|---|---|---|
| Traefik | Core | yes | ACME | ✅ | — | self | PASS |
| Portainer | Core | yes | yes | — | — | no | PASS (exc.) |
| Beszel | Monitoring | yes | yes | — | — | no | PASS (exc.) |
| Beszel-agent | Monitoring | yes | yes | host | — | no | PASS (exc.) |
| Uptime Kuma | Monitoring | yes | yes | ✅ | — | no | PASS |
| Authentik | Core | yes | yes | ✅ | — | yes | PASS |
| qBittorrent | Media Auto | yes | yes | — | ✅ | no | PASS |
| NZBGet | Media Auto | yes | yes | — | via qbit | no | PASS (exc.) |
| Sonarr | Media Auto | yes | yes | — | — | no | PASS (exc.) host |
| Radarr | Media Auto | yes | yes | ✅ | ✅ | yes | PASS (exc. port) |
| Prowlarr | Media Auto | yes | yes | ✅ | ✅ | yes | PASS (exc. port) |
| Jellyfin | Media Cons. | yes | yes | ✅ | — | yes | PASS (exc. port) |
| Jellyseerr | Media Cons. | yes | yes | ✅ | — | yes | PASS (exc. port) |
| Bazarr | Media Cons. | yes | yes | ✅ | ✅ | yes | PASS (exc. port) |
| Lidarr | Media Cons. | no | — | — | — | — | N/A |
| Ollama/Open WebUI/Hermes/Honcho/Odysseus | AI | no | mixed | mixed | — | mixed | DEFERRED |
| Nextcloud | Cloud | no | hive | ✅ | — | yes | DEFERRED |
| Remaining CasaOS apps | Mixed | no | mixed | — | — | no | DEFERRED |
