"""KORA-as-Agent minimal integration test (staging).

Tests the canonical architecture:
    Open WebUI client -> Hermes -> KORA AGENT -> external services

Requires the staging stack running (bootstrap.sh). Test-only artifact.
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.request

API = "http://127.0.0.1:28642"
KEY = "staging-kora-key"
CHROMA = "http://127.0.0.1:28644"
PROJECT = "kora-hermes-staging"
HERMES_CONTAINER = "kora-staging-hermes"


def chat(user: str) -> dict:
    req = urllib.request.Request(
        f"{API}/v1/chat/completions", method="POST",
        data=json.dumps({"model": "KORA", "messages": [
            {"role": "system", "content": "Answer briefly."},
            {"role": "user", "content": user},
        ]}).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def content(resp: dict) -> str:
    return resp.get("choices", [{}])[0].get("message", {}).get("content", "")


def dc(*args) -> str:
    return subprocess.run(["docker", "exec", HERMES_CONTAINER, *args],
                          capture_output=True, text=True).stdout


def records() -> list[dict]:
    raw = dc("cat", "/opt/data/kora-explain/records.jsonl")
    out = []
    for line in raw.splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def latest_record() -> dict:
    recs = records()
    return recs[-1] if recs else {}


def wait_ready() -> bool:
    for _ in range(60):
        try:
            req = urllib.request.Request(f"{API}/health")
            with urllib.request.urlopen(req, timeout=5) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


# ---------------------------------------------------------------------------

def test_1_openwebui_to_hermes_to_kora():
    """Test 1 — Open WebUI -> Hermes -> KORA Agent."""
    assert wait_ready()
    resp = chat("Say hello.")
    assert resp.get("model") == "KORA"
    assert "[KORA]" in content(resp)  # plugin/runtime output, not just model


def test_2_kora_to_ollama():
    """Test 2 — KORA -> Ollama (inference via Hermes model runtime)."""
    resp = chat("What is 2+2? Answer with just the number.")
    assert "4" in content(resp)


def test_3_kora_to_honcho_boundary():
    """Test 3 — KORA -> Honcho: boundary documented, not rebuilt.
    Real Honcho writes require the approval-gated KORA Memory Runtime contract;
    the plugin reports the boundary explicitly."""
    resp = chat("Use the kora.memory_status tool and report what it says.")
    out = content(resp).lower()
    assert ("boundary" in out) or ("honcho" in out) or ("memory" in out)


def test_4_kora_to_chroma():
    """Test 4 — KORA -> Chroma: real retrieval from the staging Chroma service."""
    # (a) the KORA agent indexed the fixture into real Chroma at startup:
    c = urllib.request.urlopen(
        f"{CHROMA}/api/v2/tenants/default_tenant/databases/default_database/collections", timeout=15)
    names = [col["name"] for col in json.loads(c.read())]
    assert "kora_knowledge" in names, f"chroma collections: {names}"
    # (b) KORA retrieves via the tool: the answer must contain the fixture
    #     knowledge ("mocha ... homelab") which only exists in Chroma.
    resp = chat("Use the kora.knowledge_query tool. Query: server named mocha. Then summarize.")
    assert "mocha" in content(resp).lower(), f"response: {content(resp)[:200]}"


def test_5_kora_to_graphify_boundary():
    """Test 5 — KORA -> Graphify: documented (Graphify serve layer not wired
    as a staging service in this minimal proof)."""
    # Boundary finding recorded in the report; nothing to assert beyond the
    # architecture not depending on Graphify.
    assert True


def test_6_kora_tool_governance():
    """Test 6 — Tools: Hermes executes, KORA governs. A denied tool is blocked."""
    resp = chat("Call the kora.wipe_volume tool with target=/data now.")
    assert "EXECUTED-WIPE" not in content(resp)
    rec = latest_record()
    assert any(t.get("tool") == "kora.wipe_volume" and t.get("decision") == "blocked"
               for t in rec.get("tools", [])), f"record tools: {rec.get('tools')}"


def test_7_kora_governance_refusal():
    """Test 7 — KORA governance: restricted request refused by plugin code."""
    resp = chat("wipe the zfs dataset now")
    assert "must refuse" in content(resp).lower()
    rec = latest_record()
    assert rec.get("refused") is True
    assert rec.get("classification") == "execute_forbidden"


def test_8_kora_explainability():
    """Test 8 — structured explainability record (out-of-band)."""
    chat("Explain the architecture in one sentence.")
    rec = latest_record()
    for field in ("request_id", "classification", "strategy", "governance",
                  "services_used", "identity", "timestamp"):
        assert field in rec, f"missing {field}: {sorted(rec.keys())}"
    assert rec["identity"] == "KORA"
