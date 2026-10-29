# docker-admin — Image Versions (Phase 3)

| Component | Image / Tag | Notes |
| --- | --- | --- |
| docker-admin | `homelab/docker-admin:1.0.0` | Locally built (`Dockerfile`); stdlib-only whitelist HTTP server |
| Base image | `python:3.12-slim` | Pinned major/minor (build pulls latest patch) |
| Docker CLI | host `/usr/bin/docker` | Bind-mounted read-only at runtime (`v29.5.3`) |
| docker compose plugin | host `/usr/libexec/docker/cli-plugins/docker-compose` | Bind-mounted read-only at runtime (`v5.1.4`) |
| Image ID | `sha256:a220fe7ce42db51b2c9052ae6d9963ae39908bf5b42638a73f204d92c7f89740` | Rebuild on `app.py` change |

Last reviewed: 2026-10-06
