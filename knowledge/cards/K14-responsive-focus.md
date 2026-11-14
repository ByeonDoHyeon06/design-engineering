# K14 — Test cross-viewport continuity instead of relying on breakpoint recipes

**Knowledge type:** STANDARD  
**Source IDs:** S1  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC16, VC17, VC14

## When to retrieve
The header wraps into two lines and anchor navigation hides the target.

## Verified source findings and study scope
- **Normative source — S1:** WCAG 2.2 Focus Not Obscured (Minimum) applies to focused components, not to every visually cropped section heading. Text Spacing tests layout resilience to user override. Target Size has exceptions.
- **Design hypothesis (not a normative WCAG rule):** Distinct viewport layouts should preserve comprehension, action hierarchy and visible anchor destinations whenever practical.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Capture desktop, common mobile, and narrow mobile with real content and text size overrides.
2. Measure actual sticky header geometry after wrapping, not just CSS values guessed at design time.
3. Navigate by anchors and Tab, test keyboard focus visibility, inspect meaningful text crop and horizontal scrolling.
4. Fix concrete collisions, and report which tests ran; do not mark an anchor heading hidden as automatically failing 2.4.11 unless focused UI visibility meets its failure condition.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/verified/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Run in a real browser where possible; otherwise say NOT TESTED. Prefer independent keyboard and screen-reader testing for consequential flows.

## Provenance
- `S1` — Web Content Accessibility Guidelines (WCAG) 2.2. https://www.w3.org/TR/WCAG22/ (checked: 2026-11-14; official_normative_standard_verified)
