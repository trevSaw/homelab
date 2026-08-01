# Phase 14.1 — Deployment Guide

## Prerequisites

- Docker networks: `proxy`, `ollama_ollama-net`, `ai-assistant`
- Model store: `/hive/ollama`
- UI data: `/mnt/monarch/appdata/open-webui`
- KORA data: `/mnt/monarch/appdata/kora`

## Startup order

1. Ollama  
2. KORA Runtime  
3. Hermes (thin; optional for Solo chat)  
4. Open WebUI  

Helper: `services/kora/scripts/start-solo-stack.sh`

## Manual steps

```bash
sudo mkdir -p /mnt/monarch/appdata/kora

cd /home/fatherfrank/projects/homelab/services/ollama
cp -n .env.example .env   # set OLLAMA_API_KEY from legacy env
docker compose -f compose.yaml up -d

cd ../kora
cp -n .env.example .env
docker compose -f compose.yaml up -d --build

cd ../hermes
cp -n .env.example .env   # set dashboard password
docker compose -f compose.yaml up -d

cd ../open-webui
cp -n .env.example .env   # set WEBUI_SECRET_KEY from legacy env
docker compose -f compose.yaml up -d
```

## Smoke checks

```bash
docker exec kora python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health').read().decode())"
curl -fsSI https://chat.fatherfankscloud.uk/ | head -n1
docker exec ollama ollama list | head
```

## Notes

- Do not `compose down` the legacy `/hive/ollama` project without confirming dependents still use `ollama_ollama-net`.
- Open WebUI must not re-enable direct Ollama as the production default.
