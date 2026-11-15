# K10 — Choose outcome measures that actually represent intended usability

**Knowledge type:** REVIEW  
**Source IDs:** R6, S2  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC13, VC18

## When to retrieve
Two designs have nearly equal subjective scores; the team claims objective usability superiority.

## Verified source findings and study scope
- **Evidence — R6 (publisher abstract):** Hornbæk reviews usability measures in 180 HCI papers and highlights recurring measurement validity problems.
- **Standards context — S2 (ISO official scope page):** ISO 9241-210:2019 addresses human-centered design processes, not an automatic certification of a generated UI. The full proprietary standard was not inspected here.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. State the design claim first: ease of learning, accuracy, speed, satisfaction, discoverability or error recovery.
2. Choose a matching method: representative task completion, time distribution, observed errors, interview/scale, or multiple observers.
3. Do not average unrelated metrics into one faux-scientific score without declared weights and uncertainty; separate subjective visuals from behavioral outcomes.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Record recruitment, tasks, number of trials, device and environment; mark simulations and AI reviews as such.

## Provenance
- `R6` — Current Practice in Measuring Usability: Challenges to Usability Studies and Research. https://doi.org/10.1016/j.ijhcs.2005.06.002 (checked: 2026-11-14; publisher_abstract_verified)
- `S2` — ISO 9241-210:2019. https://www.iso.org/standard/77520.html (checked: 2026-11-14; official_standard_scope_verified)
