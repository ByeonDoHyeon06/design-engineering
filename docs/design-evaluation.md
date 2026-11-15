# Design evaluation: blinded, paired pilot studies

Design Engineering's existing Knowledge retrieval benchmarks measure whether relevant cards are found. **They do not establish that using the skill produces better interfaces.** This study scaffold supports comparison on actual artifacts while keeping **source evidence, agent performance, and reviewer judgments separate**.

It is a research workflow, not a benchmark result. The repo ships **12 curated fictional briefs with no model outputs or scores**.

## Evaluation question

> For comparable interface-design briefs, does access to the Design Engineering skill change the quality of the rendered interface, judged independently across multiple criteria, under otherwise matched conditions?

This is an *exploratory hypothesis*. A single positive study cannot demonstrate general design superiority. Report negative, tied, missing, and dissenting reviews with positive cases.

## Controlled conditions

| Control | Design Engineering |
| --- | --- |
| Same agent/model, effort and tool budget | Same agent/model, effort and tool budget |
| Same brief, content, assets, target browser and time budget | Same brief, content, assets, target browser and time budget |
| **Skill unavailable or not loaded** | **Complete skill available and explicitly invoked** |
| Fresh context without prior exposure to the skill | Separate fresh context containing skill resources |
| Actual implementation and captures | Actual implementation and captures |

Record actual agent version, model name, effort level, maximum elapsed time, token budget, tool permissions, runtime, and any failed execution. **Do not silently give the skill arm extra tools or more time.** A control that has already read the skill is contaminated; restart. If using different providers, run separate studies rather than treating models as equivalent.

