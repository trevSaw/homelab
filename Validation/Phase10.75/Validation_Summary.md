# Phase 10.75 — Validation Summary

**Date:** 2026-07-30  
**Rule:** Do not recreate containers; validate repository compose against live deployment.

## Compose parse

| Service | `docker compose config` |
|---|---|
| prowlarr | PASS |
| radarr | PASS |
| jellyseerr | PASS |
| bazarr | PASS |
| actual | PASS |
| lazylibrarian | PASS |
| crafty | PASS |
| mariadb | PASS (with `--env-file .env.example`; `.env` optional via `required: false`) |
| uptime-kuma | PASS |
| byparr | PASS |
| readarr | PASS |
| kavita | PASS |
| nextcloud | PASS (with `--env-file .env.example`; `.env` optional) |

## Bind-mount parity (live inspect vs repo compose)

| Service | Result |
|---|---|
| prowlarr | MATCH |
| radarr | MATCH |
| jellyseerr | MATCH |
| bazarr | MATCH |
| actual | MATCH |
| lazylibrarian | MATCH |
| crafty | MATCH |
| mariadb | MATCH |
| uptime-kuma | MATCH |
| byparr | MATCH (no mounts) |
| readarr | MATCH |
| kavita | MATCH |
| nextcloud app | MATCH |
| nextcloud-db | MATCH |

## Reachability (existing live containers)

| Endpoint | Result |
|---|---|
| `http://127.0.0.1:9696/` (prowlarr) | 200 |
| `http://127.0.0.1:7878/` (radarr) | 200 |
| `http://127.0.0.1:5055/` (jellyseerr) | 307 |
| `http://127.0.0.1:6767/` (bazarr) | 200 |
| `http://127.0.0.1:5006/` (actual) | 200 |
| `http://127.0.0.1:5299/` (lazylibrarian) | 303 |
| `http://127.0.0.1:3001/` (uptime-kuma) | 302 |
| `http://127.0.0.1:8787/` (readarr) | 200 |
| `https://127.0.0.1:8443/` (crafty) | 302 |
| `https://kav.fatherfankscloud.uk/` | 200 |
| `https://nx.fatherfankscloud.uk/` | 302 |
| byparr on `hotio_default:8191` | 301 |
| mariadb host `3308` | open |

## Environment resolution

- Services without secrets: compose self-contained.  
- `mariadb` / `nextcloud`: variables via `.env.example` placeholders; local `.env` gitignored; compose uses `env_file.required: false`.

## Cutover status

Repository compose matches live mounts/images for imported services. Containers **continue** to run under prior CasaOS/Portainer/hive projects until an explicit cutover.
