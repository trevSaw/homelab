# Phase 19 — Technitium DNS Migration Report

**Date:** 2026-08-16  
**Verdict:** DEPLOYED + VALIDATED (LAN + Tailscale). Cutover NOT yet performed.

## Summary

Pi-hole replaced by Technitium DNS 15.4.0 as the homelab's LAN + Tailscale DNS server,
running on mocha (`192.168.50.44`). Implements the CNAME → host → Split Horizon
architecture with LAN/Tailscale split addressing. Public/WAN exposure remains disabled
(future phase). Pi-hole remains up as rollback.

## Results by area

| Area | Result |
|---|---|
| Deployment | `services/technitium/` compose, pinned `15.4.0`, appdata storage, healthy |
| Split Horizon | `mocha.fatherfankscloud.uk` APP record (`SplitHorizon.SimpleAddress`): LAN→`192.168.50.44`, TS→`100.102.139.115` |
| Records | 18 service CNAMEs → mocha (14 migrated + 5 added − `echo` held for review) |
| PTRs | 5 migrated (match Pi-hole) |
| Blocking | 4 lists (~102k domains), `0.0.0.0` responses match Pi-hole behavior |
| Traefik | all hostnames resolve + route via Traefik; wildcard cert valid |
| Security | recursion `AllowOnlyForPrivateNetworks`; DNS+web LAN/TS-bound; no public exposure |
| Tailscale | server ready on `100.102.139.115`; split-DNS route = admin-console action |

## Files created/modified

- `services/technitium/{compose.yaml,.env.example,README.md,Versions.md}` (new)
- `scripts/migration/setup-technitium.sh` (new — reproducible config)
- `Documentation/Phase19/{Phase19_Audit,Phase19_DNS_Inventory,Phase19_Design,Phase19_Validation}.md` (new)
- `Documentation/services/technitium/technitium.md` (new)
- `Documentation/services/INDEX.md`, `Services/ServiceIndex.md` (updated)

## Containers

- `technitium` — `technitium/dns-server:15.4.0`, healthy, `unless-stopped`

## Ports / IPs

- DNS: `192.168.50.44:53` + `100.102.139.115:53` (udp+tcp)
- Web: `192.168.50.44:5380` + `100.102.139.115:5380`

## Zones / records

- `fatherfankscloud.uk` Primary: APP `mocha`, CNAMEs (18), A `casaos`
- `50.168.192.in-addr.arpa` Primary: PTRs (5)

## Blocklists migrated

StevenBlack hosts, urlhaus (replaced dead malwaredomains), Disconnect tracking + ad.
Pi-hole's exact lists not readable (auth-locked) — documented defaults; parity confirmed.

## Validation

See `Documentation/Phase19/Phase19_Validation.md` — all PASS.

## Cutover status

**NOT CUT OVER.** Router DHCP DNS still points to Pi-hole (192.168.50.213).
Next steps: Tailscale admin-console split-DNS + router DHCP change (user action) after
upstream/blocklist confirmation.

## Preparation documents (all complete)

- `Phase19_Tailscale_Action.md` — Tailscale split-DNS user action (100.102.139.115 / fatherfankscloud.uk)
- `Phase19_Cutover_Procedure.md` — Phase 8 cutover + rollback procedure
- `Phase19_PostCutover_Monitoring.md` — Phase 9 full PASS/FAIL checklist
- `Phase19_PiHole_Retirement_Plan.md` — Phase 10 retirement criteria + procedure
- `Phase19_Known_Exceptions.md` — placeholder for post-cutover client findings

## Task state

- [ ] Tailscale split-DNS route — USER ACTION (admin console)
- [ ] Phase 8: Cutover — USER ACTION / approval required (router DHCP)
- [ ] Phase 9: Post-cutover monitoring — prepared; completes after cutover
- [ ] Phase 10: Pi-hole retirement — plan complete; actual retirement later

## Rollback

Pi-hole (192.168.50.213) untouched and still the LAN DNS server. To roll back Technitium:
`docker compose -f services/technitium/compose.yaml stop`; no client changes required.

## Remaining issues

1. Pi-hole exact upstream forwarders — confirm before cutover (temporary: 1.1.1.1/8.8.8.8).
2. Pi-hole blocklist/allowlist/regex — verify parity post-cutover.
3. Tailscale split-DNS route — admin console action.
4. `echo.fatherfankscloud.uk` — decide keep/drop.

## Recommended follow-up (WAN phase)

Implement WAN/DDNS/public-DNS per the documented unified architecture — the current
CNAME→host→SplitHorizon structure is WAN-ready (add `public` value + `dynamic.*` record + DDNS).
