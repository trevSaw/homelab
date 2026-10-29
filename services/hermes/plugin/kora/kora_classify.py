"""KORA classification + strategy selection (KORA-owned logic).

These functions are a faithful port of the KORA Runtime pipeline in
``AI/KORA/Runtime/app/main.py`` (``classify`` and ``select_strategy`` at Phase
14 checkpoint ``cf26e24``). They are pure functions (regex + dict building).

Why a port and not ``from app.main import classify``: importing ``app.main``
constructs the production KORA Runtime object graph (FastAPI app, Chroma vector
store, Honcho adapter, Tool Platform) at import time, which would contact
production backends. The plugin imports the REAL pure-KORA modules
(``app.event_bus``, ``app.memory_runtime``, ...) and uses this ported
classification/strategy logic for the intelligence pipeline.

Classification contract (unchanged): heuristic, deterministic, no retrieval
before classification. Labels: execute_forbidden, administrative_forbidden,
identity, preference, architecture, relationship, operational, general.

Infrastructure troubleshooting is classified as ``operational`` only when the
message shows a live diagnostic or action intent. Conceptual questions that
merely mention Docker, Traefik, or Compose remain ordinary conversation.
"""

from __future__ import annotations

import re
from typing import Any

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

FORBIDDEN_LABELS = {"execute_forbidden", "administrative_forbidden"}

_INFRA_TERMS_RE = re.compile(
    r"\b(?:docker|docker-compose|compose|containers?|traefik|reverse[- ]proxy|"
    r"prox(?:y|ies)|services?|stacks?|volumes?|networks?|images?|"
    r"registr(?:y|ies)|podman|kubernetes|k8s|portainer|daemon|compose\.ya?ml)\b",
    re.I,
)

_DIAGNOSTIC_INTENT_RE = re.compile(
    r"\b(?:troubleshoot(?:ing)?|diagnos(?:e|is|tic)|investigat(?:e|ion)|"
    r"debug(?:ging)?|why|failing|failed|failure|error(?:s)?|broken|down|"
    r"unhealthy|unavailable|crash(?:ing|ed|es)?|restarting|stopped|exited|"
    r"degraded|wrong|issue(?:s)?|problem(?:s)?|"
    r"not\s+(?:working|starting|running|responding|reachable|healthy)|"
    r"can(?:'|no)t|cannot|unable\s+to|"
    r"status|health(?:y)?|logs?|inspect(?:ion)?|check|list|running|start|"
    r"stop|restart|recreate|reload|deploy|configuration|config|route|routing|"
    r"502|503|504|401|403|404|timeout|latency|slow|performance|memory|cpu|"
    r"disk|port|mount|permissions?|connection\s+refused)\b",
    re.I,
)

_CONCEPTUAL_INTENT_RE = re.compile(
    r"^\s*(?:(?:can|could|would|will)\s+you\s+(?:please\s+)?)?"
    r"(?:what\s+(?:is|are|does|do)|"
    r"(?:explain|describe|define|compare|contrast|summari[sz]e|"
    r"overview\s+of|introduction\s+to|teach\s+me)\b|"
    r"how\s+(?:does|do|is|are)\b.+\b(?:work|works|function|functions|"
    r"behave|behaves|route|routes|operate|operates|differ)\b|"
    r"why\s+(?:does|do|would|should|can)\b|"
    r"difference\s+between|pros\s+and\s+cons|best\s+practice)\b",
    re.I,
)

_SPECIFIC_INFRA_TARGET_RE = re.compile(
    r"\b(?:my|our|this|these|those|the)\s+(?:\w+[\s-]+){0,3}"
    r"(?:containers?|services?|stacks?|prox(?:y|ies)|routers?|networks?|"
    r"volumes?|images?|daemons?|traefik|docker|compose)\b",
    re.I,
)

_LIVE_REQUEST_RE = re.compile(
    r"\b(?:status|health|logs?|inspect(?:ion)?|check|list|restart|recreate|"
    r"reload|deploy|502|503|504|401|403|404|timeout|connection\s+refused)\b",
    re.I,
)


def _is_infrastructure_diagnosis(text: str) -> bool:
    if not (_INFRA_TERMS_RE.search(text) and _DIAGNOSTIC_INTENT_RE.search(text)):
        return False
    if _CONCEPTUAL_INTENT_RE.search(text):
        if not (
            _SPECIFIC_INFRA_TARGET_RE.search(text)
            or _LIVE_REQUEST_RE.search(text)
        ):
            return False
    return True


def classify(text: str) -> dict[str, Any]:
    """Heuristic classifier — no store retrieval before this."""
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
    if _is_infrastructure_diagnosis(lower):
        return {
            "label": "operational",
            "confidence": "medium",
            "rationale": "Infrastructure diagnosis/troubleshooting request; read-only Tool access applies",
        }
    if re.search(r"\b(architecture|adr|standard|policy)\b", lower):
        return {
            "label": "architecture",
            "confidence": "medium",
            "rationale": "Architecture-like question; Knowledge retrieval applicable",
        }
    if re.search(
        r"\b(relationship|relate|related|relation|between|connect|connected|connection|link|linked|dependency|depends|graph)\b",
        lower,
    ):
        return {
            "label": "relationship",
            "confidence": "medium",
            "rationale": "Relationship-oriented question; graph + semantic Knowledge retrieval applicable",
        }
    if re.search(r"\b(models?|running|status|list|health|metrics?)\b", lower):
        return {
            "label": "operational",
            "confidence": "medium",
            "rationale": "Operational question; read-only Tool access may apply",
        }
    return {
        "label": "general",
        "confidence": "medium",
        "rationale": "General conversational request",
    }


def select_strategy(classification: dict[str, Any]) -> dict[str, Any]:
    """Context Intelligence stub — Knowledge retrieval for architecture and
    relationship queries; read-only Tools for operational queries. Memory
    remains off the chat path; no autonomous loops."""
    label = classification["label"]
    retrieval_labels = {"architecture", "relationship"}
    query_knowledge = label in retrieval_labels
    query_graph = label in retrieval_labels
    query_tools = label == "operational"
    query_memory = False
    stores_queried: list[str] = []
    stores_skipped = ["memory", "agents"]
    skip_reasons: dict[str, str] = {
        "memory": "Memory retrieval is internal and not on the chat path",
        "agents": "Autonomous agents not enabled until a later phase",
    }
    if query_knowledge:
        stores_queried.append("knowledge")
    else:
        stores_skipped.append("knowledge")
        skip_reasons["knowledge"] = "Knowledge retrieval not selected for this classification"
    if query_graph:
        stores_queried.append("graphify")
    else:
        stores_skipped.append("graphify")
        skip_reasons["graphify"] = "Graph retrieval not selected for this classification"
    if query_tools:
        stores_queried.append("tools")
    else:
        stores_skipped.append("tools")
        skip_reasons["tools"] = "Tool access not selected for this classification"
    return {
        "name": f"solo_{label}",
        "query_memory": query_memory,
        "query_knowledge": query_knowledge,
        "query_graph": query_graph,
        "query_tools": query_tools,
        "stores_queried": stores_queried,
        "stores_skipped": stores_skipped,
        "skip_reasons": skip_reasons,
        "budgets": {
            "memory": 0,
            "knowledge": 1 if query_knowledge else 0,
            "tools": 1 if query_tools else 0,
            "conversation": 1,
        },
        "confidence_posture": "conversation_only",
    }
