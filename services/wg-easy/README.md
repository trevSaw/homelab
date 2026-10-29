# wg-easy (diagnostic — alternative VPN to Tailscale)

WireGuard VPN server + web admin UI. Deployed to test whether an alternative VPN
restores remote DNS/service resolution while the Tailscale split-DNS issue on iOS
is being diagnosed. Peers/keys persist in `/mnt/monarch/appdata/wg-easy`.

## Deploy

```bash
cd services/wg-easy
cp .env.example .env   # set WG_HOST + PASSWORD_HASH first
docker compose up -d
```

Web admin UI: `http://100.102.139.115:51821` (Tailscale) or `http://192.168.50.44:51821` (LAN).
Admin password in `.env` (`PASSWORD_HASH`, bcrypt of the UI password).

## Router requirement (WAN access)

WireGuard listens on UDP `51820` (published on `0.0.0.0`, an approved exception).
For a remote client to connect you must forward **UDP 51820 → 192.168.50.44** on the
AsusWRT router (192.168.50.1). Without this the VPN works only on the LAN.

## Client setup

1. Open the admin UI, create a client, scan the QR code / download the config into the
   WireGuard app (iOS: App Store "WireGuard").
2. Config uses `WG_HOST` (currently the raw WAN IP — dynamic; consider a DDNS record
   e.g. `vpn.fatherfankscloud.uk` → WAN IP for stability) and pushes DNS `192.168.50.44`
   (Technitium) so `*.fatherfankscloud.uk` resolves to `192.168.50.44` over the tunnel.

## Notes

- Full tunnel (`WG_ALLOWED_IPS=0.0.0.0/0`) for the diagnostic; tighten to
  `192.168.50.0/24` once confirmed working.
- Container requires `NET_ADMIN`/`NET_RAW`/`SYS_MODULE` caps, `/dev/net/tun`, and
  `net.ipv4.ip_forward=1` — documented exception under DockerStandard.
- Web UI is bound to LAN + Tailscale IPs only (not public), mirroring Technitium.