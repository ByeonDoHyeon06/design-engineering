# Proposal: Design Engineering 4.0 — Knowledge as a governed system

**Status:** RFC / not implemented. **Scope:** architecture, schema, migration and acceptance criteria. **Purpose:** stop unchecked accumulation of cards/keywords as the catalog grows. Maintain one platform-neutral root `SKILL.md`.

## 1. What is wrong with the current shape?

v3.9 ships 41 cards, 55 source records, 18 curated claim records, and 22 bilingual query concepts. It already supports source-linked claims and an offline FTS index. However:

- `catalog.json` mixes identity, search hints, presentation, verification summaries and references.
- `concepts.json` acts as an implicit hand-maintained topic taxonomy; cue substring matching can generate overbroad associations.
- `sources.json` may contain the same work under different IDs. It also contains intentionally legacy or unreferenced works.
- Claim, source, design interpretation and implementation outcome are distinct kinds of knowledge but the lifecycle is only partially explicit.
- There is no stable workflow for rejecting, merging, superseding or rechecking records; the catalog can grow faster than its evidence quality.
- `K` is an identifier, **not** a scientific verification level. Verified status is an explicit source/claim link.

### v4.0 goals, with non-goals

1. Retrieve useful decisions with **fewer, better maintained** records, not the greatest card count.
2. Trace a design hypothesis back to the exact source passage, claim scope and reviewer, and forward to real tests and revisions.
3. Detect aliases, duplicates, contradictions, orphan links and stale sources before merge.
4. Support bilingual queries without copying every synonym into every card.
5. Keep installation simple: plain JSON/Markdown and SQLite; no mandatory vector DB, server, paid APIs or proprietary ontology runtime.

Not goals: fine-tuning a model, automatically verifying an academic paper, assigning universal research truth scores, or converting the repository into a fully fledged RDF knowledge graph. Existing cards must remain readable.

## 2. Typed records and identity

The proposed logical model separates six entities:

```text
Source (source-id, DOI/canonical URL, edition, license, access & review)
  │ supports / contradicts
  ▼
Claim (claim-id, exact supported statement, scope, limitation, evidence status)
  │ informs (not proves)
  ▼
Concept (concept-id, labels ko/en, broader / related)
  │ operationalized by
  ▼
Design Method (method-id, conditions, procedure, risks, countercases)
  │ evaluated by
  ▼
Observation (observation-id, project, viewport, outcome, artifact, date)
  │ informs revision
  └─────────────► Method / Claim / Concept review
```

A `Card` remains an **agent-facing view**, assembled from these typed records. One source can back several claims, and one claim can inform several methods; new studies do not imply new cards. Cards must be concise and task-oriented. Use stable opaque IDs; a record's filename/title may change without changing identity.

Separate **publication verification**, **claim fidelity**, **transfer applicability** and **implementation outcome**. They must never be collapsed into a single confidence number.

## 3. Draft schema contract (illustrative, not yet a migration)

```json
{
  "id": "method:hangul-line-breaking",
  "schema_version": 2,
  "status": "active",
  "supersedes": [],
  "concept_ids": ["concept:typography", "concept:hangul-layout"],
  "claim_refs": ["claim:hangul-linebreak-scope"],
  "applies_when": ["long Korean headlines", "mixed-script wrapping"],
  "do_not_apply_when": ["font performance is not evaluated"],
  "updated_at": "2026-11-15",
  "review_due": null,
  "owner": "maintainers"
}
```

IDs above are examples, **not** current v3.9 registry IDs. Keep old IDs as aliases during migration. No automatic deletion or renumbering.

Use relationship names inspired by W3C SKOS (`broader`, `related`) and provenance concepts inspired by W3C PROV-O; **only import what is useful**, do not claim full semantic-web standard conformance. Follow FAIR ideas for findability, traceable metadata and reuse.

References:
- W3C SKOS Reference: https://www.w3.org/TR/skos-reference/
- W3C PROV-O: https://www.w3.org/TR/prov-o/
- FAIR guiding principles: https://doi.org/10.1038/sdata.2016.18

## 4. Bounded ingestion / maintenance lifecycle

`proposed → identity-checked → source-reviewed → claim-reviewed → published → due-for-review → (revised | superseded | archived)`

