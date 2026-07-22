## Dependency Map

### 5.1 Explicit Docker Dependencies

| Service | Depends On |
|---------|------------|
| odysseus | `searxng` (service_healthy), `chromadb` (service_started) |
| *All other services* | No explicit `depends_on` entries |

### 5.2 Logical Operational Dependencies

| Service | Shared Networks / Reverse‑Proxy Relations |
|---------|-------------------------------------------|
| echoos | Connects to external networks `proxy` (Traefik reverse‑proxy) and `ai_net` (shared with AI services). |
| EchoOS | Uses internal network `echoos_net` – isolated. |
| odysseus | Uses external network `ollama-net` (shared with `ollama` service). |
| traefik | Provides `proxy` external network used by many services (e.g., echoos). |
| ollama | Provides `ollama‑net` external network used by odysseus. |
| *All other services* | No network sharing observed (networks not parsed). |