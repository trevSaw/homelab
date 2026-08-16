# Phase 19 — Validation Report (Before Cutover)

**Date:** 2026-08-16  
**Status:** PASS — Technitium validated as LAN + Tailscale DNS replacement  
**Not yet done:** cutover (router DHCP change), Pi-hole retirement

## 1. Deployment status

| Item | Status |
|---|---|
| Container | `technitium` — `technitium/dns-server:15.4.0`, **Up / healthy** |
| Web console | `http://192.168.50.44:5380/` and `http://100.102.139.115:5380/` → HTTP 200 |
| DNS (LAN) | `192.168.50.44:53/udp+tcp` responding |
| DNS (Tailscale) | `100.102.139.115:53/udp+tcp` responding |
| Config/logs | `/mnt/monarch/appdata/technitium/{config,logs}` (persist across restart) |
| Recursion | `AllowOnlyForPrivateNetworks` (verified: `NetUtilities.cs` treats CGNAT `100.64.0.0/10` as private) |
| Web console binding | LAN + Tailscale IPs only; **not** `0.0.0.0`; no public exposure |
| Blocking | enabled, `AnyAddress` (→ `0.0.0.0`), 4 block lists loaded |

## 2. Zone / record verification

- Primary zone `fatherfankscloud.uk`: SOA + NS + 1 APP host record + 18 CNAME + 1 A (`casaos`) ✓
- Host APP record `mocha` (`SplitHorizon.SimpleAddress`):
  - LAN source → `192.168.50.44` ✓
  - Tailscale source (`-b 100.102.139.115`) → `100.102.139.115` ✓
- Reverse zone `50.168.192.in-addr.arpa`: PTRs for .44, .213, .96, .73, .119 ✓ (match Pi-hole)
- `echo.fatherfankscloud.uk` **not created** (flagged for review; no running container)

## 3. Traefik HTTPS hostnames (LAN, resolved via Technitium → 192.168.50.44)

| Hostname | HTTP result | Notes |
|---|---|---|
| sso | 302 | Authentik login redirect — correct |
| home | 200 | OK |
| traefik | 302 | dashboard auth redirect — correct |
| jellyfin | 302 | OK |
| jellyseerr | 307 | OK |
| kav | 200 | OK |
| nx | 302 | OK |
| chat | 200 | OK |
| code | 302 | OK |
| hermes | 302 | OK |
| homeassistant | 200 | OK |
| honcho | 404 (root path) | Traefik routing OK; backend serves on subpath |
| bazarr | 200 | OK |
| prowlarr | 200 | OK |
| radarr | 200 | OK |
| sparkyfitness | 200 | OK |
| calib | 404 (root path) | Traefik routing OK |
| calibre | 404 (root path) | Traefik routing OK |

Wildcard cert `*.fatherfankscloud.uk` + apex SAN confirmed via `openssl s_client`; per-host CNs (jellyfin, nx, traefik, sso) confirm correct routers.

**Note:** `honcho/calib/calibre/bazarr` previously **did not resolve on LAN** via Pi-hole (fell through to dead `0.0.0.9`). They now resolve correctly.

## 4. Blocking (vs Pi-hole parity)

| Domain | Pi-hole | Technitium |
|---|---|---|
| doubleclick.net | 0.0.0.0 | 0.0.0.0 ✓ |
| googleadservices.com | 0.0.0.0 | 0.0.0.0 ✓ |
| googlesyndication.com | 0.0.0.0 | 0.0.0.0 ✓ |
| adnxs.com | 0.0.0.0 | 0.0.0.0 ✓ |
| amazon-adsystem.com | 0.0.0.0 | 0.0.0.0 ✓ |
| example.com | resolves | resolves ✓ |
| mozilla.org | resolves | resolves ✓ |

Block lists: StevenBlack hosts (98,949), urlhaus.abuse.ch (348), Disconnect tracking (34), Disconnect ad (2,700).
**Dead list removed:** `mirror1.malwaredomains.com/justdomains` returned 404 → replaced with urlhaus.abuse.ch (live).

## 5. Failure / resilience behavior

| Test | Result |
|---|---|
| NXDOMAIN | correct NXDOMAIN ✓ |
| DNSSEC validation | SERVFAIL on `dnssec-failed.org` (matches Pi-hole) ✓ |
| TCP transport | resolves ✓ |
| MX/other types | resolves ✓ |
| Container restart | healthy; config + records + blocking persist ✓ |
| Web console auth | admin password required; not exposed publicly ✓ |

## 6. Security posture

- Recursion restricted to private + CGNAT sources — cannot become public open resolver ✓
- DNS + web bound to LAN/Tailscale IPs only ✓
- No privileged mode / no extra caps / no host networking ✓
- Admin password in gitignored `.env` (mode 600) ✓

## 7. Tailscale integration — ACTION REQUIRED (admin console)

Server side is ready (Technitium answers on `100.102.139.115`; split horizon verified by binding query source to the Tailscale IP). The **split-DNS route** must be added in the Tailscale admin console:

1. Open https://login.tailscale.com/admin/dns
2. **Nameservers → Add nameserver**
3. Enter `100.102.139.115`
4. Select **Restricted nameservers (split DNS)** and add the domain **`fatherfankscloud.uk`**
5. Save

Tailscale will then send `*.fatherfankscloud.uk` queries from tailnet clients to Technitium, which answers with the Tailscale IP (`100.102.139.115`) via split horizon. No subnet routing needed (nameserver is a Tailscale IP).

## 8. Remaining pre-cutover items

1. **Confirm Pi-hole exact upstream forwarders** (auth-locked). Temporary: Cloudflare `1.1.1.1` + Google `8.8.8.8`, DNSSEC on. **Cutover requires approval of upstream choice.**
2. **Confirm Pi-hole blocklist URLs** (auth-locked). Currently using documented defaults; verify blocking parity after cutover and adjust if needed.
3. **Tailscale split-DNS admin-console step** (above).
4. **Pi-hole allowlists/denylists/regex** could not be exported (auth-locked) — verify no false-positive blocking after cutover.
5. `echo.fatherfankscloud.uk` — decide keep/drop.

## 9. Cutover (NOT performed)

Router DHCP DNS `192.168.50.213 → 192.168.50.44` — user action, after above approvals. Pi-hole stays up as rollback.
