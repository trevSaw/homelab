# Open WebUI recovery and upgrade guide

This guide documents steps to fix "stuck thinking," migration/ChromaDB errors, and stale config after upgrading Open WebUI (e.g. to v0.7.x) when running with Docker Compose, PostgreSQL, and Redis.

---

## 1. Context: what can go wrong

- **Stuck thinking** – UI hangs on "thinking" when chatting. Common causes:
  - Open WebUI talking to the wrong backend (e.g. `localhost:4000`, `litellm:4000`) instead of `http://ollama:11434`.
  - Config coming from Redis/DB instead of environment variables.
  - Database connection timeouts during LLM calls (fixed in v0.7.2).
- **Multiple workers** – With `UVICORN_WORKERS=4`, OAuth can hit "mismatching_state" (different workers handle login vs callback). Also increases risk of DB/connection issues.
- **ChromaDB schema mismatch** – After upgrading, you may see:
  - `chromadb.errors.InternalError: duplicate column name: schema_str`
  - One or more workers crash; RAG/knowledge-base requests can hang or fail.
- **Stale Redis config** – Old API URLs and connection config cached in Redis override env and can break or hang requests.

---

## 2. Compose / environment recommendations

Use these in your `open-webui` service so env wins over DB/Redis and stability is better:

```yaml
environment:
  # Force env over DB/Redis-stored connections
  - ENABLE_PERSISTENT_CONFIG=false
  - OLLAMA_BASE_URL=http://ollama:11434
  - OLLAMA_BASE_URLS=http://ollama:11434
  # Single worker: avoids OAuth state issues and connection/session problems(optional)
  - UVICORN_WORKERS=1
  # Fail fast on bad connections instead of hanging (optional)
  - AIOHTTP_CLIENT_TIMEOUT=60
  - AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST=10
```

- Pin the image to a release (e.g. `ghcr.io/open-webui/open-webui:v0.7.2`) if you want predictable upgrades; `main` is fine if you accept moving targets.
- For Microsoft OAuth logout, set `OPENID_PROVIDER_URL` to your provider’s OpenID discovery URL (e.g. `https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration`).

---

## 3. Backup before upgrades

Always backup key volumes before upgrading (DB schema and app data can change).

**Volumes to backup (examples):**

- `open-webui` – app data, uploads, cache (not models).
- `llm_postgres-data` (or your Postgres volume) – users, chats, knowledge base metadata.
- `redis-data` – optional; can be recreated.

**Example backup script (run from the directory containing your compose file):**

```bash
# Set variables to match your stack
COMPOSE_FILE=/opt/stacks/llm/compose.yml   # or your path
PROJECT_NAME=llm                            # or your compose project name
BACKUP_ROOT=/opt/stacks/llm/backups
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="$BACKUP_ROOT/backup-${PROJECT_NAME}-${TIMESTAMP}"

mkdir -p "$BACKUP_PATH"
cd "$BACKUP_PATH"

for vol in open-webui llm_postgres-data redis-data; do
  full_name="${PROJECT_NAME}_${vol}"
  if docker volume inspect "$full_name" &>/dev/null; then
    echo "Backing up $full_name ..."
    docker run --rm -v "$full_name:/data:ro" -v "$(pwd):/backup" alpine \
      tar czf "/backup/${vol}.tar.gz" -C /data .
  fi
done
```

Ollama/model volumes can be skipped; models can be re-pulled.

---

## 4. Upgrading the stack

From the directory containing your compose file:

```bash
docker compose pull
docker compose up -d
```

Or with an explicit file:

```bash
docker compose -f /opt/stacks/llm/compose.yml pull
docker compose -f /opt/stacks/llm/compose.yml up -d
```

Open WebUI runs DB migrations on startup. If release notes mention "schema change, update all instances at once," bring all instances up in one go (no rolling update with mixed versions).

---

## 5. Fixing ChromaDB schema errors and clearing stale config

If after upgrade you see ChromaDB errors (e.g. `duplicate column name: schema_str`) or workers crashing, and/or you want to clear Redis-backed config so env is used:

### 5.1 Stop Open WebUI

```bash
sudo docker compose -f /opt/stacks/llm/compose.yml stop open-webui
```

(Adjust path and project name to match your setup.)

