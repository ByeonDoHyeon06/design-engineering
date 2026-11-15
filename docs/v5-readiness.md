# v5.0 readiness and deferred blind evaluation

This is a release gate and handoff guide, **not a version changelog**. The main README intentionally describes the long-lived project rather than listing releases.

## Implementation milestones

| Milestone | Intended capability | Code / reference | Verification boundary |
| --- | --- | --- | --- |
| 4.2 | Controlled A/B study framework | `de eval`, `benchmarks/design-tasks.json`, [evaluation protocol](design-evaluation.md) | Tooling tested; **no real A/B design outcome** |
| 4.3 | Content-led design and real visual critique | `de design plan/validate/review`, [design execution](design-execution.md) | Plans and screenshot integrity verified; **no automatic aesthetic ranking** |
| 4.4 | Knowledge usage explainability and review cues | `de search --explain`, `de context --conflicts`, `de check --review-due` | Lexical heuristics and registered coverage only; **not global semantic completeness** |
| 4.5 | Usable personal Knowledge lifecycle and portable distribution | `de knowledge list/edit/conflicts/archive`; full wheel build/install | Explicit review and history; local JSON is not a multi-user concurrent database |

## Before any external blind comparison

1. Merge prerequisite PRs in sequence: [#12](https://github.com/ByeonDoHyeon06/design-engineering/pull/12) → [#13](https://github.com/ByeonDoHyeon06/design-engineering/pull/13) → [#14](https://github.com/ByeonDoHyeon06/design-engineering/pull/14) → [#15](https://github.com/ByeonDoHyeon06/design-engineering/pull/15). Branches are stacked; **do not delete a branch that remains the base of another open PR** until that dependency is retargeted.
2. Verify installation on the agent and operating systems used in the study. GitHub CI is a package test, not a guarantee of every downstream runtime.
3. Freeze the study protocol, tasks, model/effort/tools/budget, prompt and skill commit. Select genuinely held-out tasks beyond the curated pilot if making general claims.
4. Generate real skill/no-skill implementations in separate clean agent contexts, **same conditions except skill availability**, with 1440px and 390px browser screenshots for both conditions. Keep full build/runtime evidence and account for noncompletions.
5. Give independent reviewers only `blind/`. Record their visible-image judgments, explanations and disagreements. Treat task-script results and accessibility checks as separate evidence.
6. Send back `de eval report` JSON, actual image pairs, task failures and qualitative feedback for a grounded v5.0 prioritization. Share only artifacts you have permission to disclose; never expose private assignment mapping to evaluators.

## Hold points

- **Blind test remains deferred** by the project owner until after implementation milestones complete. Do not silently run models or create design scores.
- The repository provides an **evaluation framework**, not evidence that one model or skill is superior.
- No benchmark win rate, causal design lift, WCAG-conformance result, or human usability statistic exists merely because the CI test suite passes.
- Design generation remains a coding-agent action. The skill supplies execution contracts and validation tools rather than generating pages autonomously.
- Windows/macOS/Linux wheel checks verify installation, offline data availability and Korean retrieval, not all OS-native browser automation or full agent integration.
