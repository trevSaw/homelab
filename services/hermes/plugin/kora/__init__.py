"""KORA — the specialized head agent hosted by Hermes (staging prototype).

KORA IS THE AGENT. Hermes is the generic runtime. KORA does NOT implement
infrastructure; it orchestrates EXTERNAL service containers over HTTP:

    KORA → Ollama   (inference + embeddings)   http://ollama:11434
    KORA → Chroma   (knowledge store)          http://chromadb:8000 (staging)
    KORA → Honcho   (memory)                   documented boundary (approval-gated)
    KORA → Graphify (relationships)            documented boundary
    KORA → MCP/tools                            via Hermes tool runtime

KORA's own responsibilities (implemented here in real code):
  - classification / strategy selection
  - governance / refusal decision
  - deciding which service is needed, then calling it
  - response composition (identity + refusal + digest)
  - structured explainability record (out-of-band)

Uses ONLY supported Hermes v0.17.0 extension points (PluginContext hooks +
tools). No Hermes source is modified. No KORA Python service code is imported
in-process — services are reached over HTTP as real containers.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from pathlib import Path
from urllib.parse import quote

import httpx

log = logging.getLogger("kora.agent")

OLLAMA = os.environ.get("KORA_STAGING_OLLAMA", "http://ollama:11434")
CHROMA = os.environ.get("KORA_STAGING_CHROMA", "http://chromadb:8000")
EMBED_MODEL = os.environ.get("KORA_STAGING_EMBED_MODEL", "nomic-embed-text")
EXPLAIN_DIR = Path(os.environ.get("HERMES_HOME", "/opt/data")) / "kora-explain"
EXPLAIN_PATH = EXPLAIN_DIR / "records.jsonl"

# Phase 2 — narrow read-only live qBittorrent inspection. Credentials come from
# the Hermes environment (services/hermes/.env, gitignored); never log or print
# them. Base URL defaults to the host published WebUI port via the container's
# default gateway (no network change required).
QBIT_BASE = os.environ.get("KORA_QBIT_BASE_URL", "").strip()
QBIT_USER = os.environ.get("KORA_QBIT_USER", "")
QBIT_PASS = os.environ.get("KORA_QBIT_PASS", "")
QBIT_PORT = "8080"
QBIT_READ_FILTERS = {
    "all", "downloading", "seeding", "completed", "paused", "active",
    "inactive", "stalled", "stalled_uploading", "stalled_downloading", "errored",
}

# Phase 3 — controlled homelab administration via the narrow `docker-admin`
# helper. Hermes/KORA do NOT receive /var/run/docker.sock; every Docker
# operation goes through the whitelisted, token-authenticated docker-admin HTTP
# API on the internal `kora-admin` network. The token is read from the Hermes
# environment or the gitignored /opt/data/docker-admin.token file (never logged,
# never returned in tool output).
DOCKER_ADMIN_URL = os.environ.get("KORA_DOCKER_ADMIN_URL", "http://docker-admin:8765").rstrip("/")
DOCKER_ADMIN_TOKEN_FILE = Path(os.environ.get("HERMES_HOME", "/opt/data")) / "docker-admin.token"
DOCKER_ADMIN_READ_TOOLS = {
    "kora.docker_list", "kora.docker_inspect", "kora.docker_logs",
    "kora.docker_health", "kora.docker_image", "kora.docker_networks",
    "kora.docker_volumes",
}
DOCKER_ADMIN_WRITE_TOOLS = {
    "kora.docker_restart", "kora.docker_compose_validate", "kora.docker_compose_up",
}
DOCKER_ADMIN_TOOLS = DOCKER_ADMIN_READ_TOOLS | DOCKER_ADMIN_WRITE_TOOLS


def _docker_admin_token() -> str:
    tok = os.environ.get("KORA_DOCKER_ADMIN_TOKEN", "").strip()
    if tok:
        return tok
    try:
        return DOCKER_ADMIN_TOKEN_FILE.read_text(encoding="utf-8").strip()
    except Exception:  # noqa: BLE001
        return ""

# Phase 15 Council — KORA is the head agent; members are canonical content in
# Architecture/ai/Council/Members/, mounted read-only at $HERMES_HOME/council.
# KORA invokes members using Hermes' NATIVE delegate_task (subagent) tool.
COUNCIL_MEMBERS = ["NOVA", "IRIS", "TALIA", "SOLA", "LUMA", "ALUMA", "NOMA"]
COUNCIL_DIR = Path(os.environ.get("HERMES_HOME", "/opt/data")) / "council" / "Members"

COUNCIL_DIRECTIVE = (
    "COUNCIL: You are head of the KORA Council. Members: " + ", ".join(COUNCIL_MEMBERS) +
    ". To let ONE member speak: kora.council_member('<NAME>') to load its canonical identity, then delegate_task(goal='You are <NAME>, <role>. Answer as <NAME>: <request>', context=<member content>), then synthesize. Invoke only the member(s) the request warrants; a request to one member never summons the whole Council. You keep final response authority and KORA identity."
)

# Phase 17 — canonical personal-knowledge retrieval behavior. Establishes the
# source hierarchy for questions about Trev's identity, preferences, projects,
# goals, and architectural decisions. Does NOT duplicate the profile content.
PROFILE_RETRIEVAL_DIRECTIVE = (
    "KNOWLEDGE PRIORITY (user identity, preferences, projects, goals, architecture): retrieve the "
    "CANONICAL profile FIRST from the read-only corpus /opt/data/homelab-docs (source "
    "Documentation/Phase17/Personal_Knowledge_Archive.md) via file tools "
    "(read_file/search_files). If mcp_jdocmunch_* are exposed, search repo 'local/homelab-docs' "
    "then get the top section. Never claim jdocmunch/Context7/Graphify are available if they are "
    "not in your toolset. Hierarchy: (1) current canonical "
    "knowledge/decisions > (2) other authoritative project knowledge > (3) Honcho conversational "
    "memory (supplementary) > (4) model inference. Current beats historical; if a real conflict "
    "remains, say so; never treat derived memory as the authoritative profile."
)

# Phase 17.x — governance standards retrieval. KORA must consult the canonical
# homelab governance standards when preparing/modifying service deployments.
# Phase 6: the canonical homelab repo IS mounted read/write at
# /home/fatherfrank/projects/homelab; the old /opt/data/homelab-workspace clone
# is deprecated and /opt/data/homelab-repo remains an empty placeholder.
GOVERNANCE_RETRIEVAL_DIRECTIVE = (
    "GOVERNANCE FIRST: before preparing, modifying, or proposing any service deployment or infra "
    "change, retrieve the canonical standard from the read-only /opt/data/homelab-governance "
    "(search_files/read_file); if mcp_jdocmunch_* are exposed you may search repo "
    "'local/homelab-governance' and get the top section. Standards are the source of truth \u2014 "
    "follow them. The canonical repo is mounted read-only EXCEPT the writable documentation "
    "dirs Documentation/, Architecture/decisions/, Validation/ and Services/ (under "
    "/home/fatherfrank/projects/homelab); /opt/data/homelab-workspace is DEPRECATED (never "
    "authoritative). Do not modify live secrets/production without approval."
)


# Phase 22 — Hermes delegation for heavy coding/engineering work.
# KORA remains the orchestrator; heavy tasks are delegated via Hermes
# delegate_task to a child agent backed by OpenCode Go (DeepSeek Flash).
# Boundary enforcement lives in the bridge (permission profiles + approval
# gating), NOT in this prompt.
DELEGATION_DIRECTIVE = (
    "ENGINEERING DELEGATION (MUST for heavy work): for investigating, debugging, implementing, "
    "configuring, or validating real homelab infra/code, delegate the heavy work via "
    "delegate_task(goal=..., context=...). The child runs on the OpenCode Go model with the same "
    "Hermes tools (terminal, process, files, git, exposed MCPs) in /opt/data/homelab-workspace "
    "and the writable documentation dirs under /home/fatherfrank/projects/homelab. Use the default local model "
    "for conversation, "
    "explanations, writing, and simple facts \u2014 do not delegate those. Never reference or request "
    "provider credentials or model identifiers. Canonical-repo DOCUMENTATION changes may be "
    "committed locally; production deployment stays behind the approval boundary (never deploy "
    "without approval). Report exactly what the child returned; do not invent a result."
)

# Phase 1 — live-state reasoning semantics + evidence sources (remediation of
# the qBittorrent-style failure). Rules:
#   * Failure to inspect is NOT evidence of absence.
#   * Container/service questions consult live docker tools, then the snapshot.
#   * No docker.sock and no credentials. (Phase 6 additionally bind-mounts the
#     canonical repo read/write for documentation; see services/hermes.)
LIVE_STATE_DIRECTIVE = (
    "LIVE-STATE REASONING (MANDATORY): A. FAILURE TO INSPECT IS NOT EVIDENCE OF ABSENCE: docker "
    "CLI/ps failure, a missing socket/tool, search errors, inaccessible paths, HTTP 401/403, and "
    "timeouts are evidence about YOUR inspection, NOT the system \u2014 never convert 'could not "
    "inspect X' into 'X does not exist'. B. CLASSIFY EVIDENCE as exactly: (1) confirmed present, "
    "(2) confirmed absent, (3) unable to inspect, (4) stale/indirect, (5) conflicting; preserve "
    "the uncertainty for (3)-(5). C. CONTAINERS/SERVICES: use live kora.docker_* first; if "
    "unavailable fall back to the read-only snapshot /opt/data/docker-state; state only what "
    "the evidence establishes; if live state is required but unavailable, say so. D. REPO "
    "REALITY: only the documentation dirs (Documentation, Architecture/decisions, Validation, "
    "Services) under /home/fatherfrank/projects/homelab are mounted (rw); the rest of the "
    "canonical repo is NOT mounted and NO server-side Obsidian vault exists; /opt/data/"
    "homelab-workspace is DEPRECATED. E. APPLICATION STATE (e.g. torrents): use "
    "kora.qbit_* live; if unavailable "
    "report 'cannot determine' \u2014 never 'zero'/'absent', and never infer app state from container "
    "state."
)

# Phase 2 — live read-only qBittorrent inspection capability. Distinct from
# docker-state (container-level/historical) and from the generic terminal.
QBIT_DIRECTIVE = (
    "QBITTORRENT LIVE-STATE (Phase 2): for CURRENT torrent activity use the read-only tools "
    "kora.qbit_torrents "
    "(filter=all|downloading|seeding|completed|paused|active|inactive|stalled|stalled_uploading|stalled_downloading|errored), "
    "kora.qbit_transfer_info, kora.qbit_app_version, kora.qbit_categories, kora.qbit_tags. (1) "
    "Prefer the live API over the snapshot. (2) NEVER infer "
    "torrent state from container state, and NEVER infer absence from an API failure. (3) On "
    "status 'error' (auth-failed, credentials-not-configured, connection-failed, api-error) "
    "report that live torrent state could not be retrieved. (4) Do not query qBittorrent via "
    "terminal and do not read its credentials; use only these tools. (5) Strictly read-only \u2014 no "
    "pause/resume/delete/add/recheck/reannounce/limits/category/priority operations exist."
)

# Phase 3 — controlled homelab administration. KORA may inspect live Docker
# state and perform a deliberately narrow set of lifecycle operations through
# dedicated tools that call the docker-admin helper. This capability does NOT
# bypass KORA governance (KORA remains policy/orchestration; Hermes executes;
# Docker is the target). Destructive operations are not exposed at all.
DOCKER_ADMIN_DIRECTIVE = (
    "LIVE DOCKER ADMINISTRATION (Phase 3): use the narrow docker-admin tools. READ: "
    "kora.docker_list, kora.docker_inspect, kora.docker_logs, kora.docker_health, "
    "kora.docker_image, kora.docker_networks, kora.docker_volumes. WRITE (narrow, explicit): "
    "kora.docker_restart (one container), "
    "kora.docker_compose_validate, kora.docker_compose_up (recreate/deploy a canonical project; "
    "requires confirm=true). RULES: (1) read-only except restart and compose validate/up \u2014 NO "
    "delete/remove/prune/exec/build/pull or arbitrary docker; never claim or attempt them. (2) "
    "Always target an EXPLICIT service/container; never a wildcard or 'all'. (3) Validate Compose "
    "before deploying; after any write VERIFY the resulting state before reporting success. (4) "
    "Failure is not absence: on status 'error' report uncertainty; never say a container does not "
    "exist because inspect failed. (5) The helper refuses restart/deploy of the control plane "
    "(hermes, docker-admin) \u2014 report that honestly. (6) The canonical repo is the configuration "
    "source of truth; running state is evidence only."
)

# Phase 5 — external web research via the self-hosted SearXNG instance, using
# Hermes' NATIVE `web` toolset (web_search) with `web.search_backend: searxng`
# and SEARXNG_URL. SearXNG is a DISCOVERY mechanism, not an authority; KORA
# remains the governance layer. This directive changes reasoning only: no new
# privileges, no Docker socket, no new runtime, Phase 1-4 boundaries preserved.
RESEARCH_DIRECTIVE = (
    "EXTERNAL RESEARCH & SOURCING: (1) SOURCE CHOICE: local homelab facts -> existing homelab "
    "tools (kora.docker_*, kora.qbit_*, knowledge/memory, file/terminal on mounted corpora), not "
    "web search; external/current facts -> native web_search (self-hosted SearXNG); deep "
    "repository/code work -> delegate_task to the OpenCode Go child, then interpret as KORA. (2) "
    "SEARXNG IS DISCOVERY, NOT AUTHORITY: snippets are discovery only; never treat a "
    "snippet/summary/ranking as proof; open the PRIMARY source before relying on a fact. (3) "
    "PREFER OFFICIAL/UPSTREAM sources (repo, releases, official docs) over "
    "blogs/mirrors/aggregators; cite the source you actually relied on. (4) NO SNIPPET-ONLY "
    "CLAIMS: if you could not reach the primary source, say so and label the claim UNVERIFIED; "
    "never invent a version/command/path/URL or present a snippet as if you read the page. (5) "
    "BOUNDARIES: web_search is read-only discovery; no Docker socket, no new runtime, no Task "
    "Bridge. (6) web_extract is unavailable (SearXNG search-only): read a URL via terminal curl "
    "or delegate repository analysis."
)

# Phase 5.1 — mandatory research evidence & provenance protocol. Addresses the
# Kapowarr failure: accurate evidence (repo + delegated child) existed, but the
# final synthesis promoted model inference (invented image tag, fabricated
# homelab paths/hostname/health endpoint) into factual deployment claims.
# This is an ENFORCEABLE output contract, not advisory prose. It applies to
# research / implementation / deployment planning, service-install research,
# architecture investigation and configuration recommendations — NOT to ordinary
# conversational answers (do not force the four-section format onto small talk).
#
# DELIVERY NOTE (Phase 5.1): Hermes' hook-output spill
# (tools/hook_output_spill.py, hooks.output_spill.max_chars default 10000)
# replaces oversized pre_llm_call context with a 500-char head + 500-char tail.
# The combined directives exceed that cap, so the MIDDLE never reaches the model.
# RESEARCH_EVIDENCE_CONTRACT is therefore bookended (first AND last) in
# pre_llm_call, and kept under ~1000 chars so head[0:500] + tail[-500:] always
# cover it. RESEARCH_EVIDENCE_PROTOCOL (the long form) is kept for configs where
# the full context fits.
RESEARCH_EVIDENCE_CONTRACT = (
    "[KORA EVIDENCE CONTRACT - applies ONLY to "
    "research/implementation/deployment/architecture/service-install plans; NEVER force these "
    "four sections on ordinary conversation] Output four sections in order: UPSTREAM FACTS, "
    "HOMELAB FACTS, PROPOSED DESIGN DECISIONS, UNRESOLVED QUESTIONS. Put a value in a FACTS "
    "section ONLY if you read it from the primary upstream source or observed it live "
    "(tools/repo) IN THIS TASK; otherwise it MUST go under UNRESOLVED QUESTIONS. Classify each "
    "material claim as CONFIRMED_UPSTREAM, HOMELAB_FACT, PROPOSED_DECISION, MODEL_INFERENCE, "
    "CONFLICTING, or UNRESOLVED (only the first two may appear in FACTS sections); label each "
    "HOMELAB_FACT source: CANONICAL_REPO_FACT, OBSIDIAN_VAULT_FACT, DOCUMENTATION_FACT, "
    "LIVE_DOCKER_FACT - never present one as another. Never state as "
    "fact any version, image tag/digest, path, hostname, DNS record, port, volume, env var, "
    "health endpoint, network, or integration you did not verify. Model knowledge/memory is NEVER "
    "a fact. If sources conflict, STOP and mark CONFLICTING/UNRESOLVED; never invent a value to "
    "reconcile. Never cite a source you did not open this task. Production plans must not contain "
    "example.com/org/net, /path/to/..., <hostname>, or TBD. Empty/failed search = UNABLE TO "
    "VERIFY, not absence and not permission to use memory. Preserve a delegated child's verified "
    "values; never silently substitute your own."
)
RESEARCH_EVIDENCE_PROTOCOL = (
    "RESEARCH EVIDENCE PROTOCOL: the [KORA EVIDENCE CONTRACT] at the top and bottom of this "
    "context is authoritative for any research/plan deliverable."
)


from . import kora_classify as kc  # noqa: E402
from . import kora_explain as xp  # noqa: E402

FORBIDDEN = kc.FORBIDDEN_LABELS


def _embed(texts: list[str]) -> list[list[float]]:
    with httpx.Client(timeout=60.0) as c:
        r = c.post(f"{OLLAMA}/api/embed", json={"model": EMBED_MODEL, "input": texts})
        r.raise_for_status()
        return [[float(v) for v in vec] for vec in r.json()["embeddings"]]


def _chroma_ensure_collection(client: httpx.Client) -> str:
    base = f"{CHROMA}/api/v2/tenants/default_tenant/databases/default_database/collections"
    r = client.post(base, json={"name": "kora_knowledge", "get_or_create": True})
    r.raise_for_status()
    cid = r.json().get("id")
    if not cid:
        raise RuntimeError("chroma returned no collection id")
    return cid


# ---------------------------------------------------------------------------
# KORA orchestrates external services (via registered tools)
# ---------------------------------------------------------------------------

def _index_fixture() -> None:
    """KORA ingests one knowledge document into the REAL Chroma service
    (embed via Ollama, upsert into Chroma). Smallest real knowledge write."""
    fixture = "/fixtures/knowledge-fixture.md"
    try:
        text = Path(fixture).read_text(encoding="utf-8")
    except Exception:
        return
    try:
        vecs = _embed([text])
        with httpx.Client(timeout=30.0) as c:
            cid = _chroma_ensure_collection(c)
            c.post(
                f"{CHROMA}/api/v2/tenants/default_tenant/databases/default_database/collections/{cid}/upsert",
                json={
                    "ids": ["fixture:knowledge"],
                    "embeddings": vecs,
                    "documents": [text],
                    "metadatas": [{"source": fixture, "document_id": "fixture-knowledge", "version": "1"}],
                },
            )
        xp.write_state({"knowledge_ready": True})
    except Exception as exc:  # noqa: BLE001
        log.warning("kora knowledge index failed: %s", exc)
        xp.write_state({"knowledge_ready": False, "knowledge_error": str(exc)})


def handler_knowledge_query(args, **kw):
    """KORA decides knowledge is needed → calls REAL Chroma (embed via Ollama)."""
    query = str((args or {}).get("query", ""))
    try:
        vec = _embed([query])[0]
        with httpx.Client(timeout=30.0) as c:
            cid = _chroma_ensure_collection(c)
            r = c.post(
                f"{CHROMA}/api/v2/tenants/default_tenant/databases/default_database/collections/{cid}/query",
                json={"query_embeddings": [vec], "n_results": 3,
                      "include": ["documents", "metadatas", "distances"]},
            )
            r.raise_for_status()
            data = r.json() or {}
        docs = (data.get("documents") or [[]])[0]
        metas = (data.get("metadatas") or [[]])[0]
        ids = (data.get("ids") or [[]])[0]
        out = []
        for i, _id in enumerate(ids):
            out.append({"id": _id, "source": (metas[i] or {}).get("source") if i < len(metas) else None,
                        "text": docs[i] if i < len(docs) else ""})
        return json.dumps({"service": "chroma", "results": out}, sort_keys=True)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"service": "chroma", "status": "error", "error": str(exc)}, sort_keys=True)


def handler_ollama_models(args, **kw):
    """KORA → Ollama (read-only): list models from the real Ollama service."""
    try:
        with httpx.Client(timeout=20.0) as c:
            r = c.get(f"{OLLAMA}/api/tags")
            r.raise_for_status()
            return json.dumps({"service": "ollama", "models": [m.get("name") for m in r.json().get("models", [])]}, sort_keys=True)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"service": "ollama", "status": "error", "error": str(exc)}, sort_keys=True)


def handler_memory_status(args, **kw):
    """KORA → Honcho boundary (documented). Honcho is reached in Phase 14 via
    KORA's approval-gated Memory Runtime contract; not recreated here."""
    return json.dumps({"service": "honcho", "boundary": "approval-gated Memory Runtime (Phase 14.2)",
                       "status": "boundary_documented"}, sort_keys=True)


