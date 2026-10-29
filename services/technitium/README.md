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
{"private":["192.168.50.44"],"100.64.0.0/10":["100.102.139.115"],"192.168.176.1/32":["100.102.139.115"]}
```

- LAN clients → `192.168.50.44`
- Tailscale clients → `100.102.139.115`
- `192.168.176.1/32` (docker bridge gateway) → `100.102.139.115`
  - Docker's userland proxy (`docker-proxy`) rewrites the source IP of queries that
    arrive via the Tailscale listener (`100.102.139.115:53`) to the docker bridge
    gateway. Without this rule, Tailscale clients (e.g., iOS) would match the
    `private` rule and receive the LAN answer, which is unreachable off-LAN.
- Service hostnames are plain CNAMEs → `mocha.fatherfankscloud.uk`

## Authority and ACME

Technitium is authoritative only for the **internal split-horizon view**;
Cloudflare remains authoritative for public DNS. The public zone intentionally keeps
the dead `*.fatherfankscloud.uk → 0.0.0.9` wildcard and is not delegated to Technitium.

Because `DNS_SERVER_DOMAIN=dns.mocha`, Technitium auto-populates the primary zone's
apex NS and SOA with `dns.mocha`. This is **internal authority metadata, not the public
delegation**: `dns.mocha` is not a resolvable public name, and internal/public NS
records are intentionally different. Do not change the local apex NS to Cloudflare.

Traefik's `le` DNS-01 resolver must run propagation checks against the public
Cloudflare delegation, not the internal split-horizon zone.
`services/traefik/compose.yaml` therefore sets:

```yaml
dns:
  - 1.1.1.1
  - 8.8.8.8
```

Without that override, Lego follows the local apex NS to `dns.mocha`, fails to resolve
it, and certificate renewal fails even though Cloudflare holds the `_acme-challenge`
TXT record. Verified 2026-10-19: all four Traefik certificates renewed and validated
after the public-DNS override was applied.

## Blocklists / allowlists

- Block list URLs (confirmed 2026-08-16): hagezi **Pro** (`adblock/pro.txt`, AdBlock
  format — Technitium parses `||domain^`) + StevenBlack hosts (~314k domains).
  hagezi `hosts/pro.txt` is a dead path (404); `adblock/pro.txt` is the same Pro list.
- Allowlist: `hairvivi.com` (and `www.hairvivi.com`) added to the **Allowed Zone** in
  the web console (Settings/DNS → Allowed Zones or via API `/api/allowed/add`).

## Backup & restore

- Config: copy `/mnt/monarch/appdata/technitium/config`
- Restore: place files back, `docker compose restart`
- Settings export: web console → Settings → Backup Settings
- Zones export: web console → Zones → each zone → Export

## Upgrade

Bump image tag in `compose.yaml` + `Versions.md`, `docker compose up -d`.

## Known limitations / exceptions

- Upstream forwarders currently `1.1.1.1`/`8.8.8.8` (temporary) — confirm Pi-hole's actual upstreams.
- `echo.fatherfankscloud.uk` record intentionally not created (no running container).
- hagezi Pro list is aggressive (blocks ads/affiliate/tracking/malware); watch for false positives after cutover.

## Troubleshooting

- `dig @192.168.50.44 example.com`: direct query test
- `docker logs technitium`: server logs
- Web console: `http://192.168.50.44:5380/`
