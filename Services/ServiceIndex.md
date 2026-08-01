# Service Index

> **Purpose**
>
> This document serves as the living index of software, Docker containers, self-hosted applications, and other technologies that I have discovered while researching my homelab.
>
> It acts as a long-term memory and decision log, allowing me to quickly find projects I've previously researched instead of rediscovering them months later.
>
> This document tracks:
>
> - Services currently running in the homelab
> - Services planned for future deployment
> - Projects being actively researched
> - Interesting software to revisit later
> - Alternatives to existing services
> - Projects that were evaluated but ultimately rejected
>
> This is **not** deployment documentation. Instead, it is the master index that links together research, documentation, and implementation.

---

# Status Definitions

| Status | Meaning |
|---------|---------|
| **Production** | Running in the homelab |
| **Testing** | Currently deployed for evaluation |
| **Planned** | Intended for future deployment |
| **Researching** | Actively gathering information |
| **Watching** | Interesting project to revisit later |
| **Rejected** | Evaluated and decided against |
| **Replaced** | Replaced by another solution |
| **Archived** | No longer maintained or no longer relevant |

---

# Priority Definitions

| Priority | Meaning |
|----------|---------|
| **Critical** | Core infrastructure or essential service |
| **High** | Strong candidate for deployment |
| **Medium** | Useful improvement |
| **Low** | Nice to have / future consideration |

---

# Column Reference

| Column | Meaning | Example |
|--------|---------|---------|
| **Documentation** | Service doc in `homelab/docs/services/` | `homelab/docs/services/Jellyfin.md` |
| **Deployment** | Compose project or other deployment path | `homelab/compose/media/jellyfin/` |

Leave **Documentation** and **Deployment** blank or use `—` for services that are not deployed yet.

---

# Related Documentation

| Document | Purpose |
|-----------|---------|
| Hardware.md | Hardware inventory and plans |
| Network.md | Network architecture |
| Storage.md | Storage architecture |
| AIArchitecture.md | AI stack and future plans |
| Security.md | Security architecture |
| Monitoring.md | Monitoring and observability |
| Backup.md | Backup strategy |
| Roadmap.md | Long-term deployment roadmap |

---

# Infrastructure

| Service | Category | Status | Priority | Last Reviewed | Documentation | Deployment | Alternatives | GitHub | Purpose | Notes |
|---------|----------|--------|----------|---------------|---------------|------------|--------------|--------|---------|-------|
| Traefik | Reverse Proxy | Production | Critical | 2026-07 | [homelab/docs/services/Traefik.md](../../homelab/docs/services/Traefik.md) | — | Nginx Proxy Manager, Caddy | https://github.com/traefik/traefik | Reverse proxy with automatic routing | Main ingress for Docker services |
| Pi-hole | DNS | Production | Critical | 2026-07 | — | — | AdGuard Home, Technitium DNS Server | https://github.com/pi-hole/pi-hole | Network-wide ad blocking and DNS | Primary DNS |
| Technitium DNS Server | DNS | Researching | High | — | — | — | Pi-hole, AdGuard Home | https://github.com/TechnitiumSoftware/DnsServer | Authoritative and recursive DNS server | Evaluating as Pi-hole alternative; not deployed yet |
| Portainer | Container Management | Production | High | — | — | — | Dockge, Arcane | https://github.com/portainer/portainer | Docker management UI | General administration |
| Dockge | Container Management | Planned | Medium | — | — | — | Portainer, Arcane | https://github.com/louislam/dockge | Docker Compose manager | Easier compose editing |
| Arcane | Container Management | Researching | Medium | — | — | — | Portainer, Dockge | https://github.com/getarcaneapp/arcane | Modern Docker management web UI | Needs research; evaluate multi-host Docker management and socket access model |
| Filebrowser | File Management | Planned | Medium | — | — | — | FileGator | https://github.com/filebrowser/filebrowser | Browser-based file manager | Useful for quick edits |
| Vaultwarden | Security | Planned | High | — | — | — | Bitwarden | https://github.com/dani-garcia/vaultwarden | Password manager | Personal password vault |
| Tailscale | VPN | Planned | High | — | — | — | WireGuard, wg-easy, Headscale | https://github.com/tailscale/tailscale | Secure remote access | Homelab access while traveling |
| wg-easy | VPN | Researching | High | — | [homelab/docs/services/WireGuard.md](../../homelab/docs/services/WireGuard.md) | — | Tailscale, Headscale | https://github.com/wg-easy/wg-easy | WireGuard VPN with web admin UI | Not deployed yet; evaluating for remote access |
| Ansible | Configuration Management | Planned | High | — | — | [homelab/ansible/](../../homelab/ansible/) | Salt, Puppet | https://github.com/ansible/ansible | Host and service configuration automation | Planned rollout; repo scaffold only |
| Terragrunt | Infrastructure as Code | Planned | High | — | — | [homelab/terragrunt/](../../homelab/terragrunt/) | Terraform, OpenTofu | https://github.com/gruntwork-io/terragrunt | Terraform orchestration for infra modules | Planned rollout; repo scaffold only |
| zerobyte | Backup Automation | Researching | High | — | — | — | restic, Kopia, Borgmatic | https://github.com/nicotsx/zerobyte | Backup automation for self-hosters built on restic | Needs research for homelab backup workflows |

