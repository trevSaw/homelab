# Honcho — Phase 14.1 note

Honcho remains deployed as a **prototype / ADR-0005 Memory candidate**.

Phase 14.1 does **not** integrate Honcho into the Solo chat path.

| Decision | Detail |
| --- | --- |
| Action | **Remain unchanged** for Phase 14.1 |
| Compose SoT | Still `/mnt/monarch/appdata/honcho` (+ repo `services/honcho` mirror) |
| Integration | Deferred to Phase 14.2 Memory Runtime |
| Risk if touched now | Premature Memory writes / boundary violations |

See `Validation/Phase14.1/Migration_Notes.md`.
