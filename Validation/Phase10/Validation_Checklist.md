# Phase 10 Validation Checklist

## Pre-merge / local (Windows or Linux checkout)

- [x] Compose files under `Services/` reviewed for logging / restart / secrets
- [x] `.env.example` present for secret-bearing services
- [x] `.gitignore` ignores `**/.env`
- [x] `Scripts/validate.sh` added
- [x] Energy audit README + sample report match v1.4
- [x] StandardsRoadmap Phase 10 marked scoped-complete with deferrals
- [x] Phase 10 QA pack written under `Validation/Phase10/`

## Run locally

```bash
./Scripts/validate.sh
```

**Last local run (2026-07-29):** `PASS=45  WARN=3  FAIL=0`  
Warnings are expected off-host when production `.env` / secrets are absent (honcho, jellyfin, n8n).

Expected on a clean mocha checkout after `.env` creation: PASS with zero or fewer WARNs.

## mocha host (operator)

- [ ] Copy `.env.example` → `.env` for: ollama, beszel_agent, hermes, code-server, n8n, honcho
- [ ] Ensure `Services/.env` contains `AUTHENTIK_SECRET_KEY` and existing PG/path vars
- [ ] `./Scripts/validate.sh`
- [ ] Per stack: `docker compose -f <file> config`
- [ ] Recreate stacks one at a time during maintenance window
- [ ] Verify Traefik routing / SSO / chat / code / hermes still reachable
- [ ] `docker ps` — confirm no unexpected restart loops; note any `unhealthy`
- [ ] `./Scripts/audit/energy_audit.sh` — confirm Capacity shows single `%`, Mem Limit shows `Unlimited`
- [ ] Rotate previously committed secrets
- [ ] Commit Phase 10 branch only after `.env` files verified **not** staged

## Explicit non-goals (do not check as done)

- [ ] Storage migration
- [ ] Network redesign / host-port removal
- [ ] Image pinning campaign
- [ ] Privileged container elimination
- [ ] F10-1 … F10-6 governance metadata enrichment