- **Proposed:** new research candidate and why existing records do not cover it. No automatic publication.
- **Identity-checked:** normalized DOI/URL, title/author/year/edition and license, duplicate lookup.
- **Source-reviewed:** record inspected sections, access limits, review date and source identity. Abstract-only stays abstract-only.
- **Claim-reviewed:** atomize verifiable claims, scope, evidence type and `do_not_infer`; link every claim to original source, never fabricate.
- **Published:** update typed registries and **a generated search index** after integrity tests.
- **Review due:** source withdrawn, new edition, broken link, contradiction, or review policy trigger (risk-based; not every source has the same expiration).
- **Archived:** searchable by explicit include option for audit/history, but not ranked as current recommendations.
- **Superseded:** maintain stable redirects/aliases, retain original provenance.

Rejection reasons and non-promoted candidate records should be auditable. External models can suggest; only review and local validation can promote.

## 5. Taxonomy, retrieval, scale

- Define a small controlled bilingual concept vocabulary, including synonyms (alt labels) and explicit `broader`/`related` relations. Prevent cycles in `broader` edges.
- Distinguish *lexical match*, *concept match*, optional *embedding similarity*, *evidence status*, and *task applicability*. Search rank is not truth or confidence.
- Retrieve candidate IDs first, then expand references to only a few relevant **method cards**, with source scopes attached. Avoid loading the entire catalog into an LLM context.
- Allow `no useful evidence found` with diagnostic reasons. Preserve a broad-recall/debug mode.
- Deduplicate by normalized DOI and version-qualified source identity; **do not automatically merge** distinct editions, translations or legitimately independent studies.
- Build cached inverted concept → claim → method indexes; benchmark cold/warm build, query latency and memory with ~100, ~1k and ~10k synthetic records before adding infrastructure.
- Use local SQLite FTS and optional local embeddings as long as measurements justify them; do not introduce a vector server until concrete recall/latency requirements justify it.
- Collect blinded, held-out bilingual queries with relevant **and explicitly irrelevant** cards; report precision@k, recall@k, MRR, no-result false positives, and regressions by domain.

## 6. Governance and CI gates

**Errors (block PR):** broken references, duplicate IDs, missing files, orphan claim references, unsafe paths, schema mismatch, contradictory supersession cycle.

**Warnings (human review):** duplicate DOI/URL, stale source, unreferenced source, overbroad synonym, dense or disconnected concepts, repetitive methods, weak retrieval.

**Human checkpoints:** review provenance for public-facing claims; inspect Korean copy and actual rendered typography; inspect source scope before labelling findings verified. No automated "aesthetic 90/100" claims.

V3.9 pilot: `python scripts/knowledge_health.py --json` implements a **read-only integrity audit and review warnings**. It does NOT migrate records, review original research, merge aliases, or replace the existing evidence audit.

## 7. v4.0 staged migration

| Phase | Deliverable | Gate |
|---|---|---|
| 0 — Baseline | inventory, duplicates, orphan sources, benchmarks, installed-plugin smoke | repeatable report |
| 1 — Schema | stable type-specific IDs and JSON schema with legacy aliases | all 41 existing cards readable |
| 2 — Provenance | source → atomic claim → method links and lifecycle status | zero broken references, no claim promotions by inference |
| 3 — Search | typed index, taxonomy and source-aware ranking | held-out bilingual query gains, no regressions in old suite |
| 4 — Evaluation | observation/revision records, real UI tests, diagnostics | traceable before/after artifacts |
| 5 — Distribution | generated slim readable card views, same single root skill for Codex/Claude | full-install smoke success on both |

Do **not** start Phase 1 by manually rewriting all 41 cards. Write read-only export/validation tools first, then dual-read adapters, then gradually convert reviewed cards. Use snapshot tests and one-way reversible transformations. Preserve v3.9 data until parity is proven.

## 8. Approval tests for v4.0

- Adding a duplicate source is flagged with IDs and its canonical key before review.
- A source's retraction/supersession can list all dependent claims, methods and affected project observations.
- Mixed Korean/English queries find a known relevant method and reject unrelated near-matches on held-out data.
- Claim verification cannot be inferred from card ID, source title, or AI output.
- Offline full repository installs in both Claude Code and Codex with no missing support files.
- A generated production design can cite actual source scope *without* leaking research metadata into end-user copy.

**Decision request:** approve typed schema + staged migration in a v4.0 RFC before creating more than a small number of new cards.
