# Chaptarr (Phase 20)

eBook + audiobook manager (Readarr successor; Readarr retired upstream June 2025).

- Config: `/mnt/monarch/appdata/chaptarr`
- eBooks: `/hive/library/Kavita/Books` → `/ebooks` (served by Kavita)
- Audiobooks: `/hive/library/Audiobooks` → `/audiobooks` (served by Audiobookshelf)
- Downloads: `/hive/downloads/completed` → `/downloads` (matches qBittorrent's mount so reported paths resolve)
- Networks: `proxy` + `hotio` (`hotio_default`)
- WebUI: host `:8789` (transitional) and Traefik `chaptarr.fatherfankscloud.uk`

Download clients use Docker DNS `qbittorrent` (NZBGet shares qBittorrent netns → `qbittorrent:6789`). Prowlarr syncs indexers as a Readarr-compatible app.

```bash
cd services/chaptarr
cp -n .env.example .env   # optional; values are inlined
docker compose -f compose.yaml up -d
```

## Lifecycle
State: **Draft/Review** — add root folders, quality profiles (ebook EPUB; audiobook M4B/MP3), download clients, and Prowlarr app before promotion to Production.