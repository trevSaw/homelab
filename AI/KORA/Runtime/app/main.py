"""KORA Solo Runtime — Phase 14.1 Stage 1 conductor.

OpenAI-compatible façade between Open WebUI and local Ollama.
Does not implement Memory, Knowledge, Tools, MCP, or multi-member Council.
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

PRODUCT_NAME = "KORA"
PRODUCT_AKA = "Brainiac"
CONFIG_DIR = Path(os.environ.get("KORA_CONFIG_DIR", "/config"))
PROMPTS_DIR = Path(os.environ.get("KORA_PROMPTS_DIR", "/prompts"))
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434").rstrip("/")
DEFAULT_MODEL = os.environ.get("KORA_DEFAULT_MODEL", "qwen3:8b")
LOG_LEVEL = os.environ.get("KORA_LOG_LEVEL", "INFO")

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("kora")

app = FastAPI(title="KORA Runtime", version="14.1.0", docs_url=None, redoc_url=None)


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
            "rationale": "Preference-like language; Memory Runtime disabled in Stage 1",
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
    """Context Intelligence stub — all external stores skipped in Stage 1."""
    label = classification["label"]
    return {
        "name": f"solo_stage1_{label}",
        "query_memory": False,
        "query_knowledge": False,
        "query_tools": False,
        "stores_queried": [],
        "stores_skipped": ["memory", "knowledge", "tools", "agents", "graphify"],
        "skip_reasons": {
            "memory": "Memory Runtime not enabled until Phase 14.2",
            "knowledge": "Knowledge Runtime not enabled until Phase 14.3",
            "tools": "Tool Runtime not enabled until Phase 14.5",
            "agents": "Autonomous agents not enabled until Phase 14.7",
            "graphify": "ADR-0007 deferred",
        },
        "budgets": {"memory": 0, "knowledge": 0, "tools": 0, "conversation": 1},
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
        "phase": "14.1",
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


def _refusal_message(classification: dict[str, Any]) -> str:
    return (
        f"I am {PRODUCT_NAME}. I must refuse this request in Stage 1 (Solo Runtime).\n\n"
        f"Classification: {classification['label']}.\n"
        f"Reason: {classification['rationale']}.\n\n"
        "Execute and Administrative actions require gated approval UX that is not enabled yet. "
        "Memory, Knowledge, and Tools runtimes are also disabled in Phase 14.1."
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
        "phase": "14.1",
        "ollama": ollama_ok,
        "council_mode": COUNCIL.get("mode", "conceptual"),
        "hermes_role": HERMES.get("role", "thin_execution_layer"),
    }


@app.get("/v1/models")
async def list_models() -> dict[str, Any]:
    return {"object": "list", "data": await ollama_tags()}


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

    system = {
        "role": "system",
        "content": _solo_system_prompt()
        + "\n\n[Stage-1 explainability context]\n"
        + json.dumps(
            {
                "classification": classification["label"],
                "stores_skipped": strategy["stores_skipped"],
                "council_mode": "solo_conceptual",
            },
            indent=2,
        ),
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
        "phase": "14.1",
        "profile": "solo",
        "message": "KORA Runtime Stage 1 — OpenAI-compatible conductor façade",
    }
