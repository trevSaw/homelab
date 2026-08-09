"""KORA Solo Runtime — Phase 14.3 Knowledge Platform.

OpenAI-compatible façade between Open WebUI and local Ollama.
Memory proposals are event-driven and approved content persists only through
the durable-store adapter. Knowledge retrieval is classification-driven and
remains separate from Memory.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from .approval_engine import InvalidProposalTransitionError, ProposalNotFoundError
from .auth import (
    AuthenticationError,
    AuthorizationError,
    BearerAuthorizer,
    MemoryScope,
    Principal,
)
from .commit_coordinator import CommitFailedError, MemoryCommitCoordinator
from .event_bus import InProcessEventBus
from .honcho_adapter import durable_store_from_config
from .memory_models import ProposalStatus
from .memory_runtime import (
    EventDrivenMemoryRuntime,
    MemoryRuntimeConfig,
    ProposalIneligibleError,
)
from .proposal_repository import InMemoryProposalRepository, SQLiteProposalRepository

try:
    from Knowledge.config import KnowledgeConfig
    from Knowledge.service import build_knowledge_service
except ImportError:  # pragma: no cover - non-Runtime environments
    KnowledgeConfig = None  # type: ignore[assignment,misc]
    build_knowledge_service = None  # type: ignore[assignment]

PRODUCT_NAME = "KORA"
PRODUCT_AKA = "Brainiac"
CONFIG_DIR = Path(os.environ.get("KORA_CONFIG_DIR", "/config"))
PROMPTS_DIR = Path(os.environ.get("KORA_PROMPTS_DIR", "/prompts"))
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434").rstrip("/")
DEFAULT_MODEL = os.environ.get("KORA_DEFAULT_MODEL", "qwen3:8b")
LOG_LEVEL = os.environ.get("KORA_LOG_LEVEL", "INFO")

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("kora")

app = FastAPI(title="KORA Runtime", version="14.3.0", docs_url=None, redoc_url=None)


def _load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


RUNTIME = _load_yaml("runtime.yaml")
COUNCIL = _load_yaml("council_registration.yaml")
HERMES = _load_yaml("hermes_registration.yaml")
MEMORY_CONFIG = _load_yaml("memory_runtime.yaml")
KNOWLEDGE_CONFIG = _load_yaml("knowledge_runtime.yaml")

EVENT_BUS = InProcessEventBus()
WORKFLOW_CONFIG = MEMORY_CONFIG.get("workflow") or {}
if WORKFLOW_CONFIG.get("sqlite_enabled", False):
    database_path = os.environ.get(
        "KORA_MEMORY_DB_PATH",
        str(WORKFLOW_CONFIG.get("database_path", "/data/memory-runtime.sqlite3")),
    )
    PROPOSAL_REPOSITORY = SQLiteProposalRepository(database_path)
else:
    PROPOSAL_REPOSITORY = InMemoryProposalRepository()

MEMORY_RUNTIME = EventDrivenMemoryRuntime(
    EVENT_BUS,
    MemoryRuntimeConfig.from_dict(MEMORY_CONFIG),
    repository=PROPOSAL_REPOSITORY,
)
DURABLE_STORE = durable_store_from_config(MEMORY_CONFIG)
COMMIT_COORDINATOR = MemoryCommitCoordinator(MEMORY_RUNTIME, DURABLE_STORE)
MEMORY_AUTHORIZER = BearerAuthorizer.from_environment()
RECOVERY_STATE: dict[str, Any] = {"status": "not_started"}

if KnowledgeConfig is not None and build_knowledge_service is not None:
    _knowledge_cfg = KnowledgeConfig.from_dict(KNOWLEDGE_CONFIG).with_env_overrides()
    from Knowledge.storage.in_memory import InMemoryKnowledgeStore

    KNOWLEDGE_STORE = InMemoryKnowledgeStore()
    KNOWLEDGE_SERVICE = build_knowledge_service(
        config=_knowledge_cfg,
        store=KNOWLEDGE_STORE,
        event_bus=EVENT_BUS,
    )
else:  # pragma: no cover - non-Runtime environments
    KNOWLEDGE_STORE = None
    KNOWLEDGE_SERVICE = None


@app.on_event("startup")
async def recover_memory_runtime() -> None:
    global RECOVERY_STATE
    consistency = PROPOSAL_REPOSITORY.consistency_check()
    try:
        recovery = await COMMIT_COORDINATOR.recover()
        RECOVERY_STATE = {
            "status": "ok" if consistency["status"] == "ok" else "error",
            "repository": consistency,
            "recovery": recovery,
        }
    except Exception as exc:  # noqa: BLE001
        log.exception("Memory Runtime recovery failed")
        RECOVERY_STATE = {
            "status": "error",
            "repository": consistency,
            "error_type": type(exc).__name__,
        }


def _solo_system_prompt() -> str:
    path = PROMPTS_DIR / "solo_system.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return (
        f"You are {PRODUCT_NAME} ({PRODUCT_AKA}). "
        "Refuse Execute/Administrative actions in Stage 1."
    )


EXECUTE_PATTERNS = [
    r"\b(delete|destroy|wipe|format)\b.+\b(volume|dataset|zfs|disk|database)\b",
    r"\b(rm\s+-rf|docker\s+compose\s+down\s+-v|drop\s+database)\b",
    r"\bexecute\b.+\b(against|on)\b.+\b(production|homelab|host)\b",
    r"\b(restart|stop|kill)\b.+\b(all\s+)?(containers?|services?)\b.+\b(now|immediately)\b",
]

ADMIN_PATTERNS = [
    r"\b(change|rotate|reset)\b.+\b(root|admin)\b.+\bpassword\b",
    r"\b(disable|bypass)\b.+\b(auth|authentication|traefik|firewall)\b",
    r"\bgrant\b.+\b(root|sudo|admin)\b.+\baccess\b",
]


def classify(text: str) -> dict[str, Any]:
    """Stage 1 classifier — heuristic only; no store retrieval before this."""
    lower = text.lower().strip()
    for pattern in EXECUTE_PATTERNS:
        if re.search(pattern, lower, re.I):
            return {
                "label": "execute_forbidden",
                "confidence": "high",
                "rationale": "Request appears to seek ungated Execute against the environment",
            }
    for pattern in ADMIN_PATTERNS:
        if re.search(pattern, lower, re.I):
            return {
                "label": "administrative_forbidden",
                "confidence": "high",
                "rationale": "Request appears to seek administrative privilege changes",
            }
    if re.search(r"\b(who are you|your name|what are you)\b", lower):
        return {
            "label": "identity",
            "confidence": "high",
            "rationale": "Identity / branding question",
        }
    if re.search(r"\b(remember|preference|prefer|always do)\b", lower):
        return {
            "label": "preference",
            "confidence": "medium",
            "rationale": "Preference-like language; Memory capture requires explicit approval",
        }
    if re.search(r"\b(architecture|adr|standard|policy)\b", lower):
        return {
            "label": "architecture",
            "confidence": "medium",
            "rationale": "Architecture-like question; Knowledge Runtime disabled in Stage 1",
        }
    return {
        "label": "general",
        "confidence": "medium",
        "rationale": "General conversational request",
    }


def select_strategy(classification: dict[str, Any]) -> dict[str, Any]:
    """Context Intelligence stub — Phase 14.3 Knowledge retrieval is enabled for
    architecture-style queries; Memory and Tools remain off the chat path."""
    label = classification["label"]
    query_knowledge = label == "architecture"
    query_memory = False
    query_tools = False
    stores_queried: list[str] = []
    stores_skipped = ["memory", "tools", "agents", "graphify"]
    skip_reasons: dict[str, str] = {
        "memory": "Memory retrieval is internal and not on the chat path",
        "tools": "Tool Runtime not enabled until Phase 14.5",
        "agents": "Autonomous agents not enabled until a later phase",
        "graphify": "Graphify is planned for Phase 14.4; not implemented",
    }
    if query_knowledge:
        stores_queried.append("knowledge")
    else:
        stores_skipped.append("knowledge")
        skip_reasons["knowledge"] = "Knowledge retrieval not selected for this classification"
    return {
        "name": f"solo_stage1_{label}",
        "query_memory": query_memory,
        "query_knowledge": query_knowledge,
        "query_tools": query_tools,
        "stores_queried": stores_queried,
        "stores_skipped": stores_skipped,
        "skip_reasons": skip_reasons,
        "budgets": {"memory": 0, "knowledge": 1 if query_knowledge else 0, "tools": 0, "conversation": 1},
        "confidence_posture": "conversation_only",
    }


def assemble_context(messages: list[dict[str, Any]], strategy: dict[str, Any]) -> dict[str, Any]:
    return {
        "provenance": [
            {
                "source_class": "conversation",
                "source_ref": "open-webui-session",
                "authority_or_confidence": "user-supplied",
                "retrieval_reason": "active turn",
            }
        ],
        "stores_queried": strategy["stores_queried"],
        "stores_skipped": strategy["stores_skipped"],
        "message_count": len(messages),
        "laundering": False,
    }


def explainability(
    classification: dict[str, Any],
    strategy: dict[str, Any],
    assembly: dict[str, Any],
    refused: bool,
) -> dict[str, Any]:
    return {
        "identity": PRODUCT_NAME,
        "aka": PRODUCT_AKA,
        "profile": "solo",
        "phase": "14.3",
        "classification": classification,
        "retrieval_strategy": strategy["name"],
        "stores_queried": strategy["stores_queried"],
        "stores_skipped": strategy["stores_skipped"],
        "skip_reasons": strategy["skip_reasons"],
        "council": {
            "mode": COUNCIL.get("mode", "conceptual"),
            "chair": COUNCIL.get("chair", PRODUCT_NAME),
            "contributors": [PRODUCT_NAME],
        },
        "hermes": {
            "on_primary_path": False,
            "role": HERMES.get("role", "thin_execution_layer"),
        },
        "provenance": assembly["provenance"],
        "refused": refused,
        "raw_chain_of_thought": False,
    }


def _user_text(messages: list[dict[str, Any]]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, list):
                parts = [p.get("text", "") for p in content if isinstance(p, dict)]
                return " ".join(parts)
            return str(content)
    return ""


async def _retrieve_knowledge_context(
    user_text: str,
    strategy: dict[str, Any],
    classification: dict[str, Any],
) -> dict[str, Any]:
    """Phase 14.3 — retrieve Knowledge context when the strategy selects it.

    Degrades gracefully: any failure yields empty context so the chat path is
    never broken by Knowledge backend unavailability.
    """
    if not strategy.get("query_knowledge"):
        return {"text": "", "status": "skipped", "sources": [], "chunks": []}
    if KNOWLEDGE_SERVICE is None:
        return {"text": "", "status": "disabled", "sources": [], "chunks": []}
    try:
        context = await KNOWLEDGE_SERVICE.build_context(user_text)
        return {
            "text": context.knowledge_text,
            "status": context.status,
            "sources": list(context.sources),
            "chunks": [chunk for chunk in context.chunks],
        }
    except Exception as exc:  # noqa: BLE001
        log.warning("knowledge retrieval degraded during chat turn: %s", exc)
        return {"text": "", "status": "degraded", "sources": [], "chunks": []}


def _refusal_message(classification: dict[str, Any]) -> str:
    return (
        f"I am {PRODUCT_NAME}. I must refuse this request in Stage 1 (Solo Runtime).\n\n"
        f"Classification: {classification['label']}.\n"
        f"Reason: {classification['rationale']}.\n\n"
        "Execute and Administrative actions require gated approval UX that is not enabled yet. "
        "Memory retrieval, Knowledge, and Tools remain disabled on the chat path."
    )


async def ollama_chat(model: str, messages: list[dict[str, Any]], stream: bool) -> Any:
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    timeout = httpx.Timeout(float(RUNTIME.get("inference", {}).get("timeout_seconds", 300)))
    client = httpx.AsyncClient(timeout=timeout)
    try:
        if stream:
            req = client.build_request("POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            resp = await client.send(req, stream=True)
            if resp.status_code >= 400:
                body = await resp.aread()
                await resp.aclose()
                await client.aclose()
                raise HTTPException(status_code=502, detail=f"Ollama error: {body.decode()[:500]}")
            return resp, client
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        await client.aclose()
        if resp.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Ollama error: {resp.text[:500]}")
        return resp.json()
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"Ollama unreachable: {exc}") from exc


async def ollama_tags() -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            models = resp.json().get("models", [])
            return [
                {
                    "id": m.get("name", "unknown"),
                    "object": "model",
                    "created": 0,
                    "owned_by": "ollama",
                }
                for m in models
            ]
    except Exception as exc:  # noqa: BLE001
        log.warning("Failed to list Ollama models: %s", exc)
        return [
            {
                "id": DEFAULT_MODEL,
                "object": "model",
                "created": 0,
                "owned_by": "ollama",
            }
        ]


@app.get("/health")
async def health() -> dict[str, Any]:
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            ollama_ok = r.status_code == 200
    except Exception:  # noqa: BLE001
        ollama_ok = False
    status = "ok" if ollama_ok else "degraded"
    return {
        "status": status,
        "product": PRODUCT_NAME,
        "profile": "solo",
        "phase": "14.3",
        "ollama": ollama_ok,
        "council_mode": COUNCIL.get("mode", "conceptual"),
        "hermes_role": HERMES.get("role", "thin_execution_layer"),
        "event_bus": "in_process",
        "pending_memory_proposals": len(MEMORY_RUNTIME.list_pending()),
        "memory_repository": PROPOSAL_REPOSITORY.consistency_check(),
        "memory_recovery": RECOVERY_STATE,
        "knowledge": await _knowledge_health(),
    }


async def _knowledge_health() -> dict[str, Any]:
    if KNOWLEDGE_SERVICE is None:
        return {"status": "disabled", "phase": "14.3"}
    try:
        return await KNOWLEDGE_SERVICE.health()
    except Exception as exc:  # noqa: BLE001
        log.warning("knowledge health degraded: %s", exc)
        return {"status": "degraded", "phase": "14.3", "error": type(exc).__name__}


@app.get("/v1/models")
async def list_models() -> dict[str, Any]:
    return {"object": "list", "data": await ollama_tags()}


def _authorize(request: Request, scope: MemoryScope) -> Principal:
    try:
        return MEMORY_AUTHORIZER.authorize(request.headers.get("Authorization"), scope)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


async def _optional_json(request: Request) -> dict[str, Any]:
    if not await request.body():
        return {}
    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="request body must be an object")
    return body


@app.get("/v1/memory/proposals")
async def list_memory_proposals(
    request: Request,
    status: ProposalStatus = ProposalStatus.PENDING_REVIEW,
) -> dict[str, Any]:
    _authorize(request, MemoryScope.READ)
    MEMORY_RUNTIME.expire_due()
    proposals = MEMORY_RUNTIME.list_by_status(status)
    return {
        "object": "list",
        "status": status.value,
        "data": [proposal.to_dict() for proposal in proposals],
    }


@app.get("/v1/memory/proposals/{proposal_id}")
async def get_memory_proposal(proposal_id: str, request: Request) -> dict[str, Any]:
    _authorize(request, MemoryScope.READ)
    MEMORY_RUNTIME.expire_due()
    try:
        return MEMORY_RUNTIME.get_proposal(proposal_id).to_dict()
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc


@app.post("/v1/memory/proposals/{proposal_id}/approve")
async def approve_memory_proposal(proposal_id: str, request: Request) -> dict[str, Any]:
    principal = _authorize(request, MemoryScope.APPROVE)
    body = await _optional_json(request)
    try:
        proposal = await COMMIT_COORDINATOR.approve_and_commit(
            proposal_id,
            actor=principal.principal_id,
            text_final=body.get("text_final"),
        )
        return proposal.to_dict()
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc
    except ProposalIneligibleError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (CommitFailedError, InvalidProposalTransitionError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/v1/memory/proposals/{proposal_id}/reject")
async def reject_memory_proposal(proposal_id: str, request: Request) -> dict[str, Any]:
    principal = _authorize(request, MemoryScope.APPROVE)
    body = await _optional_json(request)
    try:
        return MEMORY_RUNTIME.reject(
            proposal_id,
            actor=principal.principal_id,
            reason=body.get("reason"),
        ).to_dict()
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc
    except InvalidProposalTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/v1/memory/proposals/{proposal_id}/withdraw")
async def withdraw_memory_proposal(proposal_id: str, request: Request) -> dict[str, Any]:
    principal = _authorize(request, MemoryScope.OPERATE)
    body = await _optional_json(request)
    try:
        return MEMORY_RUNTIME.withdraw(
            proposal_id,
            actor=principal.principal_id,
            reason=body.get("reason"),
        ).to_dict()
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc
    except InvalidProposalTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/v1/memory/proposals/{proposal_id}/expire")
async def expire_memory_proposal(proposal_id: str, request: Request) -> dict[str, Any]:
    principal = _authorize(request, MemoryScope.OPERATE)
    try:
        return MEMORY_RUNTIME.expire(
            proposal_id,
            actor=principal.principal_id,
        ).to_dict()
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc
    except InvalidProposalTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> Any:
    body = await request.json()
    messages = body.get("messages") or []
    model = body.get("model") or DEFAULT_MODEL
    stream = bool(body.get("stream", False))
    user_text = _user_text(messages)

    classification = classify(user_text)
    strategy = select_strategy(classification)
    assembly = assemble_context(messages, strategy)
    refused = classification["label"] in {"execute_forbidden", "administrative_forbidden"}
    explanation = explainability(classification, strategy, assembly, refused)

    log.info(
        "turn classification=%s strategy=%s refused=%s model=%s",
        classification["label"],
        strategy["name"],
        refused,
        model,
    )

    if refused:
        content = _refusal_message(classification)
        return _openai_response(model, content, explanation, finish_reason="stop")

    knowledge_context = await _retrieve_knowledge_context(
        user_text, strategy, classification
    )

    system = {
        "role": "system",
        "content": _solo_system_prompt()
        + "\n\n[Stage-1 explainability context]\n"
        + json.dumps(
            {
                "classification": classification["label"],
                "stores_queried": strategy["stores_queried"],
                "stores_skipped": strategy["stores_skipped"],
                "council_mode": "solo_conceptual",
            },
            indent=2,
        )
        + (f"\n\n[Knowledge context]\n{knowledge_context['text']}" if knowledge_context["text"] else ""),
    }
    ollama_messages = [system] + [
        {"role": m.get("role", "user"), "content": _stringify_content(m.get("content", ""))}
        for m in messages
        if m.get("role") in {"user", "assistant", "system"}
    ]

    if stream:
        return await _stream_completion(model, ollama_messages, explanation)

    result = await ollama_chat(model, ollama_messages, stream=False)
    content = (result.get("message") or {}).get("content", "")
    return _openai_response(model, content, explanation, finish_reason="stop")


def _stringify_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            p.get("text", "") if isinstance(p, dict) else str(p) for p in content
        )
    return str(content)


def _openai_response(
    model: str,
    content: str,
    explanation: dict[str, Any],
    finish_reason: str,
) -> JSONResponse:
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    payload = {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": finish_reason,
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "kora": explanation,
    }
    return JSONResponse(payload)


async def _stream_completion(
    model: str,
    messages: list[dict[str, Any]],
    explanation: dict[str, Any],
) -> StreamingResponse:
    resp, client = await ollama_chat(model, messages, stream=True)
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())

    async def event_gen():
        try:
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                piece = (chunk.get("message") or {}).get("content", "")
                done = bool(chunk.get("done"))
                if piece:
                    data = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": piece},
                                "finish_reason": None,
                            }
                        ],
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                if done:
                    final = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop",
                            }
                        ],
                        "kora": explanation,
                    }
                    yield f"data: {json.dumps(final)}\n\n"
                    yield "data: [DONE]\n\n"
                    break
        finally:
            await resp.aclose()
            await client.aclose()

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "product": PRODUCT_NAME,
        "aka": PRODUCT_AKA,
        "phase": "14.3",
        "profile": "solo",
        "message": "KORA Runtime — Solo conductor with approval-gated durable Memory and Knowledge retrieval",
    }
