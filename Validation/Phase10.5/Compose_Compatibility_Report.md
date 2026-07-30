# Phase 10.5 — Compose Compatibility Report (hardened)

Offline + live dry-run informed. **No compose files modified in Phase 10.5.**

## Summary

| Bucket | Services |
|--------|----------|
| Already appdata | beszel, hermes, honcho, n8n, open-webui, traefik (acme) |
| Repo PATH_* but live still on `/hive/config|/hive/data` | **homepage** (must migrate live paths) |
| hive-config candidates | code-server, portainer, calibre, calibre-web, jellyfin, nzbget*, hotio, ollama† |
| hive-data-keep | jellyfin media, `/hive/downloads`, library/books, NZBget nested `config/downloads` |
| Deferred / OOS | echoos, cosmoos, odysseus, beszel-agent, Kavita/Nextcloud untracked |

\*nzbget config bind includes nested downloads — excluded from SSD migration.  
†ollama models intentionally included.

## Portainer investigation (dry-run finding)

| Question | Answer |
|----------|--------|
| Is `/hive/portainer` the correct source? | **Yes** — live container mounts `/hive/portainer` → `/data` |
| Why did early dry-run abort? | `find` hit root-owned `compose/49` and `compose/50` (Permission denied); `set -o pipefail` aborted silently |
| Is the tree huge? | **No** (~815K). Historical stack YAMLs under `compose/<id>/` are small |
| Framework fix | Safe tree stats + warn on unreadable paths; optional exclude `compose/49,compose/50` |

## Homepage investigation

| Repo compose | Live container |
|--------------|----------------|
| `${PATH_CONFIG}/homepage` | `/hive/config/homepage` |
| `${PATH_DATA}/homepage/images` | `/hive/data/homepage/images` |

Treat as **migration required** from live hive paths, then align compose/env to appdata.

## NZBget investigation

| Path | Size (approx) | Action |
|------|---------------|--------|
| `/hive/NZBget/config` total | ~120G | Do not copy whole tree blindly |
| `config/downloads` | ~110G | **keep on hive** (rsync exclude) |
| `nzbget.log` | ~11G+ | exclude from SSD copy |
| `nzbget.conf` + queue/scripts | small | migrate |

## Compose validation classes

Framework now labels failures as:

- `missing_env_file`
- `missing_secrets_or_vars`
- `missing_network`
- `missing_external_file`
- `compose_syntax`
- `compose_unknown`

Dry-run: warn and continue. `--execute --apply-compose`: hard fail.

## Flags

| Flag | Status |
|------|--------|
| Premature appdata config refs on required=yes | none observed |
| Shared docker.sock | EXPECTED (not counted as bad duplicate) |
| Shared library mounts (calibre books) | intentional |
| Whole-pool mounts | code-server / odysseus tooling — do not migrate |

## Compatibility rule

No new `/mnt/monarch/appdata/<service>` config bind until copy verified and `--apply-compose` used.
