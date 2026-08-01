# Phase 14.1 — Compose Validation

## Files validated

| Project | File | `docker compose config` |
| --- | --- | --- |
| kora | `services/kora/compose.yaml` | Pass |
| open-webui | `services/open-webui/compose.yaml` | Pass |
| ollama | `services/ollama/compose.yaml` | Pass |
| hermes | `services/hermes/compose.yaml` | Pass |

## Governance checklist

| Requirement | kora | open-webui | ollama | hermes |
| --- | --- | --- | --- | --- |
| restart policy | yes | yes | yes | yes |
| resource limits | yes | yes | yes | yes |
| healthcheck | yes | yes | yes | yes |
| logging max-size | yes | yes | yes | yes |
| labels | yes | yes | yes | yes |
| external/proxy networks | yes | yes | yes* | yes |
| `.env.example` | yes | yes | yes | yes |
| `README.md` / `Versions.md` | yes | yes | yes | yes |

\* Ollama still **defines** `ollama_ollama-net` (named) so the shared AI network remains creatable from this SoT; dependents reference it as external.

## Exceptions documented

- Hermes image remains `:latest` pending digest pin
- Ollama GPU reservation retained
- KORA Traefik disabled (UI-only ingress on Open WebUI)
- Cross-project `depends_on` omitted (documented startup order)
