# K06 — Support exploration without forcing a canonical dashboard layout

**Knowledge type:** FRAMEWORK  
**Source IDs:** V04  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC07

## When to retrieve
People must move from high-level state to explanations and evidence.

## Verified source findings and study scope
- **Evidence — V04 (university repository abstract):** Shneiderman describes overview-first/zoom-and-filter/details-on-demand as a starting point and develops a taxonomy of seven information data types and seven interaction tasks.
- **Scope:** A conceptual taxonomy for information visualization, not an instruction that every screen must start with a KPI card grid.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Identify whether users primarily need compare, locate, relate, explain, filter, recover history or export.
2. Offer an overview only if it helps the task; for known exact lookups, direct navigation may be better.
3. Maintain context across filter and detail transitions and make active filters/recovery legible.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/verified/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Test whether users can recover from filtering, find the underlying record, and understand what subset is being shown.

## Provenance
- `V04` — The Eyes Have It: A Task by Data Type Taxonomy for Information Visualizations. https://doi.org/10.1109/VL.1996.545307 (checked: 2026-11-14; university_abstract_verified)
