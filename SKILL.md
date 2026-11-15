---
name: design-engineering
description: Research-informed design engineering for interfaces. Frame user goals, retrieve source-scoped evidence, explore meaningful alternatives, implement, inspect real rendered screens, verify task flows, and revise. Adapt to the brief; never enforce a fixed style or page template.
---

# Design Engineering

Design for **meaning, clarity, and user tasks**, not a stock aesthetic. Preserve the user's actual brand, content, accessibility needs, product facts, constraints and functional expectations. The skill is a reasoning workflow and local Knowledge library, **not** model fine-tuning or proof that a generated design will succeed.

## Skill root and resources

This is the **only** canonical `SKILL.md` for Codex and Claude Code. Resolve resource paths relative to the directory containing this file, **not** the user's application directory or a platform-specific parent. Before claiming research retrieval, check `knowledge/catalog.json`, `knowledge/claims.json`, `knowledge/governance.json` and `scripts/knowledge_index.py`. If files are missing, report an incomplete installation; do not fabricate studies or substitute unrelated evidence.

## Unified CLI and personal Knowledge

The user-facing command is `de`. The full package also supports `python -m design_engineering` from the skill repository and the portable launcher `python <SKILL_ROOT>/scripts/de.py` from any consumer project without installing the package. The **consumer project's working directory** determines project scope; never treat the installed skill root as the consumer project. Run `de --project /path/to/project ...` when needed.

- `de search "design question" --json` retrieves source-scoped core findings under `research` and separately labelled user/project/session guidance under `personal_guidance`. A preference is **not** research evidence.
- `de context --json` returns active personal direction with session → project → user precedence. Interpret conflict in the context of the current user request and real product requirements.
- `de add "I prefer ..." --scope project --type preference` creates a pending **local draft**, not active guidance. Other local types: principle, observation (requires context+outcome), reference (requires a local source file). `de review <draft> --approve --reviewer owner` activates a reviewed entry.
- `de add --type evidence --scope core --file PAPER --title TITLE --authors AUTHORS` uses the existing source-aware, human-reviewed ingestion path. Never promote user opinions or fabricated source summaries into core research.
- `de inspect source:N39`, `de check --smoke` and `de qa page.html --out /tmp/review` unify research/validation access. The underlying scripts remain available for advanced checks.

**Persistence consent matters:** Do not write user preferences merely because the user mentions a passing preference. Draft only when a user asks to record or apply ongoing knowledge; request/obtain their explicit approval before invoking the review/commit action. A reviewer label and CLI flag are not human identity authentication. User/project Knowledge stays local and is never automatically sent to the public GitHub catalog or external models. For full paths, scope boundaries and limitations consult `docs/personal-knowledge.md`.

## Design loop

1. **Frame:** Clarify user goal, audience, actual content, important actions, constraints, uncertainties and protected claims. Revisit the brief if observed failures contradict assumptions.
2. **Retrieve selectively:** Search unresolved questions, not page genres. Run `python scripts/knowledge_index.py search 'specific design uncertainty' --top 5 --json`. Read only relevant card bodies and inspect source scope. `--verified-only` restricts to explicit registered claim links, **not** K-prefix cards. No results means no suitable registered evidence was found.
3. **Interpret:** Distinguish findings, normative standards, practitioner reasoning and design hypotheses. Review population/method, accessible source portion, `do_not_infer`, version and context. An abstract or official draft is not independent verification of a UI outcome.
4. **Explore meaning:** When alternatives matter, compare differing information relationships, user journeys and expressions, not only palettes. Avoid style imitation, gratuitous variation, a default hero or prescribed card grids. Use `templates/concept-exploration.example.json` only if useful.
5. **Implement and trace:** Build an actual artifact with working states and authentic content. For consequential decisions record goal → source and limit → hypothesis → alternative → implementation → observed check via `scripts/decision_trace.py` or `templates/decision-note.md`. No excessive documents for minor edits.
6. **Render, inspect and verify:** Use `python scripts/visual_critique.py start page.html --out /tmp/visual-review`. **Open the captured images**, inspect hierarchy, type, rhythm, color, contrast, crop, viewport continuity and meaning. Validate functional scenarios with `scripts/ux_scenarios.py`, including errors, keyboard focus, mobile navigation and task outcomes. Make a revision, capture again, and only mark `fixed` when evidence exists.
7. **Report:** Deliver the usable artifact; state sources that actually informed decisions, alternatives/tradeoffs, tests actually run and unresolved risks. A browser assertion is not a user study; a screenshot is not a WCAG audit.

## Typography, Korean and content