A judge must not see the condition name, source code comments identifying the arm, prompts mentioning the skill, run logs, or the private random assignment. Use the generated **blind/** directory only. Visual styles can still reveal authorship; "blinded" is an intent and procedural safeguard, not a verified guarantee.

## 1. Select tasks and initialize

View the unscored brief catalog:

```bash
de eval tasks --json
```

Create a new directory under your local **ignored** workspace:

```bash
de eval init \
  --tasks benchmarks/design-tasks.json \
  --out .local/evaluation/pilot-01 \
  --seed 42 \
  --agent "Codex CLI / actual version" \
  --model "actual model identifier" \
  --effort "actual effort setting" \
  --protocol-note "Same 30-minute limit, browser tools and budget for both conditions"
```

This writes:
- `private/assignments.json` — random A/B↔baseline/skill mapping and operator metadata. **Keep private**.
- `blind/packet.json` — identical task briefs, dimension labels, and expected image names **without mapping**.
- `blind/<task-id>/` — empty destination for real screenshots. **No generated design output is implied**.

The A/B skill side is balanced across the twelve tasks (six on each side); the randomization is reproducible from the recorded seed. This mitigates simplistic side bias, but does not eliminate all confounders.

## 2. Generate both implementations independently

For **each** task, start two separate fresh agent sessions. Submit the same task's `brief`, `audience`, `task_goals`, `required_states`, `review_checks` and the shared rules in `benchmarks/design-tasks.json`.

The *only intended intervention* is whether the Design Engineering skill is available/invoked. Do not reveal either condition to the evaluator.

The operator should preserve full HTML/application builds, run logs, browser checks and failure details privately for reproducibility. Capture real desktop (~1440px) and mobile (~390px) PNGs after rendering. The evaluation CLI does **not** build pages or run agents. It accepts only supplied captures; do not pretend a screenshot is a complete accessibility or usability test.

Attach desktop and mobile captures for each condition:

```bash
de eval attach --run .local/evaluation/pilot-01 \
  --task corporate-home --condition baseline \
  --desktop /path/to/baseline-desktop.png \
  --mobile /path/to/baseline-mobile.png \
  --seconds 490 --input-tokens 3200 --output-tokens 2900

de eval attach --run .local/evaluation/pilot-01 \
  --task corporate-home --condition skill \
  --desktop /path/to/skill-desktop.png \
  --mobile /path/to/skill-mobile.png \
  --seconds 510 --input-tokens 3410 --output-tokens 3010
```

Duration and token values **above are purely illustrative arguments**, not measurements or claims about this skill. Supply only measured values; omit unknown metrics. The tool validates PNG structure and CRC, removes ancillary identity/EXIF/text chunks and saves the captures with anonymous `A/B` labels. It also tracks SHA-256 hashes to detect later file changes.

```bash
de eval validate --run .local/evaluation/pilot-01 --require-complete --json
```

Without complete captures, `ready_for_review` is false. **A successful basic validator run is not proof that all artifacts exist**; require completeness before recruiting judges.

## 3. Independent blind review

Share **only** `blind/` with judges, never the `private/` directory or attach command history. Generate a blank scorecard for each reviewer:

```bash
de eval scorecard --run .local/evaluation/pilot-01 \
  --judge reviewer01 --out .local/evaluation/reviewer01.json
```

No rating is prefilled. Reviewers must open and inspect both desktop and mobile captures for each task before writing:

- `preferred`: `A`, `B`, or `tie` (a paired preference, not an automatic rank).
- `reason`: a concrete rationale grounded in the visible artifact (minimum 20 characters).
- `artifacts_reviewed`: `true` once all four task captures are inspected.
- `ratings.A` and `ratings.B`: each dimension scored as an **integer 1–5**, where 1 is a serious shortcoming, 3 is sufficient, and 5 is unusually strong for the specified task.

The four intentionally separate **rubric dimensions** are:
1. **visual_hierarchy** — Can users distinguish primary content, navigation, and action visually?
2. **task_clarity** — Are next steps and task requirements visible and comprehensible from the interface? (Not a behavioral user-success measurement.)
3. **responsive_craft** — Are layouts, type, cropping, and focus affordances plausible across both desktop and mobile captures?
4. **originality** — Does the design express the brief rather than repeat default-looking patterns, without sacrificing meaning?

For function and accessibility claims use separate scripts and real project evidence (e.g. `de qa ... --mode tasks`). Never infer WCAG conformance, user comprehension, error recovery, or a conversion rate from screenshots. A blind judge can be independent, but an AI-based judge remains a **model judgment**, not a substitute for human participant evidence. Prefer multiple independent reviewers, keep disagreements, and disclose reviewer background.

## 4. Aggregate actual judgments

```bash
de eval report --run .local/evaluation/pilot-01 \
  --judgments .local/evaluation/reviewer01.json .local/evaluation/reviewer02.json \
  --out .local/evaluation/report.json
```

The report includes:
- Number of tasks attempted, actually reviewed, and missing/modified captures.
- Task-level skill wins, baseline wins, ties, and unresolved split verdicts (one vote per task after reviewer-majority aggregation).
- Win share **excluding ties**, or `null` when no decisive preference exists.
- Paired 1–5 rating differences per category for *descriptive inspection only*.
- Judge counts and transparent limitations, including subjective rating uncertainty.

If no scorecards contain actual judgments, the report status is **`NO_OBSERVATIONS`** and the win share is **`null`**. Missing tasks yield `INCOMPLETE`. The tool cannot silently generate winners, scores, model outputs, screenshots, or A/B experiment conclusions.

## Data hygiene and reporting policy

- Store private project artifacts and results in ignored local directories. Screenshots may still contain recognizable confidential project content. Explicitly obtain rights before sharing.
- Publish results with **all tasks**, prompt versions, model/effort/tool settings, exclusions, budget/time differences, reviewer method, negative outcomes and missing results, not just successful examples.
- Do not train or tune the skill only against the same curated 12-task set and then claim an independent benchmark. Hold out additional briefs and reviewers for later confirmation.
- Keep task quality, blind subjective review, functional checks, accessibility checks, runtime costs and user studies **separate**. Avoid a single pseudo-scientific "design score".
- For strong causal claims require independently replicated runs, prespecified analysis, adequate sample sizes and a measured user outcome; v4.2's tooling alone provides none of these.