### 5.2 Remove ChromaDB data (resets RAG vector index only)

This deletes only the vector index. Knowledge base definitions and uploaded files stay; you will need to re-index later (see section 7).

```bash
# Replace 'llm_open-webui' with your project volume name if different (e.g. myproject_open-webui)
sudo docker run --rm -v llm_open-webui:/data alpine sh -c '
  rm -rf /data/chroma /data/vector_db /data/cache/chroma 2>/dev/null
  ls -la /data/
'
```

### 5.3 Start Open WebUI again

```bash
sudo docker compose -f /opt/stacks/llm/compose.yml up -d open-webui
```

### 5.4 Flush Redis and restart Open WebUI

This clears cached config (API URLs, connection settings) so the app uses environment variables and freshly configured connections.

```bash
sudo docker exec redis-valkey redis-cli FLUSHDB
sudo docker compose -f /opt/stacks/llm/compose.yml restart open-webui
```

**Note:** If Redis is shared with other apps, use a different DB number for Open WebUI or delete only Open WebUI keys instead of `FLUSHDB`.

---

## 6. Re-adding API connections after Redis flush

After `FLUSHDB`, connections that were only in Redis (e.g. OpenAI, LiteLLM for Grok) disappear. Re-add them in the UI:

1. Log in as admin.
2. Go to **Admin Panel** → **Connections** (or **Settings** → **Connections** / **API Connections**).
3. Add each connection again, for example:
   - **OpenAI (ChatGPT):** Base URL `https://api.openai.com/v1`, API key from your env or secrets.
   - **LiteLLM (Grok / others):** If you run LiteLLM (e.g. at `http://litellm:4000` or `http://localhost:4000`), add an OpenAI-compatible connection with that URL and any required key.

If LiteLLM used to run at `localhost:4000` and is no longer running, start that service again, then add the connection.

---

## 7. Re-indexing knowledge bases (after ChromaDB clear)

If you cleared ChromaDB (section 5.2), RAG/knowledge-base search will be empty until you re-index:

1. Log in (as admin or as the user who owns the knowledge bases).
2. Open **Workspace** → **Knowledge** (or **Documents** / **Knowledge bases**).
3. For each knowledge base:
   - Open the collection.
   - Use **Re-index**, **Process**, or **Rebuild index** (wording varies by version) and wait for it to finish.

Re-indexing rebuilds the vector index from the existing documents; it does not restore a backup of the old index. End result is equivalent for users.

---

## 8. Verifying the instance

- Check that the container is running:
  ```bash
  docker compose -f /opt/stacks/llm/compose.yml ps
  ```
- Check logs for errors (e.g. no ChromaDB or migration failures):
  ```bash
  docker logs open-webui --tail 100
  ```
- Try a normal chat (without RAG); confirm it completes without hanging.
- If you use RAG, try a query that uses a knowledge base after re-indexing.

---

## 9. Quick reference: full recovery sequence

1. **Backup** – Run your volume backup (section 3).
2. **Compose** – Ensure env has `ENABLE_PERSISTENT_CONFIG=false`, `OLLAMA_BASE_URL(S)`, `UVICORN_WORKERS=1`, and timeouts (section 2).
3. **Upgrade** – `docker compose pull` and `docker compose up -d` (section 4).
4. **If ChromaDB errors or stale config:** Stop open-webui → clear ChromaDB paths (section 5.2) → start open-webui → `FLUSHDB` → restart open-webui (sections 5.1–5.4).
5. **Re-add connections** in Admin → Connections (section 6).
6. **Re-index** knowledge bases in Workspace → Knowledge (section 7).
7. **Verify** with logs and a test chat (section 8).

---

## 10. Restoring a volume from backup

If you need to restore a volume from a backup created as in section 3:

```bash
# Stop the service that uses the volume first
docker compose -f /path/to/compose.yml stop open-webui

# Restore (example: open-webui volume from backup)
docker run --rm -v llm_open-webui:/data -v /path/to/backup-llm-YYYYMMDD-HHMMSS:/backup alpine sh -c '
  cd /data && tar xzf /backup/open-webui.tar.gz
'

# Start again
docker compose -f /path/to/compose.yml up -d open-webui
```

Use the appropriate volume name and backup path for your project.
