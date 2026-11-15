# K16 — Typography as a context-sensitive reading system

**Knowledge type:** STANDARD + PRACTITIONER INTERPRETATION  
**Source IDs:** N39, S1  
**Verification level:** W3C editorial Group Note Draft + official WCAG 2.2 normative text; not an empirical font-ranking study.  
**Verified claim IDs:** none (new sources retain explicit unreviewed-claim status)

## When to retrieve
A Korean headline breaks awkwardly, a font pairing makes numbers stand out, a fixed-height card clips text, or the same typography scale is applied blindly to Korean and Latin.

## Source-grounded findings
- **N39:** Korean typesetting encompasses Hangul/Latin mixed setting, character/word-based line breaks, punctuation restrictions, character spacing and line height. The March 2026 text is a W3C **Group Note Draft**, not endorsed consensus or a universal CSS recipe.
- **S1:** WCAG 2.2 SC 1.4.12 evaluates whether user spacing overrides cause content/function loss; it does **not** require authors to set those spacing values as their default.

## Design operations (hypotheses, not experimentally proven constants)
1. Name the reading job: glance, scan, extended reading, comparison, numeric precision, or UI action.
2. Select candidates based on supported Hangul/Latin glyph coverage, licensing, weights, punctuation and numeral metrics; never choose by brand impression alone.
3. Test real Korean mixed-script strings, punctuation, 2–3-line headings and long labels. Compare line breaks and visible emphasis at actual widths.
4. Tune font size, line height, tracking and measure **together**; avoid universally prescribed pixel values.
5. Inspect desktop, narrow mobile, zoom and spacing override. Record any clipping, forced truncation or ambiguous hierarchy.
6. When font substitution changes line breaks, revise surrounding layout, not just letter spacing.

## Countercases
- The W3C Korean layout draft describes writing-system requirements, not evidence that one particular font or layout increases conversion.
- Browser support for `word-break`, `line-break`, `text-wrap`, or locale-specific settings differs. Verify the actual target browsers.
- Do not attribute practitioner judgments or aesthetic preference to WCAG requirements.

## Live validation
Capture Korean/English headings, body paragraphs, numeric tables and buttons at 1440/390/320 widths. Apply text spacing overrides; inspect truncation and anchor/focus behavior. Report NOT TESTED when browser rendering is unavailable.

## Provenance
- **N39** — W3C, *Requirements for Hangul Text Layout and Typography*, Group Note Draft (21 March 2026): https://www.w3.org/TR/klreq/
- **S1** — W3C, *WCAG 2.2*, SC 1.4.12: https://www.w3.org/TR/WCAG22/#text-spacing
