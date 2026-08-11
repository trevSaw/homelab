#!/usr/bin/env bash
# KORA-as-Agent staging prototype — bootstrap (isolated, disposable).
# Usage:
#   ./bootstrap.sh          # (re)create + start staging stack
#   ./bootstrap.sh down     # tear down containers (keeps ./data)
#   ./bootstrap.sh destroy  # tear down AND remove ./data (full disposal)
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PROJECT="kora-hermes-staging"
API=http://127.0.0.1:28642

if [ "${1:-}" = "down" ]; then
  docker compose -p "$PROJECT" down
  exit 0
fi
if [ "${1:-}" = "destroy" ]; then
  docker compose -p "$PROJECT" down -v
  rm -rf data
  exit 0
fi

mkdir -p data

echo "==> [1/5] Seed staging Hermes config (base = production v0.17.0 config, no secrets)"
if [ ! -f data/config.yaml ]; then
  if docker cp hermes:/opt/data/config.yaml data/config.yaml 2>/dev/null; then
    echo "    copied production config.yaml as base"
  else
    echo "    WARNING: could not copy production config; writing minimal config"
    cat > data/config.yaml <<'YAML'
model:
  default: 'qwen3:8b'
  provider: custom
  base_url: http://ollama:11434/v1
YAML
  fi
fi
python3 - <<'PY'
import yaml
p = "data/config.yaml"
cfg = yaml.safe_load(open(p)) or {}
cfg.setdefault("model", {})["default"] = "qwen3:8b"
cfg["model"]["provider"] = "custom"
cfg["model"]["base_url"] = "http://ollama:11434/v1"
cfg["model"]["context_length"] = 64000
cfg["model"]["ollama_num_ctx"] = 64000
cfg.setdefault("plugins", {})["enabled"] = ["kora"]
cfg.setdefault("agent", {})["reasoning_effort"] = "none"
yaml.safe_dump(cfg, open(p, "w"), sort_keys=False)
print("    patched model/plugins/reasoning")
PY

echo "==> [2/5] Copy KORA agent plugin into staging Hermes plugin dir"
rm -rf data/plugins
mkdir -p data/plugins
cp -r plugins/kora data/plugins/kora

echo "==> [3/5] Build + start isolated staging stack"
docker compose -p "$PROJECT" up -d

echo "==> [4/5] Wait for Hermes API server + staging Chroma"
for i in $(seq 1 60); do
  if curl -fsS "$API/health" >/dev/null 2>&1; then
    echo "    Hermes API server up after ${i}s"
    break
  fi
  sleep 1
done
curl -fsS "$API/health" >/dev/null 2>&1 || { echo "FAIL: Hermes API not up"; docker compose -p "$PROJECT" logs --tail=50 hermes; exit 1; }

echo "==> [5/5] Pin KORA toolset + reasoning (Hermes rewrites config at startup)"
docker compose -p "$PROJECT" exec -T hermes sh -c 'chmod 666 /opt/data/config.yaml
python3 - <<PY
import yaml
p = "/opt/data/config.yaml"
cfg = yaml.safe_load(open(p)) or {}
cfg.setdefault("plugins", {})["enabled"] = ["kora"]
cfg.setdefault("platform_toolsets", {})["api_server"] = ["kora"]
cfg.setdefault("agent", {})["reasoning_effort"] = "none"
yaml.safe_dump(cfg, open(p, "w"), sort_keys=False)
PY
chmod 444 /opt/data/config.yaml' || true
docker compose -p "$PROJECT" restart hermes
sleep 20
for i in $(seq 1 40); do
  if curl -fsS "$API/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -fsS "$API/health" >/dev/null 2>&1 || { echo "FAIL: Hermes API not up after pin"; exit 1; }

echo "==> Staging ready."
echo "    Hermes API server : $API  (API_SERVER_KEY=staging-kora-key)"
echo "    Staging Chroma    : http://127.0.0.1:28644"
echo "    Run minimal tests : pytest tests/test_kora_hermes.py -v"
echo "    Teardown          : ./bootstrap.sh down   (destroy: ./bootstrap.sh destroy)"