def handler_memory_propose(args, **kw):
    """KORA → Honcho boundary (documented, non-write). Real Honcho writes require
    the approval-gated Memory Runtime service; this is a labeled boundary stub."""
    content = str((args or {}).get("content", ""))
    return json.dumps({"service": "honcho", "status": "boundary_stub",
                       "note": "real Honcho write requires KORA Memory Runtime approval flow",
                       "content_sha": __import__("hashlib").sha256(content.encode()).hexdigest()[:12]},
                      sort_keys=True)


def handler_wipe_volume(args, **kw):
    # MUST never execute: KORA governance blocks this tool in pre_tool_call.
    return "EXECUTED-WIPE"


# ---------------------------------------------------------------------------
# Phase 15 Council — KORA loads canonical member content; invocation is via
# Hermes' native delegate_task subagent tool (no custom runtime).
# ---------------------------------------------------------------------------

def handler_council_list(args, **kw):
    """KORA lists the canonical Council members (Phase 15)."""
    return json.dumps(
        {"service": "council", "head": "KORA", "members": COUNCIL_MEMBERS},
        sort_keys=True,
    )


def handler_council_member(args, **kw):
    """KORA loads a Council member's canonical identity/personality/role.

    Reads the canonical member file from the read-only Council mount
    ($HERMES_HOME/council/Members/<NAME>.md → Architecture/ai/Council/).
    """
    name = str((args or {}).get("name", "")).strip().upper()
    if name not in COUNCIL_MEMBERS:
        return json.dumps(
            {"service": "council", "status": "error",
             "error": f"Unknown Council member '{name}'. Known: {COUNCIL_MEMBERS}"},
            sort_keys=True,
        )
    member_file = COUNCIL_DIR / f"{name}.md"
    try:
        content = member_file.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return json.dumps(
            {"service": "council", "status": "error",
             "error": f"cannot read {member_file}: {exc}"},
            sort_keys=True,
        )
    return json.dumps(
        {"service": "council", "member": name, "canonical": content},
        sort_keys=True,
    )


