# K13 — Review systems at domain, perception and implementation levels

**Knowledge type:** METHOD  
**Source IDs:** V02, V03, V01  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC04, VC05, VC06

## When to retrieve
A visually polished analytics application fails when used with real data.

## Verified source findings and study scope
- **Source synthesis:** Munzner’s four-level nested model identifies where errors may arise. Sedlmair et al. explain field-oriented design study methodology. Cleveland & McGill supply empirical evidence for quantitative decoding accuracy.
- **Important distinction:** These are complementary but distinct contributions, not one experimentally verified end-to-end UI recipe.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Check domain vocabulary and exact decision/task first; validate with actual records.
2. Check the abstraction of tasks and data types, then inspect visual encodings against perceptual precision demands.
3. Finally test algorithms/performance and interaction states using realistic volumes and failure data.
4. Keep artistic composition, perceived aesthetics and numerical validity as separate critique dimensions.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Construct test cases for real questions, edge cases, missing data, changing values and analyst interpretation.

## Provenance
- `V02` — A Nested Model for Visualization Design and Validation. https://doi.org/10.1109/TVCG.2009.111 (checked: 2026-11-14; author_abstract_verified)
- `V03` — Design Study Methodology: Reflections from the Trenches and the Stacks. https://doi.org/10.1109/TVCG.2012.213 (checked: 2026-11-14; author_abstract_verified)
- `V01` — Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods. https://doi.org/10.1080/01621459.1984.10478080 (checked: 2026-11-14; publisher_abstract_verified)
