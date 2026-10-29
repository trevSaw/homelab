# KORA plugin (canonical source)

This directory is the **tracked canonical source** for the KORA Hermes plugin.
At runtime Hermes loads the plugin from the Hermes volume:

```
services/hermes/plugin/kora/   →   container: /opt/data/plugins/kora/
```

Editing the tracked copy alone does **not** change the running agent; deploy by
copying into the volume and restarting Hermes.

## Deploy

```sh
cd services/hermes
TS=$(date +%Y%m%d%H%M%S)
docker exec hermes sh -c "cd /opt/data/plugins/kora && \
  for f in __init__.py kora_classify.py kora_explain.py plugin.yaml; do \
    [ -f \"\$f\" ] && cp \"\$f\" \"\$f.bak-$TS\"; \
  done"
for f in __init__.py kora_classify.py kora_explain.py plugin.yaml; do
  docker cp "plugin/kora/$f" "hermes:/opt/data/plugins/kora/$f"
done
docker exec hermes sh -c 'chown hermes:hermes \
  /opt/data/plugins/kora/__init__.py \
  /opt/data/plugins/kora/kora_classify.py \
  /opt/data/plugins/kora/kora_explain.py \
  /opt/data/plugins/kora/plugin.yaml; rm -rf /opt/data/plugins/kora/__pycache__'
# Bind-mounted plugin files do not change the Compose config hash, so a plain
# `up -d` is a no-op. Force-recreate only the hermes service to reload the plugin.
docker compose -f compose.yaml up -d --force-recreate --no-deps hermes
docker logs hermes 2>&1 | grep -i 'KORA agent registered'
```

All Python modules in `plugin/kora/` must be deployed together; copying only
`__init__.py` leaves an older `kora_classify.py` in place.

Before deploying, run the plugin regression tests:

```sh
python3 -m pytest services/hermes/plugin/kora/tests -q
```

## Phase history

* Phase 1 — live-state reasoning semantics (`LIVE_STATE_DIRECTIVE`).
* Phase 2 — read-only live qBittorrent tools (`kora.qbit_*`, `QBIT_DIRECTIVE`).
* Phase 3 — controlled Docker administration (`kora.docker_*`,
  `DOCKER_ADMIN_DIRECTIVE`, `services/docker-admin/`).

See `Documentation/Phase3/KORA_Controlled_Administration.md`.
