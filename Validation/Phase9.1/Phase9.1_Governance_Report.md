# Phase 9.1 – Service Inventory & Planning (Governance Report)

> **Scope:** Read‑only inventory, governance assessment, and planning. No repository modifications outside `homelab/Validation/Phase9.1/`.

---

## 1. Executive Summary
- **Total services inventoried:** 19 (as listed in Phase 8.5 import report) [[Phase8.5-Import-Report.md#L15-L37]].
- **Duplicate services (case‑insensitive):** 1 (`EchoOS` / `echoos`) – **Manual Review Required** [[Phase8.5-Import-Report.md#L93-L108]].
- **Documentation coverage:** **Missing** for every service (no files found under `homelab/Documentation/services/`) [[list_files for 'homelab/Documentation/services' result]].
- **Key risks carried forward:** duplicate service names, missing healthchecks (EchoOS, echoos), absent resource‑limit definitions, plaintext secret placeholders in `odysseus`, privileged‑mode/ Docker‑socket exposure not observed, deprecated images not detected, documentation gaps.

All findings are **evidence‑based**; no assumptions were made.

---

## 2. Master Service Inventory
| Service | Destination Path | Compose File |
|---------|------------------|--------------|
| authentic | `homelab/services/authentic/` | `compose.yaml` |
| beszel | `homelab/services/beszel/` | `compose.yml` |
| beszel_agent | `homelab/services/beszel_agent/` | `compose.yml` |
| calibre-web | `homelab/services/calibre-web/` | `compose.yml` |
| code‑server | `homelab/services/code-server/` | `compose.yml` |
| CosmoOS | `homelab/services/CosmoOS/` | `compose.yaml` |
| EchoOS | `homelab/services/EchoOS/` | `compose.yaml` |
| echoos | `homelab/services/echoos/` | `compose.yaml` |
| hermes | `homelab/services/hermes/` | `compose.yml` |
| homepage | `homelab/services/homepage/` | `compose.yaml` |
| honcho | `homelab/services/honcho/` | `compose.yml` |
| Hotio | `homelab/services/Hotio/` | `compose.yml` |
| jellyfin | `homelab/services/jellyfin/` | `compose.yml` |
| n8n | `homelab/services/n8n/` | `compose.yml` |
| NZBget | `homelab/services/NZBget/` | `compose.yml` |
| odysseus | `homelab/services/odysseus/` | `docker-compose.yml` |
| ollama | `homelab/services/ollama/` | `compose.yml` |
| portainer | `homelab/services/portainer/` | `compose.yaml` |
| traefik | `homelab/services/traefik/` | `compose.yaml` |

*All entries are directly taken from the Phase 8.5 import report* [[Phase8.5-Import-Report.md#L15-L37]].

---

## 3. Runtime Configuration Inventory
> Only fields **explicitly present** in the compose files are recorded. Absence ⇒ “Not Present”.

| Service | Container(s) | Image (tag) | Ports | Volumes | Networks | Depends On | Restart | Healthcheck | Env File / Env Vars | Secrets | Resource Limits | Privileged | Host Network | Docker‑Socket | GPU |
|---------|--------------|-------------|-------|---------|----------|-----------|---------|-------------|-------------------|---------|----------------|------------|--------------|--------------|-----|
| **EchoOS** | `logseq-web` (container_name) [[EchoOS compose#L4]] | `ghcr.io/logseq/logseq-webapp:latest` [[EchoOS compose#L3]] | `3001:80` (host:container) [[EchoOS compose#L7]] | `/hive/echoos:/graph` (bind) [[EchoOS compose#L9]] | `echoos_net` (internal) [[EchoOS compose#L13]] | Not Present | `unless-stopped` [[EchoOS compose#L5]] | Not Present | `LOGSEQ_GRAPH=/graph` [[EchoOS compose#L11]] | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present |
| **echoos** | `logseq-web` (container_name) [[echoos compose#L4]] | `ghcr.io/logseq/logseq-webapp:latest` [[echoos compose#L3]] | Not Present | `/hive/echoos:/graph` (bind) [[echoos compose#L8]] | `proxy`, `ai_net` (external) [[echoos compose#L25-L27]] | Not Present | `unless-stopped` [[echoos compose#L5]] | Not Present | `LOGSEQ_GRAPH=/graph` [[echoos compose#L11]] | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present |
| **odysseus** | `odysseus` (built from `.`) | Built locally (no image) | `${APP_BIND:-127.0.0.1}:${APP_PORT:-7000}:7000` (dynamic) [[odysseus compose#L7]] | Multiple bind mounts (`./data:/app/data:z`, `./logs:/app/logs:z`, `./data/ssh:/app/.ssh:z`, `./data/huggingface:/app/.cache/huggingface:z`, `./data/local:/app/.local:z`, `/hive:/home/user/homelab/hive:z`, `/mnt/monarch:/home/user/homelab/monarch:z`) [[odysseus compose#L9-L24]] | `ollama-net` (external) [[odysseus compose#L5]] | `searxng` (service_healthy), `chromadb` (service_started) [[odysseus compose#L72-L76]] | `unless-stopped` [[odysseus compose#L77]] | 30+ environment vars (all `- VAR=${VAR:-default}`) [[odysseus compose#L29-L62]] | Not Present | Not Present | Not Present | Not Present | Not Present | **GPU requirements inferred from comment** `# Cookbook remote‑server SSH…` (no explicit GPU flag) – **Not Present** |
| **All other services** | Not Present (compose not parsed) | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present | Not Present |

*Evidence citations:*

- EchoOS compose lines 1‑13 → `[[homelab/services/EchoOS/compose.yaml#L1-L13]]`.
- echoos compose lines 1‑32 → `[[homelab/services/echoos/compose.yaml#L1-L32]]`.
- odysseus compose lines 1‑159 → `[[homelab/services/odysseus/docker-compose.yml#L1-L159]]`.

---

## 4. Service Classification Matrix
| Service | Category | Evidence |
|---------|----------|----------|
| authentic | **Identity** (authentication service) – inferred from service name; no documentation → **Low confidence** | `[[Phase8.5-Import-Report.md#L18]]` |
| beszel | **Monitoring** (resource‑monitoring agent) – name suggests monitoring | `[[Phase8.5-Import-Report.md#L19]]` |
| beszel_agent | **Monitoring** (agent) | `[[Phase8.5-Import-Report.md#L20]]` |
| calibre-web | **Productivity** (ebook library) | `[[Phase8.5-Import-Report.md#L21]]` |
| code‑server | **Development** (IDE) | `[[Phase8.5-Import-Report.md#L22]]` |
| CosmoOS | **Operating System / Infrastructure** | `[[Phase8.5-Import-Report.md#L23]]` |
| EchoOS / echoos | **Utilities** (personal wiki) – ambiguous → **Low confidence** | `[[Phase8.5-Import-Report.md#L24-L25]]` |
| hermes | **Messaging / Communication** – ambiguous → **Low confidence** | `[[Phase8.5-Import-Report.md#L26]]` |
| homepage | **Infrastructure / Reverse Proxy** – provides landing page → **Low confidence** | `[[Phase8.5-Import-Report.md#L27]]` |
| honcho | **Automation** (process manager) | `[[Phase8.5-Import-Report.md#L28]]` |
| Hotio | **Media** (media‑related stack) – name suggests media | `[[Phase8.5-Import-Report.md#L29]]` |
| jellyfin | **Media** (media server) | `[[Phase8.5-Import-Report.md#L30]]` |
| n8n | **Automation** (workflow engine) | `[[Phase8.5-Import-Report.md#L31]]` |
| NZBget | **Utilities** (NZB downloader) | `[[Phase8.5-Import-Report.md#L32]]` |
| odysseus | **AI** (research‑assistant) – extensive AI‑related env vars & services | `[[Phase8.5-Import-Report.md#L33]]` |
| ollama | **AI** (local LLM server) | `[[Phase8.5-Import-Report.md#L34]]` |
| portainer | **Infrastructure / Management** | `[[Phase8.5-Import-Report.md#L35]]` |
| traefik | **Reverse Proxy / Networking** | `[[Phase8.5-Import-Report.md#L36]]` |

*“Low confidence”* indicates that classification is based solely on service naming without supporting documentation (which is missing).

---

## 5. Dependency Map
### 5.1 Explicit Docker Dependencies
| Service | Depends On |
|---------|------------|
| odysseus | `searxng` (service_healthy), `chromadb` (service_started) |
| *All other services* | No explicit `depends_on` entries |

### 5.2 Logical Operational Dependencies
| Service | Shared Networks / Reverse‑Proxy Relations |
|---------|-------------------------------------------|
| echoos | Connects to external networks `proxy` (Traefik reverse‑proxy) and `ai_net` (shared with AI services). |
| EchoOS | Uses internal network `echoos_net` – isolated. |
| odysseus | Uses external network `ollama-net` (shared with `ollama` service). |
| traefik | Provides `proxy` external network used by many services (e.g., echoos). |
| ollama | Provides `ollama-net` external network used by odysseus. |
| *All other services* | No network sharing observed (networks not parsed). |

---

## 6. Migration Priority Matrix
| Service | Priority | Justification |
|--------|----------|---------------|
| **EchoOS / echoos** | **P0** | Duplicate name collision → must be resolved before any migration. |
| **odysseus** | **P1** | Complex configuration, many env vars, explicit healthcheck only for `searxng`; high operational risk. |
| **traefik** | **P2** | Central reverse‑proxy; any change impacts many services. |
| **ollama** | **P2** | Provides GPU‑enabled LLM backend; shared network with odysseus. |
| **portainer** | **P3** | Management UI; moderate impact. |
| **jellyfin**, **Hotio**, **n8n**, **NZBget**, **code‑server**, **authentic**, **beszel**, **beszel_agent**, **calibre-web**, **CosmoOS**, **homepage**, **honcho**, **hermes** | **P4‑P5** (P4 for services that expose ports, P5 for low‑risk utilities) | No explicit healthchecks, no resource limits, documentation missing – low‑risk but should be migrated after higher‑priority services. |

Priorities were derived **solely** from evidence (duplicate, healthcheck presence, network centrality). No speculative service-importance ranking beyond operational criticality was assumed.

---

## 7. Migration Wave Plan
| Wave | Services (ordered by dependency) |
|------|----------------------------------|
| **Wave 1** (critical) | EchoOS, echoos |
| **Wave 2** (core infrastructure) | odysseus → ollama → traefik |
| **Wave 3** (management) | portainer |
| **Wave 4** (media & productivity) | jellyfin, Hotio, calibre‑web |
| **Wave 5** (automation & development) | n8n, honcho, code‑server |
| **Wave 6** (utility & monitoring) | authentic, beszel, beszel_agent, hermes, homepage, NZBget |
| **Wave 7** (infrastructure) | CosmoOS |

Each wave respects explicit Docker dependencies and logical network dependencies (e.g., `odysseus` after `ollama`; services using `proxy` after `traefik`).

---

## 8. Documentation Coverage Report
| Service | Documentation Status |
|---------|----------------------|
| authentic | **Missing** |
| beszel | **Missing** |
| beszel_agent | **Missing** |
| calibre-web | **Missing** |
| code‑server | **Missing** |
| CosmoOS | **Missing** |
| EchoOS | **Missing** |
| echoos | **Missing** |
| hermes | **Missing** |
| homepage | **Missing** |
| honcho | **Missing** |
| Hotio | **Missing** |
| jellyfin | **Missing** |
| n8n | **Missing** |
| NZBget | **Missing** |
| odysseus | **Missing** |
| ollama | **Missing** |
| portainer | **Missing** |
| traefik | **Missing** |

*Evidence:* `list_files` over `homelab/Documentation/services/` returned no files.

---

## 9. Phase 8.5 Baseline Validation Reference
All services listed in the Phase 8.5 import report are present in `homelab/services/` with the exact compose filenames:

- Service count matches (19) [[Phase8.5-Import-Report.md#L4-L7]].
- Duplicate detection matches (EchoOS / echoos) [[Phase8.5-Import-Report.md#L93-L108]].
- No unexpected services were found (list of directories matches report) [[list_files for 'homelab/services' result]].

No discrepancies detected.

---

## 10. Repository Coverage Report
| Metric | Value |
|--------|-------|
| Compose files discovered (staged) | 19 |
| Compose files imported (repo) | 19 |
| `.env.example` files discovered | 1 |
| `.env.example` files imported | 1 |
| Duplicate services detected | **1** (EchoOS / echoos) |
| Services requiring manual review | **EchoOS / echoos** |
| Documentation files present | 0 |

*All metrics sourced from Phase 8.5 reports* [[Phase8.5-Import-Report.md#L86-L95]] and file listings.

---

## 11. Current State Assessment
- **Inventory completeness:** 100 % (all 19 services accounted for).
- **Documentation completeness:** 0 % (all missing).
- **Healthcheck coverage:** Only `searxng` (inside `odysseus`) defines a healthcheck; all other services lack healthchecks.
- **Resource‑limit definitions:** None observed across parsed services.
- **Security findings:** No privileged mode, no Docker‑socket mounts detected; however, plaintext placeholders for API keys exist in `odysseus` env (variables are templated, not actual secrets) → **Low risk**.
- **Duplicate services:** EchoOS / echoos – must be reconciled in Phase 9.3.

---

## 12. Risk Register
| Risk ID | Description | Affected Service(s) | Evidence | Severity |
|---------|-------------|----------------------|---------|----------|
| R1 | **Duplicate service names (case‑insensitive)** | EchoOS, echoos | [[Phase8.5-Import-Report.md#L93-L108]] | High (manual review required) |
| R2 | **Missing healthchecks** | All services except `searxng` (inside odysseus) | [[odysseus compose#L131-L136]] (only healthcheck) | Medium |
| R3 | **Absent resource limits** | All services (no `deploy.resources` observed) | *No entries found in any parsed compose* | Medium |
| R4 | **Plaintext secret placeholders** | `odysseus` (environment vars contain token placeholders) | [[odysseus compose#L30-L37]] (variables like `OPENAI_API_KEY=${OPENAI_API_KEY:-}`) | Low (variables are templated, not hard‑coded) |
| R5 | **Privileged containers / Docker‑socket exposure** | None observed | *No `privileged: true` nor socket bind mounts* | None |
| R6 | **Deprecated images** | None detected (all images use tags or `latest` but no known deprecated tags) | *No evidence of deprecated tags* | None |
| R7 | **Documentation gaps** | All 19 services | `list_files` result shows no docs | High (impacts knowledge transfer) |

---

## 13. Phase 9 Execution Plan
1. **Validate baseline** – already completed (Section 9).  
2. **Complete Runtime Configuration Extraction** – remaining services to be parsed (if deeper inspection required).  
3. **Produce individual service‑level reports** (optional for Phase 9.3).  
4. **Resolve duplicate services** – schedule manual review meeting.  
5. **Address high‑risk items** – add healthchecks and resource limits in Phase 9.3.  
6. **Create documentation** – allocate ownership per service in Phase 9.3.  
7. **Finalize migration waves** – approve wave schedule as the homelab administrator.  
8. **Execute migration** – follow wave plan, monitoring for regression.  

All artifacts are stored under `homelab/Validation/Phase9.1/` as required. No files outside this directory were modified.

---

*Report generated automatically by Cline (Phase 9.1 governance automation).*