# ---------------------------------------------------------------------------
# Phase 2 — qBittorrent read-only live inspection.
# Only GET API endpoints are used; the WebUI login is required because
# qBittorrent has no read-only account/token. Read-only enforcement lives here
# (no mutation handlers or endpoints are exposed).
# ---------------------------------------------------------------------------

def _qbit_default_base_url() -> str:
    """Host published WebUI port via the container's default gateway (0 net change)."""
    try:
        with open("/proc/net/route", "r", encoding="utf-8") as f:
            next(f, None)
            for line in f:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "00000000":
                    gw = int(parts[2], 16)
                    return "http://%d.%d.%d.%d:%s" % (
                        gw & 0xFF, (gw >> 8) & 0xFF, (gw >> 16) & 0xFF, (gw >> 24) & 0xFF, QBIT_PORT)
    except Exception:
        pass
    return "http://172.17.0.1:%s" % QBIT_PORT


def _qbit_client_and_base():
    base = QBIT_BASE or _qbit_default_base_url()
    client = httpx.Client(timeout=20.0, follow_redirects=True)
    return client, base.rstrip("/")


def _qbit_auth(client, base) -> str | None:
    """Login; return None on success or a short error code (no secrets returned)."""
    if not QBIT_USER or not QBIT_PASS:
        return "credentials-not-configured"
    try:
        r = client.post(
            base + "/api/v2/auth/login",
            data={"username": QBIT_USER, "password": QBIT_PASS},
            headers={"Referer": base + "/"},
        )
    except Exception:  # noqa: BLE001
        return "connection-failed"
    if r.status_code != 200 or "Ok." not in r.text:
        return "auth-failed"
    return None


