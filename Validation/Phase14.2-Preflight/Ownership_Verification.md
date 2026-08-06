# Ownership Verification — Phase 14.2 Preflight

Recorded 2026-08-01 after migration:

| Container | Compose workdir | Config file | Health |
| --- | --- | --- | --- |
| ollama | `.../services/ollama` | `services/ollama/compose.yaml` | healthy |
| hermes | `.../services/hermes` | `services/hermes/compose.yaml` | healthy |
| open-webui | `.../services/open-webui` | `services/open-webui/compose.yaml` | healthy |
| kora | `.../services/kora` | `services/kora/compose.yaml` | healthy |

Legacy compose disabled:

- `/hive/ollama/compose.yml.DISABLED-use-services-ollama`
- `/mnt/monarch/appdata/hermes/compose.yml.DISABLED-use-services-hermes`
