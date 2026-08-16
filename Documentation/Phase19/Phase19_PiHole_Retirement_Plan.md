# Phase 19 — Pi-hole Retirement Plan (Phase 10)

**Status:** PLAN COMPLETE. **Pi-hole is NOT being retired, stopped, or modified.**
Actual retirement happens only after stabilization and explicit approval.

---

## 1. What Pi-hole currently provides (inventory)

| Item | Value |
|---|---|
| Host | ZimaBlade (192.168.50.213), CasaOS |
| Container | `pihole/pihole:2025.03.0` |
| Role | LAN recursive DNS (forwarding) + ad blocking |
| DNS | :53 tcp/udp |
| Web | :8800 |
| Local records | 14 hostnames → 192.168.50.44 (all now recreated in Technitium) |
| PTRs | 5 (all now recreated in Technitium) |
| Blocking | active (ad domains → 0.0.0.0) |
| DHCP | ports published in compose, but router (.1) is the actual DHCP server |
| Data | `/media/devmon/SamsungUSB/pihole/etc/{pihole,dnsmasq.d}` |

## 2. What Technitium now provides

- Primary zone `fatherfankscloud.uk` (18 service CNAMEs → `mocha` host APP record)
- Split Horizon: LAN → 192.168.50.44, Tailscale → 100.102.139.115
- 5 PTRs, blocking (4 lists, ~102k domains), DNSSEC validation, `AllowOnlyForPrivateNetworks`
- DNS + web bound to LAN/Tailscale IPs only

## 3. Migrated configuration

| Pi-hole item | Migrated to Technitium | Status |
|---|---|---|
| Local records (14) | CNAMEs → `mocha` + host APP record | ✅ |
| Missing records (traefik, bazarr, honcho, prowlarr, radarr) | added | ✅ |
| PTRs (5) | reverse zone | ✅ |
| Blocking behavior | block lists + AnyAddress | ✅ (lists are documented defaults, not Pi-hole's exact URLs) |
| Forwarding upstream | forwarders 1.1.1.1/8.8.8.8 + DNSSEC | ⚠️ temporary; confirm Pi-hole's actual upstreams |
| Allowlists | — | ❌ **not exported** (auth-locked) — verify via false-positive scan |
| Denylists / regex | — | ❌ **not exported** (auth-locked) — verify blocking parity |

## 4. What was NOT migrated / cannot be migrated

- Pi-hole's exact blocklist URLs, allowlist domains, denylist/regex rules — **not
  readable without admin credentials** (auth required; user chose not to provide).
- Pi-hole's DHCP scope config (if any) — router is the DHCP server; not applicable.
- Any Pi-hole-specific query history / stats.

## 5. Pi-hole backup / export requirements (before any retirement)

Before retirement, capture (manual, on the ZimaBlade / Pi-hole web console):

- [ ] **Teleporter export** (Pi-hole Settings → Teleporter → Generate) — full config:
      lists, allowlist, denylist, regex, upstreams, DHCP, custom records. Save to durable storage.
- [ ] Copy of `/media/devmon/SamsungUSB/pihole/etc/pihole/` (setupVars.conf, adlists.list,
      custom.list, etc.) and `/etc/dnsmasq.d/`.
- [ ] Record Pi-hole web admin password hash (do NOT commit to git).
- [ ] Note the Pi-hole container image + compose (CasaOS app) for reproducibility.

These are required so Pi-hole can be restored or its exact configuration referenced later.

## 6. Retirement criteria (ALL must hold)

1. **Stabilization period elapsed** — Technitium stable (e.g. ≥ 14 days) with no rollback.
2. **All important LAN services work** — Traefik hostnames (18), media, AI, home automation.
3. **All important clients resolve correctly** — LAN + Tailscale clients.
4. **Tailscale DNS works** — split-DNS route active, TS clients resolve to Tailscale IP.
5. **Blocking confirmed** — ads/telemetry blocked; **no significant false positives**
   (any Pi-hole allowlist gap verified and re-created in Technitium Allowed Zone).
6. **Traefik services remain healthy** throughout observation.
7. **Rollback no longer reasonably necessary** — no open incidents depending on Pi-hole.
8. **Pi-hole backup/export completed** (§5).

## 7. Rollback procedure (before retirement)

If Technitium fails during stabilization:

1. Router DHCP DNS → `192.168.50.213` (Pi-hole). Save.
2. Clients renew → return to Pi-hole. No Pi-hole changes needed.
3. Technitium remains installed but unused; investigate and fix, then retry cutover.

See `Phase19_Cutover_Procedure.md` §7 for full details.

## 8. Eventual Docker / container removal procedure

Only after criteria met AND user approval:

1. Router DHCP already points to Technitium (192.168.50.44).
2. Confirm no clients querying `192.168.50.213` (Pi-hole query log empty / stale leases gone).
3. On ZimaBlade (CasaOS): stop + remove the Pi-hole app (or `docker compose stop`).
4. **Keep** the Pi-hole data on `/media/devmon/SamsungUSB/pihole/` (do not delete) and the
   Teleporter export in durable storage.
5. Optionally remove the `.213 → casaos` PTR + `casaos` A record from Technitium
   (currently kept for parity).
6. Document the retirement in `Documentation/Phase19/` and update `Services/ServiceIndex.md`
   (Pi-hole → Archived, Technitium → sole DNS).

**Do NOT delete Pi-hole data or its compose config as part of this phase.**

## 9. What to preserve indefinitely

- Pi-hole Teleporter export + config copy (long-term backup).
- Pi-hole compose/CasaOS app definition (for reference/reproducibility).
- This plan + Phase 19 docs.