def _qbit_get(endpoint, params=None) -> dict:
    client, base = _qbit_client_and_base()
    try:
        auth_error = _qbit_auth(client, base)
        if auth_error:
            return {"service": "qbittorrent", "status": "error", "error": auth_error}
        r = client.get(
            base + endpoint,
            params=params or {},
            headers={"Referer": base + "/"},
        )
        r.raise_for_status()
        try:
            data = r.json()
        except Exception:  # noqa: BLE001  (e.g. /api/v2/app/version returns plain text)
            data = r.text.strip()
        return {"service": "qbittorrent", "status": "ok", "data": data}
    except Exception as exc:  # noqa: BLE001
        return {"service": "qbittorrent", "status": "error",
                "error": "api-error", "detail": str(exc)[:300]}
    finally:
        client.close()


_QBIT_SUMMARY_FIELDS = (
    "name", "hash", "state", "progress", "size", "downloaded", "uploaded",
    "ratio", "dl_speed", "up_speed", "seeds", "peers", "seeds_total",
    "peers_total", "added_on", "completion_on", "category", "tags",
    "amount_left", "save_path",
)


def _summarize_torrents(items, limit=100):
    out = []
    for t in (items or [])[:limit]:
        row = {k: t[k] for k in _QBIT_SUMMARY_FIELDS if k in t}
        out.append(row)
    return out


