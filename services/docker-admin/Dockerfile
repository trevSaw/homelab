# docker-admin — narrow Docker administration helper (Phase 3)
#
# No Python dependencies beyond the standard library. The Docker CLI and the
# docker compose plugin are bind-mounted read-only from the host at runtime
# (see compose.yaml) so the image ships only the whitelist HTTP server.
FROM python:3.12-slim

# uid 1000 matches the host repo owner so the read-only /repo .env files
# (mode 0600) are readable for Compose variable substitution at runtime.
RUN useradd --uid 1000 --create-home --shell /usr/sbin/nologin admin

COPY app.py /app/app.py
WORKDIR /app

USER 1000:1000
EXPOSE 8765

ENTRYPOINT ["python3", "/app/app.py"]
