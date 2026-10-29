# kavita

Phase 10.75 repository import of the live deployment, plus the Phase 2 Uchiyomi
media integration (ADR-0018).

## Purpose
Comics/manga/ebook library and serving layer for mobile/offline reading.

## Runtime
- Container(s): `kavita`
- Image: `jvmilazz0/kavita@sha256:1f2acae7466d022f037ea09f7989eb7c487f916b881174c7a6de33dbfa8acb39` (Kavita v0.8.9.1, pinned by digest)
- Compose: `services/kavita/compose.yaml`
- Former source of truth: CasaOS `kavita (stale; live uses /hive/library/Kavita)`

## Storage
| Host path | Container path | Mode | Purpose |
| --- | --- | --- | --- |
| `/ssd/appdata/kavita/config` | `/kavita/config` | rw | Kavita DB, covers, cache |
| `/hive/library/Kavita/Books` | `/books` | rw | existing Books library |
| `/hive/library/Kavita/Comics` | `/comics` | rw | existing Comics library (shared with Kapowarr) |
| `/hive/library/Kavita/Manga` | `/manga` | rw | existing Manga library |
| `/hive/library/Kavita/fanfic` | `/fanfic` | rw | existing Novelas library |
| `/hive/comics/uchiyomi` | `/uchiyomi` | **ro** | Uchiyomi-acquired media (ADR-0018) |

## Uchiyomi integration (ADR-0018)
Uchiyomi is the **only writer** of `/hive/comics/uchiyomi` (uid/gid `1000`).
Kavita mounts it **read-only** at `/uchiyomi` and indexes it as the dedicated
**`Uchiyomi`** library (type Manga, root `/uchiyomi`, Archive + Images).

- Kavita never writes to the shared tree and never mounts Uchiyomi's database,
  config, cache or backups (those are on `/mnt/monarch/appdata/uchiyomi`).
- New Uchiyomi downloads become visible after a Kavita library scan (Kavita
  folder watching is disabled server-side).
- Mobile offline reading uses Kavita's OPDS catalog / PSE page streaming:
  `/api/opds/<apiKey>` exposes per-chapter CBZ acquisition links that iOS
  OPDS readers can cache locally.

## Operations
```bash
cd services/kavita
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
docker compose up -d      # recreate only kavita
```

## Documentation
See `Documentation/services/kavita/` and
`Architecture/decisions/ADR-0018-Uchiyomi-Kavita-Shared-Library.md`.
