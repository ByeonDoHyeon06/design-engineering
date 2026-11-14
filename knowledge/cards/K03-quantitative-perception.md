# K03 — Choose quantitative encodings based on decoding tasks

**Knowledge type:** RESEARCH  
**Source IDs:** V01  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC04

## When to retrieve
A dashboard needs accurate comparison of several quantities.

## Verified source findings and study scope
- **Evidence — V01 (publisher abstract):** Cleveland & McGill studied elementary visual decoding tasks and experimentally compared the accuracy of extracting quantitative values from graphs. The paper argues that choice of graphical encoding matters to precision.
- **Scope:** Their experiments concern quantitative perception, not aesthetic preference, memorability, or every possible task/culture.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. First identify whether the intended task is exact comparison, ranking, proportion, trend, distribution, or anomaly detection.
2. Match visual channel to the precision needed; use scales and aligned references when precise comparisons matter.
3. Explicitly examine whether decorative shape or perspective distorts a quantitative comparison; use direct labels/tables for exact values when needed.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/verified/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Give users comparative tasks and inspect accuracy/error rates. Do not ban chart types universally; decide from actual inference goals.

## Provenance
- `V01` — Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods. https://doi.org/10.1080/01621459.1984.10478080 (checked: 2026-11-14; publisher_abstract_verified)
