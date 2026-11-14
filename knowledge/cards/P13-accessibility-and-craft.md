# P13 — Treat clarity, accessibility and implementation craft as distinct requirements

**Type:** STANDARD  — **Source IDs:** S1, S2, A2

## Use when
A visual concept is ready for implementation or release.

## Evidence and scope
WCAG is normative, VisAWI craftsmanship is a perceived aesthetic facet; they are not interchangeable. Refer to `knowledge/sources.json` for original source URLs and access limits.

## Transferable reasoning moves
1. Use semantic elements, focus visibility, keyboard access, usable labels, field error explanations and programmatic status.
2. Verify contrast based on text/UI role and the actual background; allow normative exceptions where applicable.
3. Inspect 1440/390/320 and relevant intermediate widths for overflow, cropping, fixed-header anchor overlap and font rendering.
4. Keep visual craft checks separate from the static semantics checklist.

## Do not infer
- High code-level conformance does not prove a successful user experience.
- Screenshot is not keyboard/assistive-technology evidence; static audit cannot certify WCAG conformance.

## Verify the output
Record PASS/FAIL/REVIEW/NOT TESTED per claim with screenshot/interaction evidence.
