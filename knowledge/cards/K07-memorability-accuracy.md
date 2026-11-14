# K07 — Do not confuse memorable graphics with effective analytic communication

**Knowledge type:** RESEARCH  
**Source IDs:** V05, V01  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC08, VC04

## When to retrieve
An unusual colorful visualization is remembered but its numbers are misread.

## Verified source findings and study scope
- **Evidence — V05 (IEEE abstract):** Borkin and colleagues gathered memorability judgments for a broad collection of single-panel visualizations and examined features related to recall.
- **Evidence — V01 (publisher abstract):** Cleveland & McGill empirically evaluated quantitative decoding accuracy, a *different outcome*.
- **Synthesis (our interpretation):** A visualization can be memorable without being precise. This cross-paper distinction is a design hypothesis, not a direct head-to-head experiment in these two papers.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Decide whether the primary task is recall, exact numerical comparison, explanation, or a mix.
2. Avoid adding features just to boost apparent novelty; preserve accurate scales, ordering and labels.
3. Test each target separately: delayed identification for memory, questions about values for accuracy, explanation questions for comprehension.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/verified/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Do not infer improved learning or better decisions from memorability scores alone.

## Provenance
- `V05` — What Makes a Visualization Memorable?. https://doi.org/10.1109/TVCG.2013.234 (checked: 2026-11-14; publisher_abstract_verified)
- `V01` — Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods. https://doi.org/10.1080/01621459.1984.10478080 (checked: 2026-11-14; publisher_abstract_verified)
