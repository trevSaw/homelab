# Secret Exposure Report

**Search pattern:** `(password=|apikey=|token=|secret=|BEGIN PRIVATE KEY)`

**Locations examined:** all markdown files under the repository.

**Findings**

| File | Line excerpt | Classification | Severity |
|------|--------------|----------------|----------|
| homelab/audit/ComposeV1.md | `secret="$${SEARXNG_SECRET:-}"` (example generation) | Placeholder / example code | Low |
| homelab/audit/ComposeV1.md | `secret="$$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"` | Placeholder (auto‑generated token) | Low |
| homelab/audit/ComposeV1.md | `homepage.widget.password=${TRAEFIK_PASS}` | Reference to an environment variable (no actual value) | Low |
| homelab/audit/ComposeV1.md | `BEGIN PRIVATE KEY` (within comments) | Placeholder comment | Low |
| homelab/audit/ComposeV1.md | `secret="$${SEARXNG_SECRET:-}"` (duplicate line) | Placeholder | Low |

No real credential values were discovered. All matches are **documentation placeholders** or example snippets. No actionable security incidents were recorded.

**Recommendations**

- Keep placeholder patterns clearly marked as examples.
- Ensure that any future real secrets are stored outside of source control (e.g., in a secrets manager) and never committed. |