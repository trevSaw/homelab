# ADR Template

**Filename:** `ADR-####-short-description.md` (use leading zeros, e.g., `ADR-0001-Initial-Architecture-Decision.md`)

## Required Sections

| Section | Description |
|---|---|
| **Context** | Background, problem statement, and why this decision is needed. |
| **Decision** | The chosen solution, including any relevant diagrams or code snippets. |
| **Alternatives Considered** | Other options evaluated, with pros and cons. |
| **Consequences** | Positive and negative impacts of the decision, including operational, security, and maintenance considerations. |
| **Implementation Notes** | Practical steps to implement the decision, migration paths, and any required tooling. |

## When to Create an ADR

* When a new architectural direction is introduced that affects multiple services or the overall repository layout.
* When a significant trade‑off is made (performance vs. security, complexity vs. flexibility, etc.).
* When a long‑term policy or convention is established (e.g., naming, versioning, deployment strategy).

## Lifecycle

1. **Draft** – Initial authoring, stored in a `draft/` sub‑folder if needed. |
2. **Review** – Peer review, discussion, and approval. |
3. **Approved** – Merged into the main `decisions/` directory with the final filename. |
4. **Superseded** – If a later ADR replaces this one, add a note in the **Consequences** section and update the index. |