---

# AI

| Service | Category | Status | Priority | Last Reviewed | Documentation | Deployment | Alternatives | GitHub | Purpose | Notes |
|---------|----------|--------|----------|---------------|---------------|------------|--------------|--------|---------|-------|
| Ollama | LLM Runtime | Production | Critical | 2026-08-01 | [services/ollama/README.md](../services/ollama/README.md) | [services/ollama/](../services/ollama/) | llama.cpp | https://github.com/ollama/ollama | Local LLM inference for KORA | Models at `/hive/ollama`; Phase 14.1 |
| Open WebUI | AI UI | Production | Critical | 2026-08-01 | [services/open-webui/README.md](../services/open-webui/README.md) | [services/open-webui/](../services/open-webui/) | LibreChat | https://github.com/open-webui/open-webui | UI surface for KORA (ADR-0008) | Routes to KORA, not direct Ollama |
| KORA Runtime | AI Conductor | Production | Critical | 2026-08-01 | [services/kora/README.md](../services/kora/README.md) | [services/kora/](../services/kora/) | — | — | Solo Stage 1 conductor façade | `AI/KORA/Runtime` |
| Hermes Agent | Thin Execution Layer | Production (thin) | High | 2026-08-01 | [services/hermes/README.md](../services/hermes/README.md) | [services/hermes/](../services/hermes/) | OpenHands | https://github.com/NousResearch/hermes-agent | ADR-0004 substrate | Not on Solo primary chat path |
| ChromaDB | Vector Database | Planned | Medium | — | — | — | Qdrant, Weaviate | https://github.com/chroma-core/chroma | Embeddings and semantic search | AI memory backend |
| Graphify | Knowledge Graph | Researching | Medium | — | — | — | None | https://github.com/Graphify-Labs/graphify | Turns codebases, docs, schemas, and PDFs into a queryable knowledge graph for AI coding assistants | Needs research; Cursor/Claude skill, local AST parsing, no vector store |
| OmniRoute | AI Gateway | Researching | Medium | — | — | — | LiteLLM, OpenRouter | https://github.com/diegosouzapw/OmniRoute | Unified AI gateway across many providers and models for coding assistants | Needs research; quota-aware fallback and token compression |
| Odysseus | Research | Planned | High | — | — | — | Open Deep Research | https://github.com/arthurcolle/odysseus | AI deep research | Web research workflows |
| SearXNG | Search | Planned | High | — | — | — | Brave Search API | https://github.com/searxng/searxng | Private metasearch engine | Used by AI agents |
| n8n | Automation | Planned | Medium | — | — | — | Activepieces | https://github.com/n8n-io/n8n | Workflow automation | AI workflows |
| Semaphore UI | Automation | Planned | Medium | — | — | — | AWX | https://github.com/semaphoreui/semaphore | Ansible management | Infrastructure automation |

---

# Media

