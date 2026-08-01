# Phase 14.1 — Known Limitations

1. **No Memory Runtime** — preference language is classified but Memory is skipped.
2. **No Knowledge / RAG** — architecture questions do not retrieve repo docs yet.
3. **No Tools / MCP** — operational live-state queries are not tool-backed.
4. **No multi-member Council** — Solo conceptual mode only.
5. **No agent orchestration** — Hermes not driving Solo chat.
6. **Classifier is keyword-based** — may miss novel Execute/Admin phrasings.
7. **Explainability** is returned in the OpenAI payload `kora` object; Open WebUI may not render it as a dedicated UX panel yet.
8. **Ollama compose project** may still be managed from `/hive/ollama` until residual cutover.
9. **Hermes live working_dir** may still be `/mnt/monarch/appdata/hermes` until residual cutover.
10. **Cold model loads** can make first KORA→Ollama completions slow.
