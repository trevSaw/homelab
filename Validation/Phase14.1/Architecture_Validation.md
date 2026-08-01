# Phase 14.1 — Architecture Validation

## Required Stage 1 path

```text
User → Open WebUI → KORA Runtime → Local Ollama → Response
```

| Check | Result |
| --- | --- |
| Open WebUI `OPENAI_API_BASE_URL=http://kora:8080/v1` | Pass |
| Open WebUI `ENABLE_OLLAMA_API=false` | Pass |
| Open WebUI `WEBUI_NAME=KORA` | Pass |
| KORA proxies chat to Ollama | Pass |
| Hermes not on primary chat path | Pass |
| KORA owns identity / refusal / explainability metadata | Pass |

## ADR alignment

| ADR | Expectation | Result |
| --- | --- | --- |
| ADR-0004 | Hermes substrate only; not identity | Pass (thin registration + docs) |
| ADR-0008 | Open WebUI is UI only | Pass (routes to KORA) |

## Separation maintained

| Boundary | Stage 1 posture |
| --- | --- |
| KORA vs Hermes | KORA orchestrates Solo path; Hermes thin/optional |
| Memory ≠ Knowledge | Both disabled / skipped |
| Council ≠ Agents | Solo conceptual Council only; no agents |
| Tools ≠ Decisions | Tools disabled; Execute refused |

## Diagram (implemented)

```text
┌────────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────┐
│   User     │────▶│ Open WebUI  │────▶│ KORA Runtime │────▶│ Ollama │
└────────────┘     │ (ADR-0008)  │     │ Solo Stage 1 │     └────────┘
                   └─────────────┘     └──────────────┘
                                              ▲
                   ┌─────────────┐            │ registration only
                   │   Hermes    │────────────┘ (not primary path)
                   │ thin layer  │
                   └─────────────┘
```
