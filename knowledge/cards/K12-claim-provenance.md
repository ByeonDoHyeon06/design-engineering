# K12 — Separate source findings, practitioner guidance and AI extrapolation

**Knowledge type:** METHOD  
**Source IDs:** V02, R6, S1  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC05, VC13, VC14

## When to retrieve
The AI says “research proves” a CSS ratio without identifying a suitable study.

## Verified source findings and study scope
- **Evidence — V02:** A framework’s validity threat must be matched to the level being evaluated.
- **Evidence — R6:** Usability measures frequently suffer construct-validity problems.
- **Standard — S1:** Normative rules differ from empirical findings. These sources motivate *our proposed provenance protocol*, but do not themselves validate this exact protocol.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Label statement as **SOURCE_FINDING**, **FRAMEWORK**, **STANDARD**, **PRACTITIONER**, or **DESIGN_HYPOTHESIS**.
2. Preserve a source ID and verified access level. Source metadata/abstract verification is not full-text replication.
3. For every transferred prescription, write “why it may apply here”, “when it would not”, and “what would falsify it”.
4. Prefer explicit uncertainty to fake consensus; do not count bibliographic aliases as independent studies.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/verified/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Ask whether a claim is linked to actual source text, whether the source studied the same task, and whether the suggested test would challenge the claim.

## Provenance
- `V02` — A Nested Model for Visualization Design and Validation. https://doi.org/10.1109/TVCG.2009.111 (checked: 2026-11-14; author_abstract_verified)
- `R6` — Current Practice in Measuring Usability: Challenges to Usability Studies and Research. https://doi.org/10.1016/j.ijhcs.2005.06.002 (checked: 2026-11-14; publisher_abstract_verified)
- `S1` — Web Content Accessibility Guidelines (WCAG) 2.2. https://www.w3.org/TR/WCAG22/ (checked: 2026-11-14; official_normative_standard_verified)
