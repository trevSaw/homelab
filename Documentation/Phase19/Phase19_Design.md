# Phase 19 — Technitium Deployment Design

**Date:** 2026-08-16  
**Status:** Design (approved direction)  
**Decision:** Option (a) — LAN + Tailscale now; WAN/DDNS/public-DNS is a documented future phase.

## 1. Target architecture (this phase)

```text
service.fatherfankscloud.uk
        CNAME
             ↓
mocha.fatherfankscloud.uk  (host record, Split Horizon APP)
        Split Horizon
       ↙      ↓
    LAN    Tailscale
192.168.50.44  100.102.139.115
```

- WAN keeps the existing behavior: public zone `*.fatherfankscloud.uk → 0.0.0.9` (dead placeholder) untouched. **No public DNS changes, no DDNS, no NAT changes, no public exposure of Technitium.**
- Future WAN phase (documented, not built): add `public` key in the Split Horizon APP config and a public `dynamic.fatherfankscloud.uk` A record + DDNS. The CNAME→host→SplitHorizon structure is WAN-ready; only the `public` value must be added later.

## 2. Deployment (host: mocha)

| Item | Decision |
|---|---|
| Image | `technitium/dns-server:15.4.0` (pinned) |
| Compose location | `services/technitium/compose.yaml` |
| Storage | `/mnt/monarch/appdata/technitium/config` → `/etc/dns`, `/mnt/monarch/appdata/technitium/logs` → `/var/log/technitium/dns` |
| DNS listen | `192.168.50.44:53/udp+tcp` (LAN), `100.102.139.115:53/udp+tcp` (Tailscale) — **bound to explicit IPs**, not `0.0.0.0` (avoids libvirt `192.168.122.1:53` conflict and public exposure) |
| Web console | `192.168.50.44:5380` + `100.102.139.115:5380` (LAN/Tailscale only; **no public**) |
| Restart | `unless-stopped` |
| User | default container user (no privileged, no extra caps) |
| Healthcheck | TCP probe to `:5380` via bash `/dev/tcp` |
| Networks | default bridge (service has no need of `proxy`/`hotio`; DNS is a network-edge service). No host ports beyond the explicit DNS/web binds. |

## 3. Environment (via `.env`, gitignored; `.env.example` committed)

| Var | Value |
|---|---|
| `DNS_SERVER_DOMAIN` | `dns.mocha` (server's own domain; does not auto-create zones) |
| `DNS_SERVER_ADMIN_PASSWORD` | generated strong random password (stored in `.env`, never git) |
| `DNS_SERVER_RECURSION` | `AllowOnlyForPrivateNetworks` — allows RFC1918 + CGNAT `100.64.0.0/10` (verified in `NetUtilities.cs`), denies public |
| `DNS_SERVER_ENABLE_BLOCKING` | `true` |
| `DNS_SERVER_BLOCK_LIST_URLS` | set during Phase 5 |
| `DNS_SERVER_FORWARDERS` | temporary documented value for validation (see Phase 5); **final upstream requires confirmation** |
| `DNS_SERVER_LOG_USING_LOCAL_TIME` | `true` |

## 4. Zones & records (reproducible via API script)

### Primary zone: `fatherfankscloud.uk`

**Host record (APP, Split Horizon `SplitHorizon.SimpleAddress`):**

| Name | Type | Config |
|---|---|---|
| `mocha` | APP (`SplitHorizon.SimpleAddress`) | `{"private":["192.168.50.44"],"100.64.0.0/10":["100.102.139.115"]}` |

Matching verified in `SimpleAddress.cs`: CIDR keys match most-specific first; `private` fallback = `NetUtilities.IsPrivateIP` (includes CGNAT). LAN clients → `192.168.50.44`; Tailscale clients → `100.102.139.115`; others → no answer (falls through; no WAN record yet).

**Service CNAME records** (all → `mocha.fatherfankscloud.uk`):

`sso, code, hermes, homeassistant, home, jellyfin, jellyseerr, kav, nx, chat, sparkyfitness, calib, calibre` (14 migrated)  
`traefik, bazarr, honcho, prowlarr, radarr` (5 added — verified against live Traefik routers)

**Explicitly NOT created:** `echo.fatherfankscloud.uk` (no running container; EchoOS compose in `needing-to-be-deleted`) — flagged for review.

**Bare hostname parity:** `mocha` → `192.168.50.44`, `casaos` → `192.168.50.213` (matches current Pi-hole answers).

### Reverse zone: `192.168.50.0/24`

| PTR | Target |
|---|---|
| `44` | `sso.fatherfankscloud.uk` |
| `213` | `casaos` |
| `96` | `P110M` |
| `73` | `Trevs-iPhone` |
| `119` | `MacBookPro` |

## 5. Blocklists (Phase 5)

- Technitium Block List Zone (`DNS_SERVER_ENABLE_BLOCKING=true`), blocklist URLs in settings.
- Pi-hole exact list URLs **not readable without auth** → use safe documented defaults (e.g. StevenBlack `hosts`, Disconnect lists) for validation, flagged; final lists must be confirmed by the user.
- Preserve allowlist intent via Technitium Allowed Zone (import) — pending Pi-hole export.

## 6. Upstream DNS (Phase 5)

- Pi-hole is a forwarding resolver with DNSSEC validation on (SERVFAIL on `dnssec-failed.org`).
- Exact upstreams **not readable without auth** → do **not** guess for production. Use a temporary documented forwarder (e.g. Cloudflare `1.1.1.1` + Google `8.8.8.8`, DNSSEC validation on) for isolated validation; production cutover waits for confirmation.

## 7. Tailscale (this phase)

- Configure split DNS: route `fatherfankscloud.uk` queries from Tailscale clients to Technitium at `100.102.139.115:53`.
- Mechanism: Tailscale admin console → DNS → split DNS / nameserver entry. Requires `tailscale up --accept-dns` on clients (already enabled on mocha). Verify from a Tailscale client.
- No other Tailscale changes.

## 8. Security

- DNS recursion only for private/CGNAT sources (`AllowOnlyForPrivateNetworks`).
- DNS + web bound to LAN/Tailscale IPs only — cannot become a public open resolver.
- Web console auth: admin password from `.env`; not committed.
- No privileged mode, no extra capabilities, no host network mode.

## 9. Validation (Phase 7) — before any cutover

1. `dig` from mocha: LAN A for every service hostname → `192.168.50.44`.
2. Traefik HTTPS for every hostname (resolve via Technitium, expect 200/redirect + valid cert).
3. Blocking: ad domain → blocked; allowlisted → allowed; normal → resolves.
4. Tailscale client: hostname → `100.102.139.115`; HTTPS + cert OK.
5. Failure: upstream down (temporary), NXDOMAIN, restart resilience.
6. `dig` comparisons vs Pi-hole for parity.

## 10. Cutover (Phase 8 — NOT yet)

Router DHCP DNS `192.168.50.213 → 192.168.50.44` (user action). Pi-hole remains up for rollback.

## 11. Phase boundary / definition of success

**Technitium becomes a fully validated LAN + Tailscale DNS replacement for Pi-hole, without changing public/WAN exposure.** WAN/DDNS/public-DNS integration is documented as a future phase and does not require redesign of the LAN/Tailscale DNS architecture.
