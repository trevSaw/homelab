# KORA Task Bridge — OpenCode execution worker bridge.
#
# Runs the bridge service (REST + Streamable HTTP MCP) and executes OpenCode
# tasks against the mounted canonical homelab repository. No docker.sock is
# exposed; read-only Docker state snapshots are mounted separately.
#
# OpenCode and docker-compose binaries are pinned to exact release versions and
# verified by SHA-256 at build time (deterministic, reproducible from a clean
# checkout — no host binaries are copied into the image). To upgrade, bump the
# ARG values + hashes below.
#   opencode        1.18.32  (anomalyco/opencode release, glibc x64)
#   docker-compose  5.1.4    (docker/compose release, standalone x86_64)
FROM python:3.12-slim

ARG OPENCODE_VERSION=1.18.32
ARG OPENCODE_ARCHIVE_SHA256=3046e0404fdc60fb80307e7a47824ba07477364178a4d09baa8548496dd6d43b
ARG COMPOSE_VERSION=5.1.4
ARG COMPOSE_BIN_SHA256=33b208d7e76639db742fae84b966cc01dacae58ca3fc4dabbc907045aefdf0c4
ARG MCP_VERSION=1.26.0
ARG FASTAPI_VERSION=0.115.12
ARG UVICORN_VERSION=0.34.0

# Worker binaries (pinned releases, sha256-verified) + bridge dependencies.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl ca-certificates \
    && curl -fsSL -o /tmp/opencode.tar.gz \
        "https://github.com/anomalyco/opencode/releases/download/v${OPENCODE_VERSION}/opencode-linux-x64.tar.gz" \
    && echo "${OPENCODE_ARCHIVE_SHA256}  /tmp/opencode.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/opencode.tar.gz -C /usr/local/bin opencode \
    && rm /tmp/opencode.tar.gz \
    && curl -fsSL -o /usr/local/bin/docker-compose \
        "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
    && echo "${COMPOSE_BIN_SHA256}  /usr/local/bin/docker-compose" | sha256sum -c - \
    && chmod +x /usr/local/bin/opencode /usr/local/bin/docker-compose \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir \
        "mcp==${MCP_VERSION}" \
        "fastapi==${FASTAPI_VERSION}" \
        "uvicorn==${UVICORN_VERSION}"

# Bridge application + OpenCode worker config/rules/prompts.
COPY src /opt/taskbridge/src
COPY opencode/opencode.jsonc /opt/taskbridge/etc/opencode.jsonc
COPY opencode/rules/KORA-WORKER.md /opt/taskbridge/etc/rules/KORA-WORKER.md
COPY opencode/prompts/worker-readonly.md /opt/taskbridge/etc/prompts/worker-readonly.md
COPY opencode/prompts/worker-testwrite.md /opt/taskbridge/etc/prompts/worker-testwrite.md
COPY opencode/prompts/worker-write.md /opt/taskbridge/etc/prompts/worker-write.md

# Non-root worker user (uid 1000 == repo owner fatherfrank on the host, so
# file writes through the /workspace mount are owned correctly).
RUN useradd --create-home --uid 1000 taskworker

# Data/state directories (persistent volume mounted at /opt/taskbridge/data).
RUN mkdir -p /opt/taskbridge/data /opt/taskbridge/home \
    && chown -R 1000:1000 /opt/taskbridge

USER 1000:1000
WORKDIR /opt/taskbridge

EXPOSE 8643

ENV PYTHONPATH=/opt/taskbridge/src \
    HOME=/opt/taskbridge/home \
    OPENCODE_CONFIG=/opt/taskbridge/etc/opencode.jsonc \
    TASKBRIDGE_DATA=/opt/taskbridge/data

CMD ["uvicorn", "taskbridge.main:app", "--host", "0.0.0.0", "--port", "8643", "--log-level", "info"]