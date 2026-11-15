# K01 — Distinguish what visual attractiveness actually means

**Knowledge type:** RESEARCH  
**Source IDs:** A1, A2  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC01, VC02

## When to retrieve
A visually tidy UI may still lack identity; a visually bold page may still be incoherent.

## Verified source findings and study scope
- **Evidence — A1 (publisher abstract):** Lavie & Tractinsky developed a website aesthetics instrument through four studies. Classical and expressive aesthetics are differentiated perceptual dimensions; neither specifies a universal visual style.
- **Evidence — A2 (publisher abstract):** Moshagen & Thielsch report seven studies supporting four related but distinguishable perceived aesthetic facets: simplicity, diversity, color, craftsmanship.
- **Selected primary-paper sections checked (A2):** Study 6 randomly assigned 78 participants to color variants; only the Colorfulness facet differed significantly. Study 7 compared two broader aesthetic variants with 375 participants. This strengthens construct-validation interpretation, not a claim that any color choice universally improves design.
- **Scope:** These are *user-perceived website aesthetic constructs*, not proof that a particular color, motif, grid, or font yields better task outcomes.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Identify whether the actual concern is lack of clarity, insufficient expression, unconvincing color relations, or poor craft; do not lump these into “make it beautiful.”
2. Compare variants with both *simplicity/order* and *diversity/expressiveness* considered, together with color relationships and fine finishing.
3. If using a validated instrument, follow its actual administration and interpretation; a custom rubric is a heuristic, not the VisAWI instrument.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Check with representative people where feasible; compare visual judgment separately from comprehension, keyboard access and task success. Do not give numerical aesthetic “laws.”

## Provenance
- `A1` — Assessing dimensions of perceived visual aesthetics of web sites. https://doi.org/10.1016/j.ijhcs.2003.09.002 (checked: 2026-11-14; publisher_abstract_verified)
- `A2` — Facets of visual aesthetics. https://doi.org/10.1016/j.ijhcs.2010.05.006 (checked: 2026-11-14; publisher_abstract_verified)
