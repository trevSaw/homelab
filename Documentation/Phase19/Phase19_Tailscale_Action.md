# Phase 19 — Tailscale Split-DNS (USER ACTION)

**Status:** PENDING — requires manual action in the Tailscale Admin Console.  
**Do not bypass:** the split-DNS route cannot be configured from the mocha CLI (no API token; admin console only).

## Required configuration

| Field | Value |
|---|---|
| Nameserver | `100.102.139.115` (mocha's Tailscale IP) |
| Type | **Restricted nameserver (split DNS)** |
| Domain | `fatherfankscloud.uk` |
| Override DNS servers | NOT required (leave off — only the listed domain routes to Technitium) |

## Exact steps

1. Open <https://login.tailscale.com/admin/dns>
2. In the **Nameservers** section click **Add nameserver**
3. Enter `100.102.139.115`
4. Select **Restricted nameservers** (this creates split DNS)
5. In the **Domains** field enter `fatherfankscloud.uk`
6. **Save**

## Why this works

- Tailscale sends `*.fatherfankscloud.uk` queries from tailnet clients to
  `100.102.139.115:53` (Technitium).
- Technitium's `mocha.fatherfankscloud.uk` Split Horizon APP record returns the
  **Tailscale IP** (`100.102.139.115`) to Tailscale clients.
- All other domains continue to use each client's normal DNS.
- No subnet routing needed: the nameserver is a Tailscale IP reachable over the tailnet.
- Clients already run with `--accept-dns` (verified on mocha), so the route applies.

## Verify after applying (from any Tailscale client)

```bash
# From a Tailscale-connected client:
dig @100.100.100.100 sso.fatherfankscloud.uk A +short   # expect: 100.102.139.115
curl -k https://sso.fatherfankscloud.uk/ -o /dev/null -w "%{http_code}\n"  # expect 302/200
```

On macOS use `dscacheutil -q host -a name sso.fatherfankscloud.uk`;
on Windows use `Resolve-DnsName sso.fatherfankscloud.uk` (nslookup ignores NRPT rules).

## Rollback

Remove the restricted nameserver entry in the admin console. Tailnet clients revert to
their local/system DNS immediately.