def handler_qbit_torrents(args, **kw):
    f = str((args or {}).get("filter", "all") or "all").strip().lower()
    if f not in QBIT_READ_FILTERS:
        return json.dumps({"service": "qbittorrent", "status": "error",
                           "error": "invalid-filter", "allowed": sorted(QBIT_READ_FILTERS)},
                          sort_keys=True)
    try:
        limit = max(1, min(int((args or {}).get("limit", 100) or 100), 500))
    except (TypeError, ValueError):
        limit = 100
    result = _qbit_get("/api/v2/torrents/info", {"filter": f})
    if result["status"] == "ok":
        result["data"] = _summarize_torrents(result.get("data"), limit)
    return json.dumps(result, sort_keys=True)


def handler_qbit_transfer_info(args, **kw):
    return json.dumps(_qbit_get("/api/v2/transfer/info"), sort_keys=True)


def handler_qbit_app_version(args, **kw):
    return json.dumps(_qbit_get("/api/v2/app/version"), sort_keys=True)


def handler_qbit_categories(args, **kw):
    return json.dumps(_qbit_get("/api/v2/torrents/categories"), sort_keys=True)


def handler_qbit_tags(args, **kw):
    return json.dumps(_qbit_get("/api/v2/torrents/tags"), sort_keys=True)


# ---------------------------------------------------------------------------
# Phase 3 — controlled Docker administration via the docker-admin helper.
# KORA never receives the Docker socket; it can only call these whitelisted
# HTTP operations. Read is automatic; writes are explicit and are verified.
# ---------------------------------------------------------------------------

_DOCKER_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def _docker_admin_request(method, path, body=None, timeout=30.0):
    """Call the docker-admin helper. Never logs or returns the token."""
    token = _docker_admin_token()
    if not token:
        return {"service": "docker-admin", "status": "error",
                "error": "token-not-configured"}
    url = DOCKER_ADMIN_URL + path
    headers = {"Authorization": "Bearer " + token}
    try:
        with httpx.Client(timeout=timeout) as c:
            if method == "GET":
                r = c.get(url, headers=headers)
            else:
                r = c.post(url, headers=headers, json=body or {})
    except Exception as exc:  # noqa: BLE001
        return {"service": "docker-admin", "status": "error",
                "error": "admin-unreachable", "detail": str(exc)[:200]}
    try:
        data = r.json()
    except Exception:  # noqa: BLE001
        data = {"status": "error", "error": "admin-bad-response",
                "http_status": r.status_code}
    if not isinstance(data, dict):
        data = {"status": "error", "error": "admin-bad-response",
                "http_status": r.status_code}
    if r.status_code != 200:
        data.setdefault("status", "error")
        data.setdefault("error", "admin-http-%d" % r.status_code)
    else:
        data.setdefault("status", "ok")
    # Never echo the token through any error path.
    return data


def _need_name(args):
    name = str((args or {}).get("name", "")).strip()
    if not _DOCKER_NAME_RE.match(name):
        return None
    return name


def handler_docker_list(args, **kw):
    return json.dumps(_docker_admin_request("GET", "/containers"), sort_keys=True)


def handler_docker_inspect(args, **kw):
    name = _need_name(args)
    if not name:
        return json.dumps({"service": "docker-admin", "status": "error",
                           "error": "invalid-or-missing-name"}, sort_keys=True)
    return json.dumps(_docker_admin_request("GET", "/containers/" + quote(name, safe="")),
                      sort_keys=True)


def handler_docker_logs(args, **kw):
    name = _need_name(args)
    if not name:
        return json.dumps({"service": "docker-admin", "status": "error",
                           "error": "invalid-or-missing-name"}, sort_keys=True)
    try:
        tail = max(1, min(int((args or {}).get("tail", 100) or 100), 1000))
    except (TypeError, ValueError):
        tail = 100
    return json.dumps(_docker_admin_request(
        "GET", "/containers/%s/logs?tail=%d" % (quote(name, safe=""), tail)),
        sort_keys=True)


def handler_docker_health(args, **kw):
    name = _need_name(args)
    if not name:
        return json.dumps({"service": "docker-admin", "status": "error",
                           "error": "invalid-or-missing-name"}, sort_keys=True)
    data = _docker_admin_request("GET", "/containers/" + quote(name, safe=""))
    if data.get("status") == "error":
        return json.dumps(data, sort_keys=True)
    container = data.get("container", {}) or {}
    state = container.get("state", {}) or {}
    return json.dumps({
        "service": "docker-admin", "status": "ok", "name": name,
        "image": container.get("image"),
        "state": state.get("status"),
        "running": state.get("running"),
        "health": state.get("health"),
        "started_at": state.get("started_at"),
    }, sort_keys=True)


def handler_docker_image(args, **kw):
    ref = str((args or {}).get("ref") or (args or {}).get("name") or "").strip()
    if not _DOCKER_NAME_RE.match(ref):
        return json.dumps({"service": "docker-admin", "status": "error",
                           "error": "invalid-or-missing-ref"}, sort_keys=True)
    return json.dumps(_docker_admin_request("GET", "/images/" + quote(ref, safe="")),
                      sort_keys=True)


def handler_docker_networks(args, **kw):
    name = str((args or {}).get("name", "")).strip()
    if name:
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$", name):
            return json.dumps({"service": "docker-admin", "status": "error",
                               "error": "invalid-name"}, sort_keys=True)
        return json.dumps(_docker_admin_request("GET", "/networks/" + quote(name, safe="")),
                          sort_keys=True)
    return json.dumps(_docker_admin_request("GET", "/networks"), sort_keys=True)


def handler_docker_volumes(args, **kw):
    name = str((args or {}).get("name", "")).strip()
    if name:
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$", name):
            return json.dumps({"service": "docker-admin", "status": "error",
                               "error": "invalid-name"}, sort_keys=True)
        return json.dumps(_docker_admin_request("GET", "/volumes/" + quote(name, safe="")),
                          sort_keys=True)
    return json.dumps(_docker_admin_request("GET", "/volumes"), sort_keys=True)


def handler_docker_restart(args, **kw):
    name = _need_name(args)
    if not name:
        return json.dumps({"service": "docker-admin", "status": "error",
                           "error": "invalid-or-missing-name"}, sort_keys=True)
    confirm = bool((args or {}).get("confirm", False))
    return json.dumps(_docker_admin_request(
        "POST", "/containers/%s/restart" % quote(name, safe=""),
        {"confirm": confirm}, timeout=90.0), sort_keys=True)


