# Phase 19 — Existing-State Audit (Pi-hole → Technitium DNS Migration)

**Date:** 2026-08-16  
**Status:** Complete  
**Author:** opencode (implementation agent), with host access on mocha

## 1. Host (ZimaBlade / mocha)

| Item | Value | Evidence |
|---|---|---|
| OS | Ubuntu 22.04.5 LTS (Jammy) | `/etc/os-release` |
| Kernel | 6.8.0-136-generic | `uname -a` |
| Hostname | `mocha` | `hostname` |
| CPU | Intel i5-11400 (desktop class) | `/proc/cpuinfo` |
| LAN IP | `192.168.50.44/24` (enp6s0, DHCP) | `ip addr`, lease |
| Gateway | `192.168.50.1` (router, DHCP server) | `ip route` |
| DHCP | Router hands out DNS `192.168.50.213` to clients | systemd network lease |
| Docker | 29.5.3 | `docker --version` |
| Docker Compose | v5.1.4 | `docker compose version` |
| Docker root | `/var/lib/docker` (overlay2) | `docker info` |
| Storage free | 89G of 457G (`/`) | `df -h` |
| IPv6 | **None on LAN** (link-local only); no ISP IPv6; Tailscale ULA `fd7a:...` present | `ip -6 addr`, `ping6` |
| Tailscale | `100.102.139.115` (tailnet `tail86073.ts.net`), MagicDNS on, **no custom resolvers / no split DNS** | `tailscale status`, `tailscale dns status` |
| WAN IP | `121.109.142.145` (dynamic; no DDNS exists) | `curl ifconfig.me` |

## 2. Existing Pi-hole (to be replaced)

| Item | Value |
|---|---|
| Host | ZimaBlade / CasaOS at `192.168.50.213` (MAC `00:e0:4c:30:6e:27`, Realtek) |
| Image | `pihole/pihole:2025.03.0` (CasaOS-managed) |
| DNS | `:53` tcp+udp |
| Web | `:8800` (redirect to login) |
| DHCP ports | `:67`/`:547` published in compose, **but router (.1) is the active DHCP server**; Pi-hole DHCP appears inactive |
| Storage | `/media/devmon/SamsungUSB/pihole/etc/{pihole,dnsmasq.d}` |
| Access | SSH blocked; API auth failed (password ≠ `casaos`) → live config export pending admin password |
| Role | **Forwarding resolver** (confirmed: PTR for 8.8.8.8 → dns.google) |
| Blocking | Active — ad domains answered `0.0.0.0` (doubleclick.net, googleadservices.com, etc.) |

### Pi-hole local records (TTL 0 → `192.168.50.44`)

`sso, code, hermes, homeassistant, home, jellyfin, jellyseerr, kav, nx, chat, sparkyfitness, calib, calibre, echo`

### Pi-hole local PTR records

| IP | PTR |
|---|---|
| `192.168.50.44` | `sso.fatherfankscloud.uk` |
| `192.168.50.213` | `casaos` |
| `192.168.50.96` | `P110M` |
| `192.168.50.73` | `Trevs-iPhone` |
| `192.168.50.119` | `MacBookPro` |

## 3. Existing Traefik

| Item | Value |
|---|---|
| Image | `traefik:v3.6.7` |
| Ports | `80`/`443` (web + websecure entrypoints) |
| Docker network | `proxy` (172.19.0.0/16), container IP `172.19.0.6` |
| ACME | Cloudflare DNS-01, `*.fatherfankscloud.uk` wildcard, EC256 |
| Domain | `fatherfankscloud.uk` (Cloudflare authoritative) |

### Traefik router hostnames (verified live from container labels)

| Hostname | Container |
|---|---|
| `sso.fatherfankscloud.uk` | authentik-server |
| `bazarr.fatherfankscloud.uk` | bazarr |
| `calib.fatherfankscloud.uk` | calibre-web |
| `calibre.fatherfankscloud.uk` | calibre (compose-defined; calibre-web container only in prod) |
| `code.fatherfankscloud.uk` | code-server |
| `hermes.fatherfankscloud.uk` | hermes |
| `home.fatherfankscloud.uk` | homepage |
| `honcho.fatherfankscloud.uk` | honcho-api |
| `jellyfin.fatherfankscloud.uk` | jellyfin |
| `jellyseerr.fatherfankscloud.uk` | jellyseerr |
| `kav.fatherfankscloud.uk` | kavita |
| `nx.fatherfankscloud.uk` | nextcloud |
| `chat.fatherfankscloud.uk` | open-webui |
| `prowlarr.fatherfankscloud.uk` | prowlarr |
| `radarr.fatherfankscloud.uk` | radarr |
| `traefik.fatherfankscloud.uk` | traefik |
| `sparkyfitness.fatherfankscloud.uk` | sparkyfitness-frontend |

## 4. Public DNS (Cloudflare, zone `fatherfankscloud.uk`)

- Single record: `*.fatherfankscloud.uk A 0.0.0.9` (unproxied, **dead placeholder**).
- No cloudflared/tunnel, no public A records, no MX/TXT/SPF beyond default.
- **Public access to homelab services is effectively disabled today.**
- WAN IP dynamic (`121.109.142.145`); no DDNS mechanism.

## 5. Docker networks relevant

| Network | Subnet | Purpose |
|---|---|---|
| `proxy` | 172.19.0.0/16 | Traefik ingress |
| `hotio_default` | 172.27.0.0/16 | *arr automation |
| `homelab` | 192.168.0.0/20 | pre-existing monitoring net (Beszel) |
| default bridge | 172.17.0.0/16 | default |

## 6. Port availability on mocha (for Technitium)

| Port | Status |
|---|---|
| `53/udp+tcp` | **Conflict:** libvirt dnsmasq binds `192.168.122.1:53` (virbr0 DOWN). Bind Technitium to explicit IPs (`192.168.50.44`, `100.102.139.115`) instead of `0.0.0.0`. |
| `5380` (web console) | Free |

## 7. Key findings / gaps

1. Pi-hole record set is **incomplete** — `traefik`, `bazarr`, `honcho`, `prowlarr`, `radarr` currently fall through to dead public `0.0.0.9` and **do not resolve on LAN**.
2. Live blocklist URLs / upstream resolvers / allowlist / regex are **not yet readable** (awaiting admin password).
3. No Tailscale split-DNS configured; MagicDNS `100.100.100.100` used by default.
4. No DDNS; WAN IP dynamic.
5. IPv6 absent on LAN — do not create AAAA records.
6. `0.0.0.9` public wildcard means public access is intentionally absent; keep it that way unless explicitly required.
