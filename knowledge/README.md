# Knowledge

A curated library of **design-reasoning cards and source-scoped evidence**, not a UI-template collection.

| File | Purpose |
| --- | --- |
| `cards/` | Task-selective method and research cards |
| `catalog.json` | Card discovery metadata and links to sources |
| `concepts.json` | Bilingual design-topic cues and retrieval relationships |
| `sources.json` | Bibliographic identity, access level and review scope |
| `claims.json` | Explicitly linked, checked source claims and limits |
| `governance.json` | Reviewed lifecycle state, aliases and relation metadata |
| `VERIFICATION-POLICY.md` | Evidence verification contract |

Read relevant cards **after searching the user's actual uncertainty**. Look at source coverage, not only a high retrieval score. Official normative standards, draft notes, paper abstracts, interviews, design hypotheses and tested project outcomes must remain distinguishable.

For commands and review practices see [Knowledge management](../docs/knowledge-management.md). For the read-only relation model see [Architecture](../docs/architecture.md).

The `.cache/` SQLite index can always be recreated. It is **not** a new source of truth. New sources should be connected to an existing card or claim when appropriate; do not add near-duplicate cards simply because more papers become available.
