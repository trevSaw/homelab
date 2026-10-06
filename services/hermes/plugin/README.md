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
docker exec hermes sh -c "cp /opt/data/plugins/kora/__init__.py \
  /opt/data/plugins/kora/__init__.py.bak-$TS"
docker cp plugin/kora/__init__.py hermes:/opt/data/plugins/kora/__init__.py
docker cp plugin/kora/plugin.yaml  hermes:/opt/data/plugins/kora/plugin.yaml
docker exec hermes sh -c 'chown hermes:hermes /opt/data/plugins/kora/__init__.py \
  /opt/data/plugins/kora/plugin.yaml; rm -rf /opt/data/plugins/kora/__pycache__'
docker compose -f compose.yaml up -d          # recreate Hermes to load the plugin
docker logs hermes 2>&1 | grep -i 'KORA agent registered'
```

## Phase history

* Phase 1 — live-state reasoning semantics (`LIVE_STATE_DIRECTIVE`).
* Phase 2 — read-only live qBittorrent tools (`kora.qbit_*`, `QBIT_DIRECTIVE`).
* Phase 3 — controlled Docker administration (`kora.docker_*`,
  `DOCKER_ADMIN_DIRECTIVE`, `services/docker-admin/`).

See `Documentation/Phase3/KORA_Controlled_Administration.md`.
