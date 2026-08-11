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
import time
import uuid
from pathlib import Path

import httpx

log = logging.getLogger("kora.agent")

OLLAMA = os.environ.get("KORA_STAGING_OLLAMA", "http://ollama:11434")
CHROMA = os.environ.get("KORA_STAGING_CHROMA", "http://chromadb:8000")
EMBED_MODEL = os.environ.get("KORA_STAGING_EMBED_MODEL", "nomic-embed-text")
EXPLAIN_DIR = Path(os.environ.get("HERMES_HOME", "/opt/data")) / "kora-explain"
EXPLAIN_PATH = EXPLAIN_DIR / "records.jsonl"

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
# KORA hooks (structural intelligence + governance + composition + records)
# ---------------------------------------------------------------------------

def on_session_start(**kw) -> None:
    xp.set_session(kw.get("session_id", ""), {"started": time.time()})


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
    }
    return "[KORA runtime context] " + json.dumps(ctx, sort_keys=True)


def pre_tool_call(**kw):
    tool_name = str(kw.get("tool_name", ""))
    session_id = str(kw.get("session_id", ""))
    if tool_name == "kora.wipe_volume":
        xp.record_tool(session_id, tool_name, "blocked", "KORA governance denies this tool")
        return {"action": "block", "message": "KORA policy: tool '%s' is denied by governance." % tool_name}
    xp.record_tool(session_id, tool_name, "allowed", "KORA authorized")
    return None


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
    return text + "\n\n" + digest


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

def register(ctx) -> None:
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

    # KORA seeds one knowledge document into the real Chroma service.
    import threading
    threading.Thread(target=_index_fixture, daemon=True).start()
    log.info("KORA agent registered (KORA IS THE AGENT; Hermes is the runtime)")
