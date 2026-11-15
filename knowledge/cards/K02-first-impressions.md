# K02 — Separate very-early visual impressions from durable task value

**Knowledge type:** RESEARCH  
**Source IDs:** E4  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC03

## When to retrieve
An unusual interface may be judged differently at first glance than after sustained use.

## Verified source findings and study scope
- **Evidence — E4 (institutional/publisher abstract):** Tuch and colleagues examined rapid aesthetics ratings of website screenshots under manipulated visual complexity and prototypicality. Perceived visual complexity mattered at very short exposures, and low-complexity/high-prototypicality screens received favorable ratings in their experimental setup.
- **What was measured:** Ratings of briefly shown screenshots, not production conversions, learnability, or admin task error rates.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Clarify whether the user is optimizing immediate legibility, brand distinction, or long-session efficiency.
2. Test the hierarchy in an initial screenshot without assuming that prototypicality always outweighs novelty.
3. Evaluate the same artifact during real tasks; a first-impression finding cannot replace longer-use testing.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Use blinded first-impression review for perception claims and task observation for usability claims. Avoid prescribing low complexity indiscriminately.

## Provenance
- `E4` — The role of visual complexity and prototypicality regarding first impression of websites. https://doi.org/10.1016/j.ijhcs.2012.06.003 (checked: 2026-11-14; institutional_abstract_verified)
