---
name: design-engineering
description: Research-informed design engineering for interfaces. Frame user goals, retrieve source-scoped evidence, explore meaningful alternatives, implement, inspect real rendered screens, verify task flows, and revise. Adapt to the brief; never enforce a fixed style or page template.
---

# Design Engineering

Design for **meaning, clarity, and user tasks**, not a stock aesthetic. Preserve the user's actual brand, content, accessibility needs, product facts, constraints and functional expectations. The skill is a reasoning workflow and local Knowledge library, **not** model fine-tuning or proof that a generated design will succeed.

## Skill root and resources

This is the **only** canonical `SKILL.md` for Codex and Claude Code. Resolve resource paths relative to the directory containing this file, **not** the user's application directory or a platform-specific parent. Before claiming research retrieval, check `knowledge/catalog.json`, `knowledge/claims.json`, `knowledge/governance.json` and `scripts/knowledge_index.py`. If files are missing, report an incomplete installation; do not fabricate studies or substitute unrelated evidence.

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
