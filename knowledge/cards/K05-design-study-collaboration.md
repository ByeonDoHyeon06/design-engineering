# K05 — Investigate unfamiliar domains before codifying UI patterns

**Knowledge type:** METHODOLOGY  
**Source IDs:** V03  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC06

## When to retrieve
The task is novel and the designer does not understand what experts mean by “urgent”.

## Verified source findings and study scope
- **Evidence — V03 (author/institutional abstract):** Sedlmair, Meyer & Munzner propose a design study methodology based on reflections from 21 design studies and literature review. Their nine-stage framework includes learn, winnow, cast, discover, design, implement, deploy, reflect, write.
- **Selected primary-paper sections checked:** The authors state they reviewed 21 of their own design studies, and they identified three attempts they considered failures; this makes limitations/pitfalls part of the contribution.
- **Evidence type:** Methodological synthesis; the nine stages are not experimentally proven superior for every UI project.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Separate actual domain language from invented generic metrics; gather examples of real decisions and failure cases.
2. Test whose knowledge is missing (in experts’ heads, logs, workflows, documents).
3. Select an appropriate level of user involvement and prototype fidelity; do not mechanically run every framework phase for a small cosmetic fix.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/verified/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Record assumptions, representative data and real domain feedback; revise when domain tasks contradict the mockup.

## Provenance
- `V03` — Design Study Methodology: Reflections from the Trenches and the Stacks. https://doi.org/10.1109/TVCG.2012.213 (checked: 2026-11-14; author_abstract_verified)
