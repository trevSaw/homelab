# Phase 19 — Post-Cutover Monitoring (Phase 9)

**Status:** PREPARED. Marked COMPLETE only after the actual cutover has occurred and
this checklist passes. Runs for the stabilization period after the router DHCP change.

---

## A. DNS health

| Check | Command (from LAN client / mocha) | Expected | PASS/FAIL |
|---|---|---|---|
| External resolution | `dig @192.168.50.44 example.com A +short` | real A record | ☐ |
| Internal hostname | `dig @192.168.50.44 sso.fatherfankscloud.uk A +short` | `192.168.50.44` | ☐ |
| NXDOMAIN | `dig @192.168.50.44 nope$RANDOM.com A +noall +comments` | `status: NXDOMAIN` | ☐ |
| DNSSEC | `dig @192.168.50.44 dnssec-failed.org A +noall +comments` | `status: SERVFAIL` | ☐ |
| UDP DNS | `dig @192.168.50.44 example.com A +short` | answer | ☐ |
| TCP DNS | `dig +tcp @192.168.50.44 example.com A +short` | answer | ☐ |
| Technitium health | `docker inspect technitium --format '{{.State.Health.Status}}'` | `healthy` | ☐ |
| Query success rate | `docker logs technitium --since 1h` | no error spikes; responses flowing | ☐ |
| Blocking behavior | `dig @192.168.50.44 doubleclick.net A +short` | `0.0.0.0` | ☐ |

## B. Traefik — all 18 migrated hostnames

For each: resolve → LAN IP → HTTPS → Traefik responds → valid wildcard cert → backend responds.

```bash
for svc in sso code hermes homeassistant home jellyfin jellyseerr kav nx chat \
           sparkyfitness calib calibre traefik bazarr honcho prowlarr radarr; do
  ip=$(dig @192.168.50.44 "$svc.fatherfankscloud.uk" A +noall +answer +time=3 +tries=1 | awk '$4=="A"{print $5;exit}')
  code=$(curl -sk -m 6 -o /dev/null -w "%{http_code}" --resolve "$svc.fatherfankscloud.uk:443:$ip" "https://$svc.fatherfankscloud.uk/")
  echo "$svc ip=$ip http=$code"
done
```

| Hostname | DNS → LAN IP | HTTPS | Traefik responds | Cert valid | Backend responds | PASS/FAIL |
|---|---|---|---|---|---|---|
| sso | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| code | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| hermes | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| homeassistant | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| home | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| jellyfin | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| jellyseerr | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| kav | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| nx | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| chat | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| sparkyfitness | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| calib | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| calibre | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| traefik | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| bazarr | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| honcho | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| prowlarr | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |
| radarr | 192.168.50.44 | ☐ | ☐ | ☐ | ☐ | ☐ |

Cert check: `echo | openssl s_client -connect 192.168.50.44:443 -servername <host> 2>/dev/null | openssl x509 -noout -subject -ext subjectAltName`

## C. Blocking

| Check | Command | Expected | PASS/FAIL |
|---|---|---|---|
| Known blocked | `dig @192.168.50.44 googleadservices.com A +short` | `0.0.0.0` | ☐ |
| Known blocked | `dig @192.168.50.44 adnxs.com A +short` | `0.0.0.0` | ☐ |
| Normal domain | `dig @192.168.50.44 github.com A +short` | real A | ☐ |
| Important app host | `dig @192.168.50.44 microsoft.com A +short` | real A | ☐ |
| False-positive scan | browse/use Jellyfin, Home Assistant, chat, sso, radarr, prowlarr | all load normally | ☐ |
| False-positive scan | common benign hosts (mozilla.org, cloudflare.com, apple.com) | resolve | ☐ |

**False-positive attention:** Pi-hole allowlists could not be exported (auth-locked). If
an application breaks after cutover, test its domains: `dig <domain> A +short`. If it
returns `0.0.0.0`, add it to the Technitium **Allowed Zone** (web console → Allowed
Zones → Add) or as a blocking bypass. Do NOT disable blocking globally.

## D. Clients

| Check | How | Expected | PASS/FAIL |
|---|---|---|---|
| Old leases retained | router lease table; Pi-hole query log | some clients briefly on 192.168.50.213 | ☐ |
| Clients still on Pi-hole | see `Phase19_Cutover_Procedure.md` §6 | only static/hardcoded or un-renewed | ☐ |
| Hardcoded DNS | `ipconfig /all` / `/etc/resolv.conf` on clients | document exceptions | ☐ |
| IPv6 DNS bypass | `resolvectl` / `ipconfig /all` — look for non-router IPv6 DNS | document if found | ☐ |
| Apps with own resolver | e.g. browsers with DoH, docker containers with custom DNS | document if found | ☐ |

Do NOT modify clients unnecessarily. Document exceptions in `Phase19/Phase19_Known_Exceptions.md`.

## E. Monitoring cadence

| When | Action |
|---|---|
| T+0 (immediately after cutover) | Full A + B checklist; spot-check C |
| T+1h | B (all 18), C, D |
| T+24h | Full A–D; review Technitium logs for error rate |
| Daily for stabilization period | Quick A + B spot-check; D lease count on Pi-hole should → 0 |

## F. Stabilization criteria (to close Phase 9)

- [ ] All A checks pass consistently
- [ ] All 18 Traefik hostnames pass B
- [ ] Blocking works; no unresolved false positives
- [ ] No clients still actively using Pi-hole (or only documented exceptions)
- [ ] Technitium healthy for the full observation period
- [ ] No rollback triggered
