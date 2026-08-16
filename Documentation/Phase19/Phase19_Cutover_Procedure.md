# Phase 19 — Cutover Procedure (Phase 8)

**Status:** PREPARED — cutover is a USER ACTION requiring explicit approval.  
**Current:** Router DHCP hands out DNS `192.168.50.213` (Pi-hole) to LAN clients.  
**Target:** Router DHCP hands out DNS `192.168.50.44` (Technitium).  
**Do NOT change the router configuration from code/scripts.** Perform these steps manually.

---

## 0. Preconditions (all must be true)

- [ ] Technitium healthy (`docker inspect technitium --format '{{.State.Health.Status}}'` → healthy)
- [ ] Validation matrix in `Phase19_Validation.md` passes
- [ ] Tailscale split-DNS applied (see `Phase19_Tailscale_Action.md`)
- [ ] Upstream forwarders confirmed (temporary: `1.1.1.1`, `8.8.8.8`) — user approval
- [ ] Pi-hole (192.168.50.213) still running and answering
- [ ] Technitium reachable at `192.168.50.44:53` from a LAN client

## 1. Pre-cutover snapshot

```bash
# Baseline: what the router currently hands out (expect 192.168.50.213)
resolvectl status enp6s0 | grep -i "dns servers"

# Confirm Pi-hole answer parity before switch (compare A answers)
for d in sso.fatherfankscloud.uk doubleclick.net example.com; do
  echo "== $d =="
  dig @192.168.50.213 $d A +short
  dig @192.168.50.44  $d A +short
done
```

## 2. Cutover (manual router change)

On the router (192.168.50.1, DHCP server):

1. Log in to router admin.
2. DHCP server settings → DNS server 1.
3. Change `192.168.50.213` → `192.168.50.44`.
4. (Optional) set DNS server 2 = `192.168.50.213` as fallback. **Not recommended** — a
   mixed-resolver setup can cause inconsistent split-horizon answers. Prefer single
   resolver during the stabilization period.
5. Save/apply. Optionally renew DHCP leases, or wait for lease expiry (router default).

## 3. Expected DNS behavior after cutover

| Client | Resolver | `sso.fatherfankscloud.uk` → |
|---|---|---|
| LAN client (new lease) | `192.168.50.44` (Technitium) | `192.168.50.44` (LAN) |
| LAN client (old lease, still on Pi-hole) | `192.168.50.213` | `192.168.50.44` (LAN) — same result |
| Tailscale client | `100.102.139.115` via split-DNS | `100.102.139.115` (Tailscale) |
| WAN client | public DNS (unchanged) | `0.0.0.9` (dead placeholder, unchanged) |

**Key point:** during lease overlap, clients on Pi-hole and clients on Technitium both
resolve internal names to `192.168.50.44` — identical split-horizon LAN result, so no
service disruption during the transition.

## 4. Validation commands immediately after cutover

```bash
# From a LAN client with a NEW lease (DNS = 192.168.50.44):
ipconfig /all   # (Win) or resolvectl status (Linux)
dig sso.fatherfankscloud.uk A +short          # expect 192.168.50.44
dig doubleclick.net A +short                  # expect 0.0.0.0 (blocked)
dig example.com A +short                      # expect real IP
dig dnssec-failed.org A +noall +comments     # expect SERVFAIL (DNSSEC ok)
dig +tcp example.com A +short                 # TCP DNS ok
```

## 5. What to check immediately after DHCP changes

1. **Router lease table** — confirm clients are being assigned DNS `192.168.50.44`.
2. **Technitium query log** — confirm LAN client IPs are querying it:
   ```bash
   docker logs technitium --since 5m | grep -cE "192\.168\.50\." 
   ```
3. **Traefik hostnames** — spot-check a few (see Phase 9 checklist).
4. **Internet browsing** — normal sites load; ads blocked.
5. **No hard breakage** — if critical services fail, revert (below).

## 6. Identify clients still using Pi-hole (old leases)

```bash
# From mocha, after cutover: any client still querying Pi-hole is on an old lease
docker logs technitium --since 1h 2>/dev/null | grep -oE "192\.168\.50\.[0-9]+" | sort | uniq -c

# Clients querying Pi-hole (192.168.50.213) directly — check Pi-hole's own query log
# (web console at http://192.168.50.213:8800 → Query Log) or, if reachable,
# grep Pi-hole container logs.

# Force renewal on a test client:
#   Linux:  sudo systemctl restart systemd-resolved (or dhclient -r -v && dhclient -v)
#   macOS:  networksetup -setdnsservers Wi-Fi 192.168.50.44
#   Windows: ipconfig /release && ipconfig /renew
```

Clients with **static/hardcoded** DNS to `192.168.50.213` will keep using Pi-hole —
that is acceptable during the stabilization period (Pi-hole and Technitium return the
same LAN answers). Flag them but do not modify them unless they misbehave.

## 7. Rollback procedure (revert to Pi-hole)

If cutover fails or critical services break:

1. Router admin → DHCP → DNS server 1 → `192.168.50.44` → `192.168.50.213`. Save.
2. Clients renew leases or revert automatically (lease expiry).
3. Pi-hole is untouched and fully functional — no Pi-hole changes were ever made.
4. Technitium stays running (harmless) or can be stopped:
   ```bash
   cd services/technitium && docker compose stop
   ```
5. Verify rollback: `dig @192.168.50.213 sso.fatherfankscloud.uk A +short` → `192.168.50.44`.

**Rollback is safe at any time** because:
- Pi-hole was never modified, stopped, or removed.
- Both resolvers return the same LAN answers for internal hostnames.
- No client configuration is required to revert (DHCP-driven).
