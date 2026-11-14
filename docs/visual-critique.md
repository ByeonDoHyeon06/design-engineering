# Visual Critique Loop — operating contract

This is **not** an automatic beauty scoring algorithm. Running `start` captures real
screens at 1440/390/320 and records geometric indicators. A designer/agent must
**view the pixels** and then describe visible issues. An unresolved observation is
not a verified design defect and a stylistic preference is not a WCAG failure.

```bash
python scripts/visual_critique.py start path/to/site.html --out /tmp/visual-critique
# Inspect all *-viewport.png and *-full.png; edit /tmp/visual-critique/critique.json
python scripts/visual_critique.py validate /tmp/visual-critique/critique.json
```

For each **manual** issue append an entry in `observations`:

```json
{
  "id":"VIS-001", "dimension":"hierarchy", "viewport":390,
  "severity":"high", "observation":"Program CTA blends with dense hero graphic",
  "before_screenshot":"390-viewport.png",
  "proposed_change":"Reduce competition between headline and graphic, preserve event detail",
  "status":"open", "after_screenshot":null, "after_observation":null,
  "linked_decision":"DEC-003", "detected_by":"manual"
}
```

After a change, capture **new** screenshots, link `after_screenshot` with an actual
existing file, record what changed, and set `status: fixed` only if verified.
Check: hierarchy / proportion / density / rhythm / meaning / typography/crop
craft / cross-viewport consistency. Do not assign fake numeric aesthetics scores.

Inspect keyboard/focus/interaction separately with UX task scenarios. Geometry
smoke checks are not proof of user comprehension, aesthetic preference, or WCAG conformance.
