# Task Bridge — Image Versions (Phase 21)

| Component | Version | Notes |
| --- | --- | --- |
| Image | `homelab/taskbridge:1.0.0` | Locally built (Dockerfile) |
| Base image | `python:3.12-slim` | Pinned major/minor (build pulls latest patch) |
| OpenCode worker binary | `1.18.32` | **Pinned in-image** via Dockerfile ARG + SHA-256 (anomalyco/opencode release `opencode-linux-x64.tar.gz`) |
| docker-compose (validation) | `v5.1.4` | **Pinned in-image** via Dockerfile ARG + SHA-256 (docker/compose release `docker-compose-linux-x86_64`) |
| Python packages | `mcp==1.26.0`, `fastapi==0.115.12`, `uvicorn==0.34.0` | Pinned in Dockerfile ARGs |
| Worker model | `gpt-oss:20b-cloud` (via Ollama) | Override via `TASKBRIDGE_MODEL` |

To upgrade a pinned binary, bump the version + SHA-256 ARGs in `Dockerfile`.

Last reviewed: 2026-09-23