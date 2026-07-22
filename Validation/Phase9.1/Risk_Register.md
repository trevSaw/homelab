## Risk Register

| Risk ID | Description | Affected Service(s) | Evidence | Severity |
|---------|-------------|----------------------|---------|----------|
| R1 | **Duplicate service names (case‑insensitive)** | EchoOS, echoos | `[[Phase8.5-Import-Report.md#L93-L108]]` | High (manual review required) |
| R2 | **Missing healthchecks** | All services except `searxng` (inside odysseus) | `[[odysseus compose#L131-L136]]` (only healthcheck) | Medium |
| R3 | **Absent resource limits** | All services (no `deploy.resources` observed) | *No entries found in any parsed compose* | Medium |
| R4 | **Plaintext secret placeholders** | `odysseus` (environment vars contain token placeholders) | `[[odysseus compose#L30-L37]]` (variables like `OPENAI_API_KEY=${OPENAI_API_KEY:-}`) | Low (variables are templated, not hard‑coded) |
| R5 | **Privileged containers / Docker‑socket exposure** | None observed | *No `privileged: true` nor socket bind mounts* | None |
| R6 | **Deprecated images** | None detected (all images use tags or `latest` but no known deprecated tags) | *No evidence of deprecated tags* | None |
| R7 | **Documentation gaps** | All 19 services | `list_files` result shows no docs | High (impacts knowledge transfer) |