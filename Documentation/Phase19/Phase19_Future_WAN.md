# Phase 19 — Future Phase: WAN / DDNS / Public DNS

**Status:** DESIGNED, NOT BUILT (Phase 20+)

The unified LAN/Tailscale/WAN hostname architecture is achieved incrementally. This
phase delivers LAN + Tailscale. The WAN layer is documented here so it can be added
later **without redesigning** the LAN/Tailscale DNS architecture.

## Target architecture

```text
service.fatherfankscloud.uk
        CNAME
             ↓
mocha.fatherfankscloud.uk
        Split Horizon
       ↙      ↓       ↘
    LAN    Tailscale   WAN
192.168.50.44  100.102.139.115  public IP
```

## What changes (when built)

1. **Technitium Split Horizon** — add a `public` key to the `mocha` APP record config:
   ```json
   {"private":["192.168.50.44"],"100.64.0.0/10":["100.102.139.115"],"public":["<WAN-IP>"]}
   ```
   WAN clients querying Technitium directly would get the public IP. (Technitium is not
   publicly exposed, so the `public` value is mainly for completeness / future use.)

2. **Public DNS (Cloudflare)** — replace the dead `*.fatherfankscloud.uk A 0.0.0.9`
   wildcard with:
   - `dynamic.fatherfankscloud.uk A <WAN-IP>` (only record containing the public IP)
   - Optional per-service records or a `*.fatherfankscloud.uk` wildcard → via CNAME to `dynamic`
3. **DDNS container** — small Docker Compose service updating `dynamic.fatherfankscloud.uk`
   via the Cloudflare API when the WAN IP changes (least-privilege token, no creds in git).
4. **NAT/router** — port-forward 443 (+80 redirect) from WAN to Traefik `192.168.50.44`.
5. **Traefik** — wildcard cert `*.fatherfankscloud.uk` already exists (DNS-01) and works
   for WAN. No cert changes needed.
6. **Tailscale** — unchanged (already routes `fatherfankscloud.uk` → Technitium).

## Validation (when built)

Same hostname `service.fatherfankscloud.uk` from all three contexts:
- LAN → `192.168.50.44`, HTTPS + cert OK
- Tailscale → `100.102.139.115`, HTTPS + cert OK
- WAN → WAN IP, NAT + HTTPS + cert OK

## Open items / prerequisites

- Confirm the ISP WAN IP is dynamic and whether CGNAT is in use (test: WAN IP vs router WAN IP).
- Choose DNS provider API for DDNS (Cloudflare API token with DNS edit, scoped to the zone).
- Security: keep Technitium recursion non-public; keep DNS/web LAN+TS-bound.