def handler_docker_compose_validate(args, **kw):
    project = str((args or {}).get("project", "")).strip()
    if not _DOCKER_NAME_RE.match(project):
        return json.dumps({"service": "docker-admin", "status": "error",
                           "error": "invalid-or-missing-project"}, sort_keys=True)
    body = {"project": project}
    service = str((args or {}).get("service", "") or "").strip()
    if service:
        body["service"] = service
    return json.dumps(_docker_admin_request("POST", "/compose/validate", body),
                      sort_keys=True)


def handler_docker_compose_up(args, **kw):
    project = str((args or {}).get("project", "")).strip()
    if not _DOCKER_NAME_RE.match(project):
        return json.dumps({"service": "docker-admin", "status": "error",
                           "error": "invalid-or-missing-project"}, sort_keys=True)
    body = {"project": project, "confirm": bool((args or {}).get("confirm", False))}
    service = str((args or {}).get("service", "") or "").strip()
    if service:
        body["service"] = service
    return json.dumps(_docker_admin_request(
        "POST", "/compose/up", body, timeout=300.0), sort_keys=True)


# ---------------------------------------------------------------------------
# KORA hooks (structural intelligence + governance + composition + records)
# ---------------------------------------------------------------------------

def on_session_start(**kw) -> None:
    xp.set_session(kw.get("session_id", ""), {"started": time.time()})


# Phase 5.1 follow-up — deterministic intent gate. The evidence contract is
# injected (bookended) ONLY for research/plan/deployment-style requests, so
# ordinary conversation is never forced into the four-section format. If the
# intent regex misses a plan request, the always-present RESEARCH_DIRECTIVE and
# the guard remain the backstop.
_PLAN_INTENT_RE = re.compile(
    r"\b(research|plan|planning|implementation|implement|deploy|deployment|"
    r"install|installation|configure|configuration|migration|migrate|"
    r"provision|rollout)\b|\bhomelab\b",
    re.IGNORECASE,
)


def pre_llm_call(**kw) -> str:
    user = str(kw.get("user_message", ""))
    turn_id = str(kw.get("turn_id", "") or uuid.uuid4().hex)
    session_id = str(kw.get("session_id", "") or "unknown")
    model = str(kw.get("model", ""))

    classification = kc.classify(user)
    strategy = kc.select_strategy(classification)
    rec = xp.begin_record(turn_id=turn_id, session_id=session_id, request=user,
                          classification=classification, strategy=strategy, model=model)
    xp.set_current(session_id, rec)

    if classification["label"] in FORBIDDEN:
        rec["governance"] = {"decision": "refused", "label": classification["label"],
                             "reason": classification["rationale"]}
        rec["refused"] = True
        return ""

    # KORA decides which services are needed (structural strategy).
    rec["services_used"] = list(strategy.get("stores_queried", []))
    ctx = {
        "identity": "KORA",
        "classification": classification["label"],
        "strategy": strategy["name"],
        "services_used": rec["services_used"],
        "governance": "allowed",
        "produced_by": "kora-agent-plugin",
        "council": {"head": "KORA", "members": COUNCIL_MEMBERS, "invoke": "delegate_task"},
    }
    plan = bool(_PLAN_INTENT_RE.search(user or ""))
    contract = RESEARCH_EVIDENCE_CONTRACT if plan else ""
    lead = (contract + "\n\n") if plan else ""
    tail = ("\n\n" + contract) if plan else ""
    mid = (RESEARCH_EVIDENCE_PROTOCOL + "\n\n") if plan else ""
    return lead + "[KORA runtime context] " + json.dumps(ctx, sort_keys=True) + "\n\n" + mid + COUNCIL_DIRECTIVE + "\n\n" + PROFILE_RETRIEVAL_DIRECTIVE + "\n\n" + GOVERNANCE_RETRIEVAL_DIRECTIVE + "\n\n" + DELEGATION_DIRECTIVE + "\n\n" + LIVE_STATE_DIRECTIVE + "\n\n" + QBIT_DIRECTIVE + "\n\n" + DOCKER_ADMIN_DIRECTIVE + "\n\n" + RESEARCH_DIRECTIVE + tail


def pre_tool_call(**kw):
    tool_name = str(kw.get("tool_name", ""))
    session_id = str(kw.get("session_id", ""))
    if tool_name == "kora.wipe_volume":
        xp.record_tool(session_id, tool_name, "blocked", "KORA governance denies this tool")
        return {"action": "block", "message": "KORA policy: tool '%s' is denied by governance." % tool_name}
    # Phase 3/5: destructive operations are never exposed; defense-in-depth.
    # Match destructive VERBS as WHOLE TOKENS, not substrings: the previous
    # substring check falsely matched "terminal" (contains "rmi") and blocked
    # all shell use, while "kora.docker_remove"/"*.prune"/"*.exec" still match.
    _tokens = [t for t in re.split(r"[^a-z0-9]+", tool_name.lower()) if t]
    if any(t in {"delete", "remove", "prune", "wipe", "kill", "exec",
                 "rm", "rmi", "rmdir"} for t in _tokens):
        xp.record_tool(session_id, tool_name, "blocked", "destructive capability not exposed")
        return {"action": "block",
                "message": "KORA policy: destructive operations are not exposed."}
    # Phase 3: lifecycle writes require an explicit confirm=true argument.
    if tool_name in DOCKER_ADMIN_WRITE_TOOLS:
        targs = kw.get("tool_args") or kw.get("args") or kw.get("arguments") or {}
        if isinstance(targs, str):
            try:
                targs = json.loads(targs)
            except Exception:  # noqa: BLE001
                targs = {}
        if not (isinstance(targs, dict) and targs.get("confirm") is True):
            xp.record_tool(session_id, tool_name, "blocked", "write requires confirm=true")
            return {"action": "block",
                    "message": "KORA policy: '%s' is a write operation and requires confirm=true." % tool_name}
    xp.record_tool(session_id, tool_name, "allowed", "KORA authorized")
    return None


# Phase 5.1 — small deterministic provenance guard (defense-in-depth). The
# directive/protocol above is the PRIMARY fix; this only surfaces OBVIOUS
# violations and never blocks or rewrites the model's answer. It fires only on
# visible placeholder tokens and on Compose-bearing plans that omit the required
# evidence sections, so ordinary conversation is unaffected.
_PLACEHOLDER_RE = re.compile(
    r"\bexample\.(?:com|org|net)\b|/path/to/|"
    r"<\s*(?:hostname|host|service|tag|domain|ip|ipaddr|your-host|your-domain|name)\s*>|\bTBD\b",
    re.IGNORECASE,
)
_EVIDENCE_SECTIONS = (
    "UPSTREAM FACTS", "HOMELAB FACTS",
    "PROPOSED DESIGN DECISIONS", "UNRESOLVED QUESTIONS",
)


