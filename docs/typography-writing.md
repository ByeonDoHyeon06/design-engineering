# Typography, Korean writing and content layout

This is a **small optional judgment protocol**, not another mandatory checklist for every task. Use it when typography, Korean UX writing or content architecture materially affects task success. Canonical workflow: `SKILL.md`.

## Frame the problem
- User task / target audience / writing language(s) and formality level
- Critical verified product claims, obligations, terminology, prices and measurements to preserve
- Reading mode: quick scan, comparison, continuous reading, form, warning
- Real source content and explicit unknowns (never invent copy to fill a layout)

## Research selectively
Use `knowledge_index.py search` with the **uncertain question**:
- `python scripts/knowledge_index.py search '한국어 한영 혼합 제목 줄바꿈 타이포그래피' --top 5 --json`
- `python scripts/knowledge_index.py search '자연스러운 한국어 오류 메시지 버튼 문구' --top 5 --json`
- `python scripts/knowledge_index.py search '콘텐츠 중요도에 따라 레이아웃 정보 구조' --top 5 --json`

Read K16, K17 and K18 only when returned/relevant. Source identity or an official draft is **not** experimental validation. `verified_claims: []` is expected for these new practitioner/draft cards; do not call them verified empirical findings.

## Concrete decision and revision record
For each significant decision, record:

| Field | Example |
|---|---|
| User problem | Korean schedule name wraps and obscures date |
| Protected meaning | Session title, day/time and speaker stay unchanged |
| Source/status | K16 / W3C Group Note **Draft** / no causal effect claim |
| Alternative A/B | Show time above title vs. align time in side column |
| Hypothesis | A keeps title intact on 320px |
| Before screenshot | file + viewport |
| After screenshot | file + viewport |
| Task check | Find session time / result or NOT TESTED |

## Typography check
- Actual typeface license and **Hangul/Latin glyph coverage** checked
- Real Korean and mixed-language examples tested; fallback tested
- Hierarchy distinguishes title, label, helper, body, numeric data by purpose (not just size)
- Long headings, error messages, user-entered text and translated text do not clip
- Spacing override checked **for loss of content**, not mistaken for an author CSS baseline
- Tested widths, browser names, font loading status and screenshots recorded

## Korean UX writing check
- Meaning, legal obligations, numbers, brand terms and actions preserved
- Awkward translationese, duplicated subjects, vague benefit claims and unnecessary passives considered **contextually**, not blindly replaced
- Buttons indicate resulting action; errors give a next step when known
- Honorific level consistent across labels, forms and feedback; no synthetic claims
- Human language review marked separately from automated linting

## Content-layout check
- Each piece of content labelled orientation/evidence/sequence/comparison/action/warning/feedback
- Layout is chosen from **meaning and task**, not a universal hero/card/grid rule
- Information order and keyboard/focus order match intended interpretation
- Responsive layout tested with real Korean text, not short lorem placeholders
- Copy revisions and layout revisions both allowed when evidence suggests a mismatch

## Evaluation boundaries
Screenshot review does not establish comprehension; successful click assertions do not establish usability; source-backed design reasoning does not prove layout efficacy. Report failures and UNTESTED explicitly. Avoid numeric aesthetic scores with false precision.

## References
- W3C Hangul Layout Group Note Draft, 21 March 2026: https://www.w3.org/TR/klreq/
- W3C WCAG 2.2 SC 1.4.12: https://www.w3.org/TR/WCAG22/#text-spacing
- GOV.UK Understanding content design: https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/plan-manage-content/understand-content-design/
- GOV.UK Identifying user needs: https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/plan-manage-content/identify-user-needs/
