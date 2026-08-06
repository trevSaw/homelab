# Phase 14.2A Test Results

**Date:** 2026-08-03

**Runtime:** `python:3.12-slim-bookworm` KORA image

**Result:** Pass — 16 tests

## Command

```bash
docker build -t kora-phase142a-validation AI/KORA/Runtime
docker run --rm \
  -v "$PWD/AI/KORA/Runtime:/workspace" \
  -w /workspace \
  --entrypoint python \
  kora-phase142a-validation \
  -m unittest discover -s tests -v
```

## Coverage

| Area | Checks |
| --- | --- |
| Event Bus | JSON round trip, publish/subscribe, namespace/filter routing, unsubscribe, failure isolation |
| Proposal creation | General-event routing, explicit candidate requirement, eligibility, capacity |
| Lifecycle | Pending creation, approve, expire, invalid transition |
| Duplicates | Event idempotency and semantic duplicate withdrawal |
| HTTP API | List/get, invalid status, not found, mutation unavailable |

Additional checks:

- Python AST parse: pass
- `docker compose -f services/kora/compose.yaml config --quiet`: pass
- KORA image build: pass