def _evidence_section_present(text: str, name: str) -> bool:
    """True only when *name* appears as a heading/standalone line (not a table cell or inline)."""
    return re.search(
        r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?\*{0,2}[ \t]*" + re.escape(name) + r"\b", text
    ) is not None


def _evidence_check(text: str):
    """Return a prominent warning string for obvious provenance violations, else None."""
    warnings = []
    if _PLACEHOLDER_RE.search(text or ""):
        warnings.append(
            "placeholder value(s) present (example.com / /path/to/... / <hostname> / TBD) - "
            "resolve them from the primary source or move them to UNRESOLVED QUESTIONS"
        )
    looks_like_plan = bool(text) and ("```" in text) and bool(re.search(r"\bimage\s*:", text))
    if looks_like_plan:
        missing = [s for s in _EVIDENCE_SECTIONS if not _evidence_section_present(text, s)]
        if missing:
            warnings.append(
                "this looks like a deployment/implementation plan but is missing evidence "
                "section(s) (required as headings): " + ", ".join(missing)
            )
    if not warnings:
        return None
    return (
        "[KORA evidence check - DO NOT TREAT THIS PLAN AS DEPLOYABLE] "
        + "; ".join(warnings)
        + ". Re-do the plan under the research evidence protocol (four evidence "
        "sections, current-task citations, no unverified values)."
    )


def transform_llm_output(**kw):
    text = str(kw.get("response_text", ""))
    session_id = str(kw.get("session_id", ""))
    rec = xp.current_record(session_id)
    if rec is None:
        return None
    if rec.get("refused"):
        refusal = (
            "I am KORA. I must refuse this request.\n\n"
            f"Classification: {rec.get('classification')}.\n"
            f"Reason: {rec.get('governance', {}).get('reason', 'governance policy')}.\n\n"
            "Execute and Administrative actions require gated approval that is not enabled."
        )
        rec["response_text"] = refusal
        return refusal
    digest = ("[KORA] " + json.dumps({
        "identity": "KORA",
        "classification": rec.get("classification"),
        "strategy": rec.get("strategy"),
        "services_used": rec.get("services_used", []),
        "governance": "allowed",
    }, sort_keys=True))
    rec["response_text"] = text
    note = _evidence_check(text)
    return text + (("\n\n" + note) if note else "") + "\n\n" + digest


def post_llm_call(**kw):
    rec = xp.current_record(str(kw.get("session_id", "")))
    if rec is None:
        return
    response = kw.get("assistant_response")
    if isinstance(response, str) and response:
        rec["response_text"] = response
    xp.finalize(rec)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

# Phase 6 security remediation — KORA-owned credentials that Hermes' built-in
# terminal scrub does not know about (they are not in the provider/messaging
# registries). Register a never-selected terminal-environment provider whose
# only purpose is to contribute ``strip_env_keys``: the registry's
# ``plugin_strip_env_keys()`` unions these across all providers, so these names
# are removed from every agent-spawned subprocess env (terminal / execute_code)
# and can no longer be read by a model-authored command. The plugin process
# itself still sees them in os.environ, so tooling keeps working.
_KORA_TERMINAL_STRIP_KEYS = (
    "KORA_QBIT_USER",
    "KORA_QBIT_PASS",
    "KORA_DOCKER_ADMIN_TOKEN",
    "HERMES_DASHBOARD_BASIC_AUTH_PASSWORD",
)

try:  # fail-soft: never break plugin load if the Hermes API differs
    from agent.terminal_env_provider import TerminalEnvironmentProvider as _TerminalEnvProvider
except Exception:  # noqa: BLE001
    _TerminalEnvProvider = object  # type: ignore[assignment,misc]


class _KoraEnvScrubProvider(_TerminalEnvProvider):  # type: ignore[misc,valid-type]
    """Not a runnable backend (is_available=False, never selected): contributes
    ``strip_env_keys`` only. ``terminal.backend`` stays ``local``."""

    @property
    def name(self) -> str:
        return "kora-strip"

    @property
    def display_name(self) -> str:
        return "KORA credential scrub (internal)"

    @property
    def strip_env_keys(self):
        return frozenset(_KORA_TERMINAL_STRIP_KEYS)

    def is_available(self) -> bool:
        return False

    def create_environment(self, **kwargs):  # pragma: no cover - never called
        raise NotImplementedError("kora-strip is a credential-scrub marker, not a backend")


