# Beszel (+ agent) — Phase 12.1 Validation

## Before

- Hub compose SoT: `/mnt/monarch/appdata/beszel/compose.yml` (`henrygd/beszel:latest`)
- Agent compose SoT: `/mnt/monarch/appdata/beszel_agent/compose.yml` with **plaintext KEY/TOKEN in compose**
- Storage already under `/mnt/monarch/appdata/beszel{,_agent}/…`
- Agent relative volume `./beszel_agent_data`

See `inspect/before-beszel.json`, `inspect/before-beszel-agent.json`.

## Steps

1. Standardize hub + agent under `services/beszel` and `services/beszel_agent`.
2. Pin both images to `0.18.7`.
3. Move agent secrets to gitignored `.env`; absolute appdata bind for agent data.
4. Agent docker.sock remains `:ro`; hub uses external `homelab` network.
5. `docker compose up -d` for both.

## After

- Hub: `henrygd/beszel:0.18.7` from `services/beszel`; HTTP 200 on `:8090`
- Agent: `henrygd/beszel-agent:0.18.7` from `services/beszel_agent`; data on absolute appdata path
- No secrets in tracked compose

See `inspect/after-beszel.json`, `inspect/after-beszel-agent.json`.

## Volume migration

None (paths already appdata). Agent bind changed from relative compose-dir path to `/mnt/monarch/appdata/beszel_agent/beszel_agent_data` (same directory).

## Rollback

```bash
cd /mnt/monarch/appdata/beszel && docker compose up -d
cd /mnt/monarch/appdata/beszel_agent && docker compose up -d
```

## Exceptions

`homelab` network; agent `network_mode: host`; sockets — Known_Exceptions.md.

## Security note

Agent KEY/TOKEN previously lived in plaintext on-disk compose under appdata. Moved to `.env`. Consider rotating the agent token in the Beszel UI when convenient.
