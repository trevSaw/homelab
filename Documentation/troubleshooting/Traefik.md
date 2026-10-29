# Traefik Troubleshooting

Troubleshooting guide for Traefik issues.

## ACME DNS-01 renewal fails with `lookup dns.mocha`

### Symptoms

Traefik logs repeat an error like:

```text
propagation: time limit exceeded: ... lookup dns.mocha. on 127.0.0.11:53: no such host
```

Certificates expire or are served past `notAfter`, even though Cloudflare contains
the `_acme-challenge` TXT records.

### Cause

Technitium serves the internal split-horizon authoritative zone for
`fatherfankscloud.uk`. Its apex NS/SOA default to `dns.mocha` from
`DNS_SERVER_DOMAIN`; this is internal authority metadata, not the public delegation.
Lego's propagation check follows the local NS, cannot resolve `dns.mocha`, and never
reaches Cloudflare's public nameservers (`pola.ns.cloudflare.com`,
`rob.ns.cloudflare.com`).

### Fix

Keep the public resolver override in `services/traefik/compose.yaml`:

```yaml
dns:
  - 1.1.1.1
  - 8.8.8.8
```

This makes ACME propagation checks use public DNS while Docker service discovery
continues to use Docker's embedded DNS. Do not change Technitium's apex NS to
Cloudflare; the internal and public authority records are intentionally different.

### Validation

- `docker exec traefik cat /etc/resolv.conf` shows `ExtServers: [1.1.1.1 8.8.8.8]`.
- `docker logs traefik` shows certificate renewals without propagation errors.
- `openssl s_client -connect 192.168.50.44:443 -servername <host> -verify_return_error`
  returns `Verify return code: 0 (ok)` and a valid `notAfter` date.

Verified 2026-10-19: all four Traefik certificates renewed and validated after the
override was applied.
