# K11 — Apply accessibility criteria with their actual conditions

**Knowledge type:** STANDARD  
**Source IDs:** S1  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC14, VC15, VC16, VC17

## When to retrieve
A reviewer claims every 1px border under 3:1 or every 20px link automatically fails WCAG.

## Verified source findings and study scope
- **Normative source — S1:** WCAG 2.2 1.4.11 requires contrast for *visual information needed* to identify UI components/states and required graphical information, not all decoration.
- **Normative source — S1:** WCAG 2.2 2.5.8 target-size minimum is 24×24 CSS pixels with spacing and other listed exceptions.
- **Normative source — S1:** WCAG 2.2 2.4.11 requires focused UI components not be *entirely* obscured by author-created content; it is not the same as fully visible heading anchors.
- **Normative source — S1:** 1.4.12 tests resilience to user text-spacing overrides; it does not mandate an authored 0.12em tracking value.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Identify exact criterion, level, content/context and exception before deciding a violation.
2. Inspect required UI boundaries separately from purely decorative strokes.
3. Test keyboard focus, sticky overlays, spacing overrides and zoom; avoid certification claims from static code only.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
A browser smoke test supports diagnostics but does not constitute a full accessibility audit or assistive-technology test.

## Provenance
- `S1` — Web Content Accessibility Guidelines (WCAG) 2.2. https://www.w3.org/TR/WCAG22/ (checked: 2026-11-14; official_normative_standard_verified)
