# P12 — Design understandable choices and physically operable targets

**Type:** RESEARCH  — **Source IDs:** E1, E2, S1

## Use when
Users must choose among alternatives or operate small/close controls.

## Evidence and scope
Original experiments concern response selection and motor performance; real UI tasks add context. Refer to `knowledge/sources.json` for original source URLs and access limits.

## Transferable reasoning moves
1. Clarify choice labels and organize mutually related options.
2. Assess target size, spacing, reachable position, keyboard focus and consequences of mis-taps.
3. Do not reduce a complex decision to fewer buttons if doing so hides information.
4. Apply the relevant platform/WCAG criterion rather than inferring a magic number from Fitts or Hick.

## Do not infer
- Hick is not a rule that menus cannot exceed N items.
- Fitts is not a fixed 44px requirement; WCAG 2.2 target-size criterion has stated exceptions.

## Verify the output
Measure actual interactive target rectangles and test focus/operability at narrow viewport sizes.
