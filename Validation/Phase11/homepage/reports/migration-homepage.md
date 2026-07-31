# Migration report

Generated: 2026-07-30T09:28:04Z

```json
{
  "timestamp": "2026-07-30T09:28:04Z",
  "service": "homepage",
  "phase": "orchestrator",
  "status": "SUCCESS",
  "dry_run": false,
  "execute": true,
  "source": "/hive/config/homepage",
  "destination": "/mnt/monarch/appdata/homepage",
  "files": 3,
  "directories": 2,
  "bytes": "42KB",
  "bytes_raw": 42005,
  "copy_required": "yes",
  "compose_update_needed": "yes",
  "compose_updated": false,
  "verification_status": "orchestrator_complete",
  "rollback_available": true,
  "rsync_excludes": "",
  "warnings": ["[preflight] git working tree not clean — EXPECTED while Phase 10.5 framework changes are uncommitted","[compose] Source path string not found verbatim in compose — proposed file is a copy for manual edit (live drift possible)","[compose] compose PROPOSED: missing .env file — create from .env.example before --execute/--apply-compose","[migration] [preflight] git working tree not clean — EXPECTED while Phase 10.5 framework changes are uncommitted","[migration] [compose] Source path string not found verbatim in compose — proposed file is a copy for manual edit (live drift possible)","[migration] [compose] compose CURRENT: missing .env file — create from .env.example before --execute/--apply-compose","[migration] [compose] compose PROPOSED: missing .env file — create from .env.example before --execute/--apply-compose"],
  "errors": [],
  "warning_count": 7,
  "error_count": 0
}
```