| Service | Category | Status | Priority | Last Reviewed | Documentation | Deployment | Alternatives | GitHub | Purpose | Notes |
|---------|----------|--------|----------|---------------|---------------|------------|--------------|--------|---------|-------|
| Jellyfin | Media Server | Production | Critical | — | [homelab/docs/services/Jellyfin.md](../../homelab/docs/services/Jellyfin.md) | — | Plex, Emby | https://github.com/jellyfin/jellyfin | Movies, TV, music | Primary media server |
| Kapowarr | Comic Library | Researching | Medium | — | — | — | Mylar3 | https://github.com/Casvt/Kapowarr | Build and manage a comic book library | Needs research for comic library management |
| Maintainerr | Media Management | Researching | High | — | — | — | Janitorr | https://github.com/maintainerr/maintainerr | Cleans unused media | Storage management |
| Janitorr | Media Management | Researching | Medium | — | — | — | Maintainerr | https://github.com/Schaka/janitorr | Automated media cleanup | Alternative to Maintainerr |
| Playarr | Gaming | Researching | Medium | — | — | — | None | https://github.com/michaelpcole/playarr | Manage PC game libraries | Steam/GOG/Epic integration |
| Immich | Photos | Planned | High | — | — | — | PhotoPrism | https://github.com/immich-app/immich | Self-hosted Google Photos alternative | Automatic phone backups |

---

# Productivity

| Service | Category | Status | Priority | Last Reviewed | Documentation | Deployment | Alternatives | GitHub | Purpose | Notes |
|---------|----------|--------|----------|---------------|---------------|------------|--------------|--------|---------|-------|
| Nextcloud | Cloud Storage | Production | Critical | — | [homelab/docs/services/Nextcloud.md](../../homelab/docs/services/Nextcloud.md) | — | Seafile | https://github.com/nextcloud/server | File sync and collaboration | Also stores Logseq |
| Paperless-ngx | Documents | Planned | High | — | [homelab/docs/services/PaperlessNGX.md](../../homelab/docs/services/PaperlessNGX.md) | — | Maya EDMS | https://github.com/paperless-ngx/paperless-ngx | OCR document management | Paper archive |
| Stirling PDF | PDF Tools | Planned | Medium | — | — | — | PDFTK | https://github.com/Stirling-Tools/Stirling-PDF | PDF editing | General document tools |
| Mealie | Recipes | Planned | Low | — | — | — | Tandoor Recipes | https://github.com/mealie-recipes/mealie | Recipe manager | Household use |
| SparkyFitness | Health and Fitness | Researching | Medium | — | — | — | None | https://github.com/CodeWithCJ/SparkyFitness | Family food, fitness, water, and health tracking | Needs testing; not deployed yet |
| Actual Budget | Finance | Researching | Medium | — | — | — | Firefly III | https://github.com/actualbudget/actual | Personal budgeting | YNAB alternative |
| Karakeep | Knowledge | Planned | High | — | [homelab/docs/services/Karakeep.md](../../homelab/docs/services/Karakeep.md) | — | Hoarder, Linkwarden | https://github.com/karakeep-app/karakeep | AI bookmark manager | Knowledge capture |
| Code Server | Development | Production | High | — | — | — | VS Code Remote | https://github.com/coder/code-server | Browser IDE | Infrastructure development |
| Forgejo | Git | Planned | Medium | — | — | — | Gitea | https://github.com/forgejo/forgejo | Self-hosted Git | Candidate Git platform |
| Gitea | Git | Researching | Medium | — | — | — | Forgejo | https://github.com/go-gitea/gitea | Git hosting | Compared with Forgejo |

---

# Monitoring

| Service | Category | Status | Priority | Last Reviewed | Documentation | Deployment | Alternatives | GitHub | Purpose | Notes |
|---------|----------|--------|----------|---------------|---------------|------------|--------------|--------|---------|-------|
| Beszel | Monitoring | Planned | High | — | [homelab/docs/services/Beszel.md](../../homelab/docs/services/Beszel.md) | — | Netdata | https://github.com/henrygd/beszel | Lightweight monitoring | Primary candidate |
| Grafana | Dashboards | Planned | High | — | — | — | Kibana | https://github.com/grafana/grafana | Dashboards | Visualization |
| Prometheus | Metrics | Planned | High | — | — | — | VictoriaMetrics | https://github.com/prometheus/prometheus | Metrics collection | Grafana backend |
| Uptime Kuma | Uptime | Planned | High | — | — | — | Gatus | https://github.com/louislam/uptime-kuma | Service monitoring | External health checks |
| Glances | Monitoring | Researching | Low | — | — | — | btop | https://github.com/nicolargo/glances | Live system metrics | Useful diagnostics |
| Dozzle | Logging | Planned | Medium | — | — | — | Loki | https://github.com/amir20/dozzle | Docker log viewer | Simple troubleshooting |
| Watchtower | Updates | Researching | Low | — | — | — | Diun | https://github.com/containrrr/watchtower | Automatic container updates | Use with caution |

