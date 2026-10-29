# Audiobookshelf (Phase 20)

Audiobook + podcast streaming server (Chaptarr playback frontend).

- Config: `/mnt/monarch/appdata/audiobookshelf/config`
- Metadata (covers, probes): `/mnt/monarch/appdata/audiobookshelf/metadata`
- Audiobooks: `/hive/library/Audiobooks` → `/audiobooks`
- Networks: `proxy`
- WebUI: host `:13378` (transitional) and Traefik `audiobooks.fatherfankscloud.uk`

Pairs with Chaptarr (writes to the same `/hive/library/Audiobooks` root). Kavita continues to serve eBooks from `/hive/library/Kavita/Books`.

```bash
cd services/audiobookshelf
cp -n .env.example .env   # optional; values are inlined
docker compose -f compose.yaml up -d
```

## Lifecycle
State: **Draft/Review** — create admin account and add the `/audiobooks` library before promotion to Production.