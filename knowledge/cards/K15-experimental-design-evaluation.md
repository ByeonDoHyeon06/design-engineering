# K15 — Avoid overstating small design A/B experiments

**Knowledge type:** METHOD  
**Source IDs:** R6, A1, A2, CR3  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC01, VC02, VC12, VC13

## When to retrieve
A six-page model-generated A/B test yields a tiny score gap and a claim of scientific superiority.

## Verified source findings and study scope
- **Evidence base:** A1/A2 offer constructs for *perceived aesthetics*, Hornbæk warns about usability measurement validity, and Dow’s experiment illustrates an explicit controlled human-design context.
- **Our protocol below is methodological advice**, not a validated test instrument from these papers.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Predefine outcome and evaluation criteria; blind reviewers to conditions.
2. Use actual rendered artifacts, not only CSS source inspection; assess interactions separately.
3. Treat multiple outputs from one model session as potentially dependent. Report averages and uncertainty without claiming causal generality from n=3.
4. If using custom expert scores, label them as exploratory subjective judgments; do not call them VisAWI results.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/verified/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Repeat under multiple tasks and truly independent runs; maintain a preregistered change log for scoring adjustments.

## Provenance
- `R6` — Current Practice in Measuring Usability: Challenges to Usability Studies and Research. https://doi.org/10.1016/j.ijhcs.2005.06.002 (checked: 2026-11-14; publisher_abstract_verified)
- `A1` — Assessing dimensions of perceived visual aesthetics of web sites. https://doi.org/10.1016/j.ijhcs.2003.09.002 (checked: 2026-11-14; publisher_abstract_verified)
- `A2` — Facets of visual aesthetics. https://doi.org/10.1016/j.ijhcs.2010.05.006 (checked: 2026-11-14; publisher_abstract_verified)
- `CR3` — Parallel prototyping leads to better design results, more divergence, and increased self-efficacy. https://doi.org/10.1145/1879831.1879836 (checked: 2026-11-14; publisher_abstract_verified)
