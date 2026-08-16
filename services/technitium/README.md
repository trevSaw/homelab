# Technitium — homelab DNS server (Phase 19)

## Overview

Primary LAN + Tailscale DNS server, replacing Pi-hole. Recursive + authoritative,
with ad-blocking and split-horizon (LAN vs Tailscale) host resolution.

- Domain: `fatherfankscloud.uk` (Primary zone, served to LAN/Tailscale)
- Host record: `mocha.fatherfankscloud.uk` (Split Horizon APP record)
- Service hostnames: CNAME → `mocha.fatherfankscloud.uk`
- WAN/public exposure: **intentionally disabled** (future phase)

## Deploy

```bash
cd services/technitium
cp .env.example .env   # set strong admin password
docker compose up -d
```

## Required env

See `.env.example`.

## Storage

| Host path | Container | Notes |
|---|---|---|
| `/mnt/monarch/appdata/technitium/config` | `/etc/dns` | Config, zones, app configs |
| `/mnt/monarch/appdata/technitium/logs` | `/var/log/technitium/dns` | Query/log files |

## Ports

| Port | Host bind | Purpose |
|---|---|---|
| `53/udp+tcp` | `192.168.50.44`, `100.102.139.115` | DNS service (LAN + Tailscale only) |
| `5380/tcp` | `192.168.50.44`, `100.102.139.115` | Web console (LAN + Tailscale only) |

**Why explicit IPs and not `0.0.0.0`:** libvirt dnsmasq already binds
`192.168.122.1:53` (virbr0, DOWN); a wildcard `53` publish would conflict. Binding
only LAN + Tailscale IPs also guarantees DNS cannot become a public open resolver.

## Split Horizon

The `mocha` host record is an APP record using `SplitHorizon.SimpleAddress`:

```json
{"private":["192.168.50.44"],"100.64.0.0/10":["100.102.139.115"]}
```

- LAN clients → `192.168.50.44`
- Tailscale clients → `100.102.139.115`
- Service hostnames are plain CNAMEs → `mocha.fatherfankscloud.uk`

## Backup & restore

- Config: copy `/mnt/monarch/appdata/technitium/config`
- Restore: place files back, `docker compose restart`
- Settings export: web console → Settings → Backup Settings
- Zones export: web console → Zones → each zone → Export

## Upgrade

Bump image tag in `compose.yaml` + `Versions.md`, `docker compose up -d`.

## Known limitations / exceptions

- Blocklist URLs + final upstream forwarders require Pi-hole admin access to
  confirm; temporary documented values are used for validation.
- `echo.fatherfankscloud.uk` record intentionally not created (no running container).

## Troubleshooting

- `dig @192.168.50.44 example.com`: direct query test
- `docker logs technitium`: server logs
- Web console: `http://192.168.50.44:5380/`
