---
title: ADR-0003 Home Assistant Networking
document_type: ADR
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
related_documents:
  - Architecture/standards/DockerStandard.md
  - Architecture/standards/HomelabArchitectureStandard.md
  - Documentation/services/homeassistant/service.md
---

# ADR-0003 — Home Assistant Networking

## Context

Home Assistant’s upstream Docker documentation commonly recommends `network_mode: host`
so that mDNS, SSDP, multicast discovery, and some local integrations work without
extra routing. This repository’s Homelab Architecture Standard and Docker Compose
Standard require:

- Attachment to declared core networks only (`proxy`, `internal`, `hotio`, …)
- No host-port publication for UI ingress
- Reverse-proxy (Traefik) as the sole external HTTP(S) entry point
- Avoidance of `network_mode: host` unless formally approved

Home Assistant is being introduced as a Phase 12 production SoT stack under
`services/homeassistant/` with config on `/mnt/monarch/appdata/homeassistant`.
A networking decision is required before compose is accepted as governance-compliant.

## Decision

Deploy Home Assistant Core on the **`proxy` bridge network only**, with:

- Traefik labels routing `homeassistant.fatherfankscloud.uk` → container port `8123`
- **No** published host ports
- **No** `network_mode: host` in the baseline compose

LAN device discovery that depends on multicast/broadcast is accepted as a
**known limitation** of the baseline. Integrations that support explicit host/IP
configuration are preferred.

If production requirements later prove that host networking (or selective
`macvlan` / host-net) is mandatory for radios or discovery, that change MUST:

1. Be recorded as an Architecture-approved exception in the service README
2. Update this ADR (or supersede it)
3. Pass Security Standard review (especially if combined with device mounts)

## Alternatives Considered

| Option | Pros | Cons |
|---|---|---|
| A. Host networking (upstream default) | Best discovery; simple for USB/Zigbee hosts | Violates DockerStandard §6/§9 without exception; bypasses proxy network model; widens host attack surface |
| B. Dual-home `proxy` + `internal` | Extra isolation for future backends | No current HA backend peers; adds complexity without benefit |
| C. `proxy` only + Traefik (**chosen**) | Compliant ingress, TLS, no host ports, matches Phase 12 UI services | Weaker automatic discovery; USB still needs separate exception |
| D. macvlan / ipvlan for HA | Near-LAN presence without full host net | New network type not in core network list; Architecture amendment required |

## Consequences

**Positive**

- Stack meets Architecture / Docker networking and reverse-proxy rules out of the box
- Consistent with Jellyfin/Jellyseerr Traefik patterns
- Smaller host exposure; easier audit of published ports (none)

**Negative**

- Auto-discovery of some IoT devices may fail until integrations are configured manually or a future exception is approved
- USB Zigbee/Z-Wave is not part of baseline and remains a separate Security exception if added

**Neutral**

- Operators must set `http.trusted_proxies` for the `proxy` Docker network CIDR

## Implementation Notes

1. Ship `services/homeassistant/compose.yaml` attached only to external `proxy`.
2. Provide `config/configuration.yaml.example` with `use_x_forwarded_for` and
   `trusted_proxies` covering the live `proxy` subnet.
3. Document discovery/USB limitations in README and `service.md`.
4. Do not add host ports “for convenience”; use Traefik or an approved temporary debug exception with expiry.
