#!/usr/bin/env bash
# Phase 14.1 Solo stack startup helper (documented order).
# Does not tear down legacy /hive/ollama project automatically.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "==> Ensuring appdata directories"
sudo mkdir -p /mnt/monarch/appdata/kora /mnt/monarch/appdata/open-webui

echo "==> 1/4 Ollama"
cd "$ROOT/services/ollama"
cp -n .env.example .env || true
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d

echo "==> 2/4 KORA Runtime"
cd "$ROOT/services/kora"
cp -n .env.example .env || true
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d --build

echo "==> 3/4 Hermes (thin layer; optional for Solo chat)"
cd "$ROOT/services/hermes"
cp -n .env.example .env || true
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d

echo "==> 4/4 Open WebUI"
cd "$ROOT/services/open-webui"
cp -n .env.example .env || true
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d

echo "==> Done. Validate with Validation/Phase14.1/ scripts / checklists."
