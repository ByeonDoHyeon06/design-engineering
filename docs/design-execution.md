# Design execution: content, composition and visual asset direction

Use this workflow to convert a real content brief into alternative design directions **before** producing UI. This is an execution contract and quality gate, not a prescriptive visual aesthetic or generator.

## Brief

Create a JSON file with the actual goal, audience, action and real content:

```json
{
  "schema_version": 1,
  "goal": "Help prospective enterprise buyers understand the product scope",
  "audience": "Technical evaluation teams at mid-size organizations",
  "primary_action": "Request a demonstration through the contact form",
  "constraints": ["Brand vocabulary must be preserved", "Mobile layout must fit 320px"],
  "content_blocks": [
    {"id": "promise", "role": "hero", "content": "A precise, user-supplied product statement"},
    {"id": "features", "role": "explanation", "content": "Actual capabilities, with no invented claims"},
    {"id": "contact", "role": "contact", "content": "Contact us to discuss a suitable deployment"}
  ]
}
```

These are **illustrative fictional strings**, not factual descriptions of any product. Content blocks and roles should be written from the user's brief, not invented as if they were customer facts.

## Design a composition

```bash
de design plan --brief my-brief.json --out .local/my-design-plan.json
```

The new plan has two **empty conceptual directions** to fill. Define their *information relationship, layout strategy, trade-offs, primary-action visibility*, and how each content block is presented. Distinct color palettes alone are not distinct ideas. The plan requires an explicit direction choice and reason.

Add source-backed IDs under `principles.research_refs` and local preferences under `personal_preference_refs`, separately. The validator checks ID shapes, not the scientific accuracy of an uninspected paper. Inspect any cited content independently.

## Visual asset direction (without unnecessary images)

For every content block choose: `none`, `photo`, `illustration`, `diagram`, `icon`, `video`, or `other`. Record why the image exists, provenance (`original`, `user_supplied`, `generated`, `licensed`), usage/source rights, a meaningful alt-text or decorative decision, and its intended mobile crop/behavior. The validator does not make up permissions or silently generate imagery.

An image should clarify meaning, illustrate a real feature or reinforce the intended brand. Decorative assets need justification; do not create meaningless gradients or claim a generated mockup depicts a running product. For culturally specific Korean and mixed-script layouts, check actual copy and font coverage at rendered sizes.

```bash
de design validate .local/my-design-plan.json --json
de design validate .local/my-design-plan.json --require-ready
```

`ready=false` on missing decisions. `--require-ready` rejects draft or incomplete plans. This is **completeness only**: it cannot prove the chosen design is visually excellent or accessible.

## Render and revise

1. Implement a viable design in the chosen project framework; don't replace real user content with generic placeholders.
2. Run `de qa page.html --mode visual --out .local/review-01` (Playwright required).
3. **Open real screenshots** at 1440, 390 and 320 px. Manually note hierarchy, density, rhythm, crop and layout problems.
4. Fill the produced `critique.json` with screenshot references, observations and proposed revisions.
5. Change code, re-capture the actual interface, record an after-screenshot and after-observation for every proposed fixed issue.
6. Run `de design review .local/review-01/critique.json`. It rejects missing paths, copied before/after captures and falsely confirmed fixes.
7. Validate keyboard/focus/interactions separately through task scenarios; a pixel comparison does **not** certify WCAG conformance or user comprehension.

The review loop does not auto-edit CSS, auto-judge aesthetic quality, or fill fake screenshots. It makes revisions explainable and auditable. This process is available before external A/B evaluation; it does not require the user to conduct the planned blind comparison yet.