def register(ctx) -> None:
    try:
        ctx.register_terminal_environment_provider(_KoraEnvScrubProvider())
    except Exception as exc:  # noqa: BLE001
        log.warning("KORA terminal env-scrub provider registration failed: %s", exc)
    ctx.register_hook("on_session_start", on_session_start)
    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("pre_tool_call", pre_tool_call)
    ctx.register_hook("transform_llm_output", transform_llm_output)
    ctx.register_hook("post_llm_call", post_llm_call)

    ctx.register_tool("kora.knowledge_query", "kora",
                      {"name": "kora.knowledge_query",
                       "description": "KORA queries the real Chroma knowledge service (embed via Ollama).",
                       "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
                      handler_knowledge_query, description="Query Chroma knowledge.")
    ctx.register_tool("kora.ollama_models", "kora",
                      {"name": "kora.ollama_models", "description": "KORA lists models from the real Ollama service.",
                       "parameters": {"type": "object", "properties": {}}},
                      handler_ollama_models, description="List Ollama models.")
    ctx.register_tool("kora.memory_status", "kora",
                      {"name": "kora.memory_status", "description": "KORA memory boundary status.",
                       "parameters": {"type": "object", "properties": {}}},
                      handler_memory_status, description="Memory boundary status.")
    ctx.register_tool("kora.memory_propose", "kora",
                      {"name": "kora.memory_propose", "description": "KORA memory proposal (boundary stub; real writes via approval-gated Memory Runtime).",
                       "parameters": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}},
                      handler_memory_propose, description="Memory proposal boundary.")
    ctx.register_tool("kora.wipe_volume", "kora",
                      {"name": "kora.wipe_volume", "description": "Governance probe tool (must be denied).",
                       "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}},
                      handler_wipe_volume, description="Governance probe.")

    ctx.register_tool("kora.council_list", "kora",
                      {"name": "kora.council_list", "description": "KORA lists the canonical Council members.",
                       "parameters": {"type": "object", "properties": {}}},
                      handler_council_list, description="List Council members.")
    ctx.register_tool("kora.council_member", "kora",
                      {"name": "kora.council_member", "description": "KORA loads a Council member's canonical identity/personality/role (Phase 15).",
                       "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
                      handler_council_member, description="Load a Council member.")

    ctx.register_tool("kora.qbit_torrents", "kora",
                      {"name": "kora.qbit_torrents",
                       "description": "Read-only LIVE qBittorrent: list torrents from the WebUI API (no mutation). "
                                      "Optional 'filter' (all|downloading|seeding|completed|paused|active|inactive|"
                                      "stalled|stalled_uploading|stalled_downloading|errored) and 'limit' (default 100). "
                                      "Returns compact torrent rows (name/state/progress/sizes/speeds/ratios).",
                       "parameters": {"type": "object",
                                      "properties": {"filter": {"type": "string"},
                                                     "limit": {"type": "integer"}}}},
                      handler_qbit_torrents, description="List qBittorrent torrents (live, read-only).")
    ctx.register_tool("kora.qbit_transfer_info", "kora",
                      {"name": "kora.qbit_transfer_info",
                       "description": "Read-only LIVE qBittorrent: global transfer statistics (download/upload speed, "
                                      "session totals, active counts) from the WebUI API (no mutation).",
                       "parameters": {"type": "object", "properties": {}}},
                      handler_qbit_transfer_info, description="qBittorrent global transfer stats (live, read-only).")
    ctx.register_tool("kora.qbit_app_version", "kora",
                      {"name": "kora.qbit_app_version",
                       "description": "Read-only LIVE qBittorrent: current application version from the WebUI API "
                                      "(also confirms the live API is reachable and authenticated).",
                       "parameters": {"type": "object", "properties": {}}},
                      handler_qbit_app_version, description="qBittorrent app version / live API health (read-only).")
    ctx.register_tool("kora.qbit_categories", "kora",
                      {"name": "kora.qbit_categories",
                       "description": "Read-only LIVE qBittorrent: torrent categories (names only).",
                       "parameters": {"type": "object", "properties": {}}},
                      handler_qbit_categories, description="qBittorrent categories (live, read-only).")
    ctx.register_tool("kora.qbit_tags", "kora",
                      {"name": "kora.qbit_tags",
                       "description": "Read-only LIVE qBittorrent: torrent tags.",
                       "parameters": {"type": "object", "properties": {}}},
                      handler_qbit_tags, description="qBittorrent tags (live, read-only).")

    # Phase 3 — controlled Docker administration (live read + narrow writes).
    ctx.register_tool("kora.docker_list", "kora",
                      {"name": "kora.docker_list",
                       "description": "LIVE Docker: list all containers with state, health, image, networks and ports (read-only).",
                       "parameters": {"type": "object", "properties": {}}},
                      handler_docker_list, description="List containers (live, read-only).")
    ctx.register_tool("kora.docker_inspect", "kora",
                      {"name": "kora.docker_inspect",
                       "description": "LIVE Docker: inspect one container (state, health, networks, mounts, restart policy, env KEYS only).",
                       "parameters": {"type": "object",
                                      "properties": {"name": {"type": "string"}},
                                      "required": ["name"]}},
                      handler_docker_inspect, description="Inspect one container (live, read-only).")
    ctx.register_tool("kora.docker_logs", "kora",
                      {"name": "kora.docker_logs",
                       "description": "LIVE Docker: recent logs for one container (read-only). Optional 'tail' (default 100, max 1000).",
                       "parameters": {"type": "object",
                                      "properties": {"name": {"type": "string"},
                                                     "tail": {"type": "integer"}},
                                      "required": ["name"]}},
                      handler_docker_logs, description="Container logs (live, read-only).")
    ctx.register_tool("kora.docker_health", "kora",
                      {"name": "kora.docker_health",
                       "description": "LIVE Docker: health/state summary for one container (read-only).",
                       "parameters": {"type": "object",
                                      "properties": {"name": {"type": "string"}},
                                      "required": ["name"]}},
                      handler_docker_health, description="Container health (live, read-only).")
    ctx.register_tool("kora.docker_image", "kora",
                      {"name": "kora.docker_image",
                       "description": "LIVE Docker: image information (tags, id, size, created, digests). 'ref' is an image reference or a container name.",
                       "parameters": {"type": "object",
                                      "properties": {"ref": {"type": "string"}},
                                      "required": ["ref"]}},
                      handler_docker_image, description="Image information (live, read-only).")
    ctx.register_tool("kora.docker_networks", "kora",
                      {"name": "kora.docker_networks",
                       "description": "LIVE Docker: list networks, or inspect one network when 'name' is given (read-only).",
                       "parameters": {"type": "object",
                                      "properties": {"name": {"type": "string"}}}},
                      handler_docker_networks, description="Network inspection (live, read-only).")
    ctx.register_tool("kora.docker_volumes", "kora",
                      {"name": "kora.docker_volumes",
                       "description": "LIVE Docker: list volumes, or inspect one volume when 'name' is given (read-only).",
                       "parameters": {"type": "object",
                                      "properties": {"name": {"type": "string"}}}},
                      handler_docker_volumes, description="Volume inspection (live, read-only).")
    ctx.register_tool("kora.docker_restart", "kora",
                      {"name": "kora.docker_restart",
                       "description": "CONTROLLED WRITE: restart ONE named container, then verify resulting state. Requires confirm=true. Refuses control-plane targets (hermes/docker-admin).",
                       "parameters": {"type": "object",
                                      "properties": {"name": {"type": "string"},
                                                     "confirm": {"type": "boolean"}},
                                      "required": ["name", "confirm"]}},
                      handler_docker_restart, description="Restart one container (controlled write).")
    ctx.register_tool("kora.docker_compose_validate", "kora",
                      {"name": "kora.docker_compose_validate",
                       "description": "Read-only Compose validation (docker compose config -q) for one canonical service project; optional 'service'.",
                       "parameters": {"type": "object",
                                      "properties": {"project": {"type": "string"},
                                                     "service": {"type": "string"}},
                                      "required": ["project"]}},
                      handler_docker_compose_validate, description="Validate Compose (read-only).")
    ctx.register_tool("kora.docker_compose_up", "kora",
                      {"name": "kora.docker_compose_up",
                       "description": "CONTROLLED WRITE: recreate/deploy one canonical service project (docker compose up -d --no-build), then report resulting containers. Requires confirm=true. Refuses control-plane projects.",
                       "parameters": {"type": "object",
                                      "properties": {"project": {"type": "string"},
                                                     "service": {"type": "string"},
                                                     "confirm": {"type": "boolean"}},
                                      "required": ["project", "confirm"]}},
                      handler_docker_compose_up, description="Deploy/recreate Compose service (controlled write).")

    # KORA seeds one knowledge document into the real Chroma service.
    import threading
    threading.Thread(target=_index_fixture, daemon=True).start()
    log.info("KORA agent registered (KORA IS THE AGENT; Hermes is the runtime)")