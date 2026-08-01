# Phase 14.1 — Rollback Procedure

## A. Restore Open WebUI direct-to-Ollama (fastest chat rollback)

Keeps KORA container but removes it from the chat path.

1. Stop current Open WebUI:

```bash
cd /home/fatherfrank/projects/homelab/services/open-webui
docker compose -f compose.yaml stop
docker compose -f compose.yaml rm -f
```

2. Recreate from legacy compose (or temporary override):

```bash
# Legacy project still at /hive/ollama — ensure open-webui service block exists
cd /hive/ollama
docker compose up -d open-webui
```

Ensure env has `OLLAMA_BASE_URL=http://ollama:11434` and does **not** require KORA.

3. Verify:

```bash
curl -fsSI https://chat.fatherfankscloud.uk/ | head -n1
docker inspect open-webui --format '{{range .Config.Env}}{{println .}}{{end}}' | grep OLLAMA
```

Data at `/mnt/monarch/appdata/open-webui` is retained.

## B. Stop KORA only

```bash
cd /home/fatherfrank/projects/homelab/services/kora
docker compose -f compose.yaml stop
```

Use after A if Open WebUI no longer depends on KORA.

## C. Do not destroy shared network

Never remove `ollama_ollama-net` while Hermes, Honcho, Odysseus, or code-server are attached.

## D. Ollama models

Do not delete `/hive/ollama`. Rollback never requires model wipe.
