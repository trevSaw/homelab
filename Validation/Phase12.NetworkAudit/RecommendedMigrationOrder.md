# Recommended Migration Order — Media Network Compliance

**Date:** 2026-07-31  
**Intent:** Planning only — **do not execute** as part of this audit.

Order minimizes blast radius: fix broken automation first, then dual-home *arr, then ingress, then request UI, then VPN/DNS hard problems.

---

## 0. Immediate hygiene (no network redesign)

| Item | Why | Risk | Suggested work | Est. downtime | Rollback |
|---|---|---|---|---|---|
| **Radarr download-client hosts** | Clients point at Radarr’s own IP `172.27.0.7` instead of qBittorrent `172.27.0.4` / DNS names — grabs/imports unreliable | **High** | In Radarr UI (or DB with backup): set hosts to `qbittorrent` (and `qbittorrent` for NZB port while shared netns) or correct IP; test both clients | ~5–15 min | Revert host fields from backup / UI history |

Do this before investing in Traefik for Radarr.

---

## 1. Dual-home *arr already on `hotio` (add `proxy` + Traefik)

| Service | Why differs | Risk | Suggested migration | Est. downtime | Rollback complexity |
|---|---|---|---|---|---|
| **Prowlarr** | On `hotio` only; host `:9696`; no Traefik; CasaOS compose / `/DATA` config | Medium | Attach `proxy`; add Traefik labels (`traefik.docker.network=proxy`); verify `https://prowlarr.<domain>`; then unpublish `9696` | 5–15 min | Detach `proxy`, restore port publish; low |
| **Radarr** | Missing `proxy`; host `:7878`; CasaOS + `/DATA` appdata; client host bug | Medium–High | After client fix: attach `proxy` + Traefik; optional Phase 12 SoT/appdata move as separate change | 10–30 min (network-only shorter) | Detach `proxy` / restore ports; medium if appdata moved |
| **Bazarr** | Missing `proxy`; host `:6767`; CasaOS | Medium | Same dual-home + Traefik pattern; confirm it can still reach Sonarr/Radarr on `hotio` | 5–15 min | Low |

---

## 2. Sonarr — leave host networking

| Service | Why differs | Risk | Suggested migration | Est. downtime | Rollback complexity |
|---|---|---|---|---|---|
| **Sonarr** | `network_mode: host`; `localhost` download clients; no Traefik; not on `proxy`/`hotio` | Medium (cutover) | 1) Attach `proxy`+`hotio` in compose (drop host mode) 2) Change clients to `qbittorrent:8080` and `qbittorrent:6789` (NZB shared netns) 3) Traefik router 4) Validate 214 series + client tests | 15–45 min | **Low–medium** — Phase 12.2B backup + known host-mode rollback path |

Depends on qBittorrent staying healthy on `hotio` (already PASS).

---

## 3. Jellyfin — Traefik-only hardening

| Service | Why differs | Risk | Suggested migration | Est. downtime | Rollback complexity |
|---|---|---|---|---|---|
| **Jellyfin** | Already `proxy` + Traefik, but still publishes `:8096` | Low | Remove host port publish after confirming clients use hostname only | &lt;5 min | Re-add port mapping; low |

Network membership already PASS/aligned.

---

## 4. Jellyseerr (Overseerr role)

| Service | Why differs | Risk | Suggested migration | Est. downtime | Rollback complexity |
|---|---|---|---|---|---|
| **Jellyseerr** | On `hotio` + `jellyfin_default`; expected **proxy-only**; no Traefik; host `:5055` | Medium | Move to `proxy`; add Traefik; point app at Jellyfin/Sonarr/Radarr via Traefik URLs or documented DNS; drop extra networks unless exception filed | 15–30 min | Reattach prior networks + port; medium |

---

## 5. NZBGet first-class DNS (deferred hard problem)

| Service | Why differs | Risk | Suggested migration | Est. downtime | Rollback complexity |
|---|---|---|---|---|---|
| **NZBGet** | `network_mode: container:qbittorrent` — VPN share; no `nzbget` DNS name | High if done wrong | Dedicated design: keep VPN egress **and** join `hotio` with name `nzbget`, **or** permanently document `qbittorrent:6789` as the automation endpoint | 30–90 min+ | **High** — VPN/connectivity regressions |

Do not fold into a casual *arr Traefik change.

---

## 6. Optional / out of canonical table

| Service | Note |
|---|---|
| Readarr | On `hotio`; not in membership standard — decide later (dual-home vs retire) |
| Byparr | Automation helper on `hotio` — acceptable; document if kept |
| Lidarr / Overseerr | Deploy greenfield to canonical networks only |

---

## Suggested sequence (summary)

1. Fix **Radarr** download-client endpoints  
2. Dual-home + Traefik: **Prowlarr → Radarr → Bazarr**  
3. Re-home **Sonarr** off host networking  
4. Remove redundant **Jellyfin** host port  
5. Re-home **Jellyseerr** to `proxy`  
6. Plan **NZBGet** DNS/VPN redesign separately  

No step in this document was executed during the audit.
