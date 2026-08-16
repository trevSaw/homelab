# Phase 19 — DNS Record Inventory (Migration Source Data)

**Date:** 2026-08-16  
**Source:** live Pi-hole DNS enumeration (192.168.50.213), Traefik container labels, Cloudflare zone API, Tailscale status

## A. Service hostnames (all → Traefik `192.168.50.44`)

Target architecture: **service CNAME → host record** (`mocha.fatherfankscloud.uk`), host record is Split Horizon.

| # | Hostname | Type (current) | Current target | In Pi-hole today? | Verdict |
|---|---|---|---|---|---|
| 1 | `sso.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 2 | `code.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 3 | `hermes.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 4 | `homeassistant.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 5 | `home.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 6 | `jellyfin.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 7 | `jellyseerr.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 8 | `kav.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 9 | `nx.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 10 | `chat.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 11 | `sparkyfitness.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 12 | `calib.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate |
| 13 | `calibre.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | Migrate (compose defines router; calibre container not running — keep for parity) |
| 14 | `echo.fatherfankscloud.uk` | A | 192.168.50.44 | ✅ TTL0 | **FLAG** — EchoOS compose in `needing-to-be-deleted`; no running container. Candidate for review, not deletion. |
| 15 | `traefik.fatherfankscloud.uk` | A | ❌ falls to 0.0.0.9 | ❌ | **ADD** (needed; dashboard) |
| 16 | `bazarr.fatherfankscloud.uk` | A | ❌ falls to 0.0.0.9 | ❌ | **ADD** (router live) |
| 17 | `honcho.fatherfankscloud.uk` | A | ❌ falls to 0.0.0.9 | ❌ | **ADD** (router live) |
| 18 | `prowlarr.fatherfankscloud.uk` | A | ❌ falls to 0.0.0.9 | ❌ | **ADD** (router live) |
| 19 | `radarr.fatherfankscloud.uk` | A | ❌ falls to 0.0.0.9 | ❌ | **ADD** (router live) |

## B. Host records (contain addresses)

| Hostname | Type | LAN | Tailscale | Public |
|---|---|---|---|---|
| `mocha.fatherfankscloud.uk` | Host A (Split Horizon) | `192.168.50.44` | `100.102.139.115` | — (no public exposure) |
| `casaos.fatherfankscloud.uk` | Host (optional) | `192.168.50.213` | — | — **FLAG**: is CasaOS admin still needed? Keep optional. |

## C. PTR records (reverse)

| PTR | Target | Migrate? |
|---|---|---|
| `44.50.168.192.in-addr.arpa` → `sso.fatherfankscloud.uk` | — | ✅ yes |
| `213.50.168.192.in-addr.arpa` → `casaos` | Pi-hole host | Flag — Pi-hole host; keep for parity |
| `96.50.168.192.in-addr.arpa` → `P110M` | unknown LAN device | Migrate |
| `73.50.168.192.in-addr.arpa` → `Trevs-iPhone` | iPhone | Migrate |
| `119.50.168.192.in-addr.arpa` → `MacBookPro` | MacBook | Migrate |

## D. Public DNS (Cloudflare) — do not touch unless explicitly required

| Record | Value | Verdict |
|---|---|---|
| `*.fatherfankscloud.uk A 0.0.0.9` | dead placeholder | **Keep** — public access intentionally disabled |

## E. Tailscale / MagicDNS

| Item | Value |
|---|---|
| Tailscale DNS | enabled, `100.100.100.100` MagicDNS |
| Split DNS for `fatherfankscloud.uk` | **not configured** → configure to send to Technitium (`100.102.139.115`) |
| mocha tailnet name | `mocha.tail86073.ts.net` |

## F. Upstream resolvers (Pi-hole)

- **Pending admin password** to read exact upstreams. Pi-hole is a forwarding resolver.
- Candidate forwarders (to confirm): Cloudflare `1.1.1.1`, Google `8.8.8.8`, or DNS-over-TLS/HTTPS equivalents.

## G. Blocklists (Pi-hole)

- **Pending admin password** to read `adlists.list`. Pi-hole blocking confirmed active (0.0.0.0 answers).
- Known blocklist candidates to verify against Pi-hole: OISD, StevenBlack, AdGuard DNS lists.
