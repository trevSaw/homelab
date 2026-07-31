# NZBGet — Verification Report

**Status:** PASS (exclude-aware)

| Metric | Source (migratable) | Destination |
|---|---|---|
| Regular files | 10 | 10 |
| Bytes | 1,259,140 | 1,259,140 |
| Checksums | match | match |
| `nzbget.log` | excluded | absent |
| `downloads/**` files | excluded (~110 GB on source) | 0 files |

Framework full-tree checksum was aborted (would scan excluded 140 GB). Manual `find`+`cksum` with the same exclude set as `services.conf` is the authoritative verification for this service.