For real text-layout problems, query K16 (Hangul typography and mixed-script layout), K17 (natural Korean UX copy) and K18 (content roles and layout), as applicable. Preserve legal/brand terminology, product facts and exact actions; review Korean honorific tone, translationese, line wrapping, truncation and cross-viewport typography **in the rendered UI**. W3C Hangul layout is a Group Note Draft, and English practitioner guidance does not experimentally validate Korean wording choices. Details: `docs/typography-writing.md`.

## Content-first design execution and visual assets

For nontrivial UI tasks, start from actual text, user goals and action states. `de design plan --brief BRIEF.json --out PLAN.json` scaffolds **two distinct layout/meaning directions** plus image provenance and responsive checks. Complete it by judgment, not by automatically inventing features or claims; `de design validate PLAN.json --require-ready` checks completeness, not visual quality. For rendered UI, use `de qa ... --mode visual`, view the actual pixels and record corrections; `de design review critique.json` requires different before/after screenshot content and an actual after-observation. See `docs/design-execution.md`. Research, creative hypotheses and personal preferences remain different kinds of inputs.

## Knowledge retrieval confidence and user preference conflicts

For searches needing transparent provenance, use `de search "question" --explain --json` and distinguish matched cards, reviewed claim links and the current library's gaps. The diagnostic is **not** a literature-wide search or a claim that no applicable research exists. `de context --conflicts --json` flags **possible lexical opposition** between saved preferences for review (do not auto-delete or auto-prioritize). For lifecycle work, `de check --review-due` reports only explicit review records, never invented expiry. See `docs/knowledge-management.md`.

## Controlled design evaluation (optional)

When asked to **measure whether this skill improves outputs**, do not manufacture outcomes or compare unrelated designs. Use `de eval tasks` and `de eval init` to prepare matched baseline-versus-skill trials, capture **actual desktop and mobile PNGs for both**, and share only `blind/` with independent reviewers. Only human-authored, evidence-linked reviews may enter `de eval report`; without them the status is `NO_OBSERVATIONS`. Preserve negative results and missing pairs. The CLI does **not** generate webpages, perform human studies or supply aesthetic scores. See `docs/design-evaluation.md`. This procedure is not required for ordinary interface design work.

## Knowledge and governance

The current library keeps **one source of truth** for each record type: `knowledge/sources.json`, `knowledge/claims.json`, `knowledge/concepts.json`, `knowledge/catalog.json` and the actual `knowledge/cards/`. `knowledge/governance.json` holds sparse lifecycle/review metadata; the typed graph is derived, not a duplicate store.

- Search: `scripts/knowledge_index.py` — offline SQLite FTS5, bilingual concept hints and character similarity; optional local sentence embeddings are opt-in. Scores are **heuristics, not calibrated confidence**. Use `--relative-cutoff 0` when investigating missed matches; `--include-inactive` only for historic/audit searches.
- Provenance: `python scripts/knowledge_graph.py validate` and `python scripts/knowledge_graph.py impact source:N39`. Check dependencies, not merely card counts.
- Integrity: `python scripts/knowledge_health.py --json` flags duplicate/unreferenced sources for **human review**, never automatic merging. A lifecycle state of `active` is **not** evidence verification.
- Changes: `scripts/knowledge_governance.py` uses proposal → explicit reviewer → `apply --confirm`; do not silently archive/rewrite sources. `scripts/knowledge_ingest.py` requires original source, quotation checks, limitations and approval.
- Evaluate: `scripts/retrieval_evaluation.py` reports hit@k, precision and false positives on curated queries including no-answer cases; it is not a benchmark of general human performance.

Read `docs/architecture.md`, `docs/knowledge-management.md` and `knowledge/VERIFICATION-POLICY.md` when working on the Knowledge system.

## Tools and optional providers

`scripts/static_page_audit.py` checks deterministic HTML structure issues; `scripts/visual_critique.py` captures screenshots and audit records; `scripts/ux_scenarios.py` validates observable tasks. Actual browser tests need Playwright/Chromium; otherwise mark `NOT TESTED`. Check images/fonts usage rights and real asset availability.

Gemini is **off by default**. External metadata selection via `scripts/knowledge_research.py` needs a configured `config.json`, `GEMINI_API_KEY` and explicit outbound-consent flag. It cannot approve new evidence or invent verified source IDs. Never send client data or unpublished source material without authorization.

## Boundaries

- **No canonical aesthetic. No forced branch** by page type, no obligatory hero/cards/charts or style gallery; let goals and actual content determine the composition.
- Don't turn narrow experimental findings, designer advice or standards into universal numerical CSS rules.
- Do not increase card count or cited-paper count as a proxy for quality. Favor useful retrieval, accurate wording, actual visual polish, working interactions and verified revisions.
