# Knowledge architecture — task-selective, typed, traceable

This library contains **method and evidence cards, not web examples**. Cards are *design reasoning operations* which may apply across different kinds of products. The same card can support a poster, a dashboard, an editor or an admin interface, without dictating its appearance.

## Reading strategy for AI

1. Identify a **question/uncertainty**, not a design genre. Examples: “Is this grouping misleading?”, “Will a user understand this icon?”, “Have we fixated on the first composition?”
2. Search `catalog.json` or run `scripts/knowledge_lookup.py` for likely cards. Read at most the useful cards, not the whole directory.
3. Read **claim scope** before applying an operation. Locate scholarly sources in `sources.json` or practitioner provenance in `methods/designer-methods.json`.
4. Generate a design hypothesis, develop an inspectable implementation, validate it and record whether your prediction held.
5. If no card is appropriate, reason from first principles and the actual brief; missing coverage must not force a poor fit.

## Knowledge types

- `RESEARCH`: paper-backed observed effects or conceptual findings, *with study scope and transfers marked*.
- `STANDARD`: normative accessibility/HCD rules; verify applicability and version.
- `METHOD`: task-independent engineering/prototype process, not experimentally validated as a whole.
- `PRACTITIONER`: source-documented questions and craft operations, not stylistic templates or causal proofs.

`source_ids` connect each card to bibliographic metadata. Not every source has been read in full: `access_level` and other metadata distinguish abstract-based notes and older carried-forward records. Nothing in the library guarantees the generated interface is visually good: examine its actual rendered result.

## Contents intentionally excluded

The library intentionally excludes screenshots, live-site design galleries, borrowed templates and page-type style recipes. Bibliography entries are *evidence provenance*, not collections of design examples.

## Curated source-checking layer

Read `VERIFICATION-POLICY.md` before treating an academic claim as verified. New K-cards contain deep context-specific examples; source-level summaries and limitations live in `verified/claims.json`. Existing source aliases and unchecked bibliographic records are retained but not promoted.

## v4 typed governance layer

Read [v4 operations](v4/README.md). The existing catalog, sources, claims and concept JSON files remain **the authoritative records**; `v4/governance.json` is a sparse overlay for lifecycle states, manually reviewed aliases/equivalences, concept relations and optional public-safe observations. `scripts/knowledge_graph.py` materializes a deterministic Source → Claim → Concept → Method → Observation view, with dependency tracing and validation; it does not copy or replace research content.

**No automatic publication, retraction, or false academic confidence scoring.** Retired sources flag still-active dependent cards for review. Normal `knowledge_index.py` search skips archived or superseded methods, and `--include-inactive` restores them for historical audits. Verified-only retrieval rejects inactive-source claims unless historical audit is explicitly requested.