---

# Future Research

| Service | Category | Status | Priority | Last Reviewed | Documentation | Deployment | Alternatives | GitHub | Purpose | Notes |
|---------|----------|--------|----------|---------------|---------------|------------|--------------|--------|---------|-------|
| Home Assistant | Smart Home | Designed (Phase 12 SoT) | High | 2026-07-31 | Documentation/services/homeassistant/service.md | services/homeassistant/ (ADR-0003) | OpenHAB | https://github.com/home-assistant/core | Home automation | `/mnt/monarch/appdata/homeassistant`; Traefik on proxy |
| Frigate | Security | Researching | High | — | — | — | Shinobi | https://github.com/blakeblackshear/frigate | AI NVR | Coral TPU eventually |
| OpenHands | AI | Researching | Medium | — | — | — | Hermes Agent | https://github.com/All-Hands-AI/OpenHands | Coding agent | Compare with Hermes |
| Langfuse | AI | Researching | Medium | — | — | — | Helicone | https://github.com/langfuse/langfuse | LLM observability | AI analytics |
| Wiki.js | Documentation | Researching | Medium | — | — | — | BookStack | https://github.com/requarks/wiki | Personal wiki | Documentation |
| BookStack | Documentation | Researching | Medium | — | — | — | Wiki.js | https://github.com/BookStackApp/BookStack | Documentation wiki | Alternative |
| Docmost | Documentation | Researching | Medium | — | — | — | Outline | https://github.com/docmost/docmost | Collaborative documentation | Modern docs |
| Linkwarden | Bookmarks | Researching | Medium | — | — | — | Karakeep | https://github.com/linkwarden/linkwarden | Bookmark manager | Compared against Karakeep |
| Hoarder | Bookmarks | Researching | Medium | — | — | — | Karakeep | https://github.com/hoarder-app/hoarder | AI bookmark manager | Compared against Karakeep |
| MCP Gateway | AI Infrastructure | Planned | High | — | — | — | None | https://github.com/hwdsl2/mcp-gateway | Central MCP server | Planned AI architecture |
| Homebox | Inventory | Researching | Low | — | — | — | Snipe-IT | https://github.com/hay-kot/homebox | Home inventory | Track hardware |
| IT-Tools | Utilities | Planned | Low | — | — | — | CyberChef | https://github.com/CorentinTh/it-tools | Developer toolbox | Handy utilities |
| Apache Guacamole | Remote Access | Researching | Medium | — | — | — | RustDesk | https://github.com/apache/guacamole-client | Browser-based RDP/SSH/VNC | Remote management |
| The One File | Planning | Researching | Medium | — | — | — | None | https://github.com/gelatinescreams/The-One-File | Offline-first visual planning and replay for networks, smart homes, and infrastructure | Interesting candidate for rack, network, and facility diagrams |

---

# Review Process

When discovering a new service:

1. Add the service to this document.
2. Assign an initial **Status** and **Priority**.
3. Record the **Last Reviewed** month (`YYYY-MM`).
4. Add known alternatives and any initial notes.
5. If the service moves beyond casual research, create a detailed service document in:

   ```
   homelab/docs/services/
   ```

6. As research continues, update the service's status, notes, and last reviewed date.
7. If the service is deployed:
   - Update the status to **Production**.
   - Set **Documentation** to `homelab/docs/services/<Service>.md`.
   - Set **Deployment** to `homelab/compose/<domain>/<project>/` (or another deployment path).
   - Keep the entry updated as the service evolves.
8. If the service is abandoned or replaced, update its status to **Rejected**, **Replaced**, or **Archived** and record the reason in the Notes column.

This document is the authoritative index of every technology considered for the homelab.

---

# Deployment Lifecycle

```text
Discovered
      │
      ▼
Watching
      │
      ▼
Researching
      │
      ▼
Testing
      │
      ▼
Production
      │
      ├──────────────┐
      ▼              ▼
Replaced         Archived
      │
      ▼
Rejected
```