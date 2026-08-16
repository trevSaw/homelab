# technitium

## Overview
- Purpose: Primary LAN + Tailscale DNS server (recursive + authoritative + ad blocking), replacing Pi-hole
- Category: Infrastructure / Networking
- Current lifecycle state: Production (deployed 2026-08-16, Phase 19)
- Importance level: Critical

## Repository Location
- Service directory: `services/technitium/`
- Compose file: `services/technitium/compose.yaml`
- Documentation path: `Documentation/services/technitium/technitium.md`

## Runtime Information
- Container names: technitium
- Restart policy: unless-stopped
- Environment files: `.env` (gitignored, secrets), `.env.example` (template)
- Networks: default bridge (DNS is a network-edge service; no `proxy`/`hotio` membership)
- Volumes: `/mnt/monarch/appdata/technitium/{config,logs}`

## IP / Ports
| Port | Host bind | Purpose |
|---|---|---|
| `53/udp+tcp` | `192.168.50.44`, `100.102.139.115` | DNS service (LAN + Tailscale only) |
| `5380/tcp` | `192.168.50.44`, `100.102.139.115` | Web console (LAN + Tailscale only) |

No public exposure. Explicit-IP binding avoids libvirt `192.168.122.1:53` conflict and prevents a public open resolver.

## DNS Architecture
- Primary zone: `fatherfankscloud.uk` (LAN/Tailscale only; public zone stays at Cloudflare with dead `0.0.0.9` wildcard)
- Host record: `mocha.fatherfankscloud.uk` = APP record `SplitHorizon.SimpleAddress`
  - LAN clients → `192.168.50.44`
  - Tailscale clients → `100.102.139.115`
- Service hostnames: CNAME → `mocha.fatherfankscloud.uk`
- Reverse zone: `192.168.50.0/24` PTRs (.44→sso, .213→casaos, .96→P110M, .73→Trevs-iPhone, .119→MacBookPro)
- Recursion: `AllowOnlyForPrivateNetworks` (RFC1918 + CGNAT `100.64.0.0/10`)
- Forwarders (temporary): Cloudflare `1.1.1.1` + Google `8.8.8.8`, DNSSEC validation on — **confirm Pi-hole's actual upstreams before cutover**
- Blocking: `AnyAddress` (→ 0.0.0.0), lists = StevenBlack hosts, urlhaus, Disconnect tracking + ad — **confirm against Pi-hole's lists**

## Architecture Relationships
- Upstream dependencies: none (recursive + forwarders)
- Downstream consumers: LAN clients, Tailscale clients, Traefik hostname resolution
- Reverse proxy relationships: Traefik remains the only HTTP/HTTPS ingress; Technitium only resolves names

## Security Review
- Secret handling approach: admin password in gitignored `.env` (mode 600)
- Privileged mode status: not used
- Docker socket exposure: none
- External exposure: none — DNS + web bound to LAN/Tailscale IPs only
- Known risks: temporary forwarders/blocklists pending Pi-hole confirmation

## Operational Notes
- Backup considerations: config in `/mnt/monarch/appdata/technitium/config`; use web console Settings → Backup Settings + per-zone Export
- Recovery notes: restore config dir, `docker compose up -d`
- Monitoring requirements: container healthcheck (TCP :5380); query logging enabled
- Maintenance considerations: pinned `15.4.0` (see `Versions.md`); upgrade = bump tag + `docker compose up -d`

## Governance Metadata
- ADR references: []
- Migration priority: P1
- Migration wave: Phase 19

### Evidence References

Classification:
- Source: Technitium DNS Server v15.4 official Docker image

Runtime:
- Deployed 2026-08-16, healthy; split horizon verified LAN + Tailscale.

Dependencies:
- Source: audit of Pi-hole (192.168.50.213), Traefik labels, Cloudflare zone

Risks:
- Pi-hole exact upstreams/blocklists/allowlists not exported (auth-locked); documented in Phase 19.

Migration:
- Phase 19; setup reproducible via `scripts/migration/setup-technitium.sh`

ADRs:
- None identified.

## Known Issues
- `echo.fatherfankscloud.uk` intentionally not created (no running container; EchoOS compose in `needing-to-be-deleted`).
- `honcho`/`calib`/`calibre` return 404 at root path — Traefik routing is correct; backends serve on subpaths.
- Tailscale split-DNS route for `fatherfankscloud.uk` must be added in the Tailscale admin console (restricted nameserver → `100.102.139.115`).
- LAN cutover (router DHCP DNS → `192.168.50.44`) not yet performed.
