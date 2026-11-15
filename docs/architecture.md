# Architecture

Design Engineering is an **offline-first skill package**, not a website generator, cloud service or trained model. A single root `SKILL.md` drives the same workflow in Codex and Claude Code. Python tools supplement (but do not replace) an agent's judgment and actual browser inspection.

## Source-of-truth map

| Data | Canonical file | Responsibility |
| --- | --- | --- |
| Design operation cards | `knowledge/cards/*.md` | Task cues, decision moves, limitations |
| Card discovery metadata | `knowledge/catalog.json` | Stable card IDs, relevant queries, source references |
| Bilingual concepts | `knowledge/concepts.json` | Query expansions and concept-to-card links |
| Bibliography and access review | `knowledge/sources.json` | Source identity and inspected scope |
| Reviewed statements | `knowledge/claims.json` | Atomic verified-claim IDs, limitations and citation scope |
| Governance | `knowledge/governance.json` | Lifecycle overrides, aliases, reviewed equivalences, relations |
| Practitioner records | `methods/designer-methods.json` | Documented designer approaches (not style cloning) |

Only the files above are editable source data. The typed graph is a **deterministic, read-only projection** over these records, materialized through `scripts/knowledge_graph.py`. Its exported JSON and the SQLite search index under `.cache/` are disposable outputs; neither should be manually maintained.

## Knowledge graph

```text
Source ── supports ◄── Claim
   ▲                    ▲
   │ cites              │ supported_by
   │                    │
  Method ◄── retrieves ─ Concept
   ▲
   └── observed_method ─ Observation

Practitioner records are represented as separate Practice nodes.
```

Typed graph IDs use `source:N39`, `claim:VC14`, `concept:hangul_typography`, `method:K16` and `practice:rams`. Historical record IDs remain stable. A graph node's `active` lifecycle state means **available for current retrieval**; it says nothing about scientific strength.

Source withdrawal/supersession warnings identify still-active dependent methods and claims. Known aliases and equal-work relationships require human approval, and recorded equivalence does not silently delete either source.

## Retrieval architecture

```text
Question
  → bilingual cue analysis (query_understanding.py)
  → offline concept expansion
  → SQLite FTS5 + character n-gram matching (+ optional local embeddings)
  → applicability/noise gate
  → lifecycle and provenance filtering
  → ranked method cards and explicit evidence metadata
```

`knowledge_index.py` owns the SQLite index; catalog, claims, source records and governance contribute to its signature for rebuilds. The query-relative cutoff limits weak tails; `--relative-cutoff 0` is the broad-recall diagnostic mode. `--verified-only` requires an explicit claim ID linked to a reverified source, never a file-name prefix. The index does **not** prove whether a generated UI follows that claim.

## Validation architecture

- `validate_install.py` checks the whole package and exercises real indexing and search.
- `knowledge_health.py` checks IDs, references, possible duplicate URLs and missing dependencies; warnings are reviewed, not automatically fixed.
- `knowledge_graph.py validate` blocks invalid typed links and supersession cycles; `impact` reports transitive dependencies.
- `retrieval_evaluation.py` checks curated positives and out-of-domain/no-answer cases.
- `visual_critique.py` captures screenshots and requires explicit after-evidence for proposed fixes.
- `ux_scenarios.py` tests observable browser states; it is not human usability testing.

The scripts share a root directory convention. Avoid importing project files from the consumer application as if they were plugin resources.

## Distribution and boundaries

- Claude Code reads `.claude-plugin/plugin.json` and the root skill.
- Codex can use the full repository installed under `.agents/skills/design-engineering`.
- `agents/openai.yaml` provides Codex-facing metadata; it does not contain a second instruction source.
- Gemini and local embeddings are optional and disabled unless explicitly configured.
- No proprietary user screenshots, research PDFs, client documents or browser state are shipped in the public Knowledge library.

The project intentionally avoids mandatory network access, a hosted vector database and an aesthetic score. Research, implementation hypotheses and observed task success remain separate forms of evidence.

## Unified CLI and scoped personal Knowledge (v4.1)

`design_engineering/cli.py` is the public entry point, exposed by `pyproject.toml` (`de`/`design-engineering`) and the portable launcher `scripts/de.py`. Existing scripts stay modular behind it. Read-only core evidence retrieval and local preferences are **never combined into one evidence confidence grade**.

Personal data is held separately by `design_engineering/local_knowledge.py` at user, project or explicit session scope. Draft → reviewer approval → local JSON applies a scope-bound checksum guard, source-file fingerprint and exact-duplicate check. These are workflow safeguards, not authenticated multi-user database transactions. See [Personal Knowledge](personal-knowledge.md).
