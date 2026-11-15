---
name: design-engineering
description: Research-informed, context-flexible design engineering for websites and interfaces. Retrieve source-scoped research, interpret designer problem-solving methods, explore distinct hypotheses, implement, critique real rendered screens, verify task flows and revise. Not a style reference collection or fixed website/dashboard template system.
---

# Design Engineering — knowledge applied through feedback

Build a design that serves its **meaning and user tasks**, not a prescribed visual style. Research helps generate and challenge hypotheses; it does not manufacture universal layout recipes. Preserve the user's content, constraints, brand, domain rules and functional contract. A Skill cannot fine-tune model weights; humans' design methods are transferable questions, not proven agent-performance laws.

## Portable resource loading

This root `SKILL.md` is the **only** canonical skill instruction for every agent. Resolve paths from the directory containing this file (the **skill root**), not from the current product project's working directory. Before relying on local research, verify `knowledge/catalog.json` and `scripts/knowledge_index.py` are present alongside this file; run commands with the skill root as the working directory or with an equivalent explicit path. If support files are absent, state that the installation is incomplete and **do not claim local research was retrieved**. Do not assume one agent's environment variables or installation path exist in another.

## Working loop (scale the formality to the task)

1. **Frame:** Identify user goal, audience, content/data, consequential actions, uncertainty and protected requirements. If the observed failure suggests the original framing is wrong, revisit it.
2. **Retrieve:** Search the unresolved *question*, not a page type. `python scripts/knowledge_index.py search 'question' --top 5 --json`. Read relevant full cards and source limits. For source-checked claims use `--verified-only`. Absence of results means **no retrieved evidence**, not proof that research is absent.
3. **Interpret evidence:** Separate `SOURCE_FINDING`, `FRAMEWORK`, `STANDARD`, `PRACTITIONER` and `DESIGN_HYPOTHESIS`. Check study population, method, source-access level, `do_not_infer`, and whether the finding transfers to this problem. Verification of an abstract is not independent replication.
4. **Explore meaning first:** When substantive design choices are open, compare genuinely different **interpretations and visual relationships**, not only palettes or motifs. Learn design *operations* (reframe, sketch, simplify, test metaphors), never copy a famous designer's look. Do not force diversity where the brief has one natural answer. `templates/concept-exploration.example.json` is optional scaffolding.
5. **Implement and trace:** Record major choices as problem → evidence + scope → hypothesis → alternative → code/artifact → checks, using `templates/decision-note.md` or `scripts/decision_trace.py`. Small straightforward fixes do not need paperwork. Never include research metadata in production UI unless requested.
6. **Render, critique, test and revise:** Inspect actual desktop/mobile screenshots for hierarchy, proportion, density, rhythm, meaningful graphic expression, typography and cropping. Run browser geometry smoke tests, **and** separately verify representative user-task flows, state changes, error recovery and keyboard behavior. Link each discovered issue to a concrete revision and a fresh observation. If a hypothesis fails, change it; do not merely decorate or hide the problem.
7. **Report with limits:** State artifact, important tradeoffs, what was actually inspected/tested, what failed or remains untested. Do not call automated browser assertions a user study, screenshot inspection a WCAG audit, or AI preference a measured usability result.

## Knowledge Retrieval 2.0

- `python scripts/knowledge_index.py rebuild` — disposable offline FTS5 index from the catalog and cards.
- `python scripts/knowledge_index.py search '행사 홈페이지에서 정보를 명확하게 전달하는 방법' --top 5 --json` — bilingual question analysis, concept expansion, FTS+character retrieval, and provenance-linked results. These offline concepts are heuristics, **not complete semantic understanding**.
- `--verified-only` filters by **explicit claim ID + matching reverified source**, not filename or K-prefix. Results include `verified_claims`, `source_scope`, `do_not_infer` and evidence state.
- Optional *real* local sentence embeddings: `--embedding-model /path/to/pre-downloaded-model`; requires extra `sentence-transformers` and does **not** download a model automatically. Model validity/quality depends on that choice.
- `python scripts/retrieval_benchmark.py` — repeat a transparent regression dataset; do not confuse the curated benchmark with held-out real-world evaluation.

## Evidence and optional external AI

- Source identity, selected paper sections and claim provenance are in `knowledge/sources.json`, `knowledge/verified/claims.json` and `knowledge/VERIFICATION-POLICY.md`. Unreviewed legacy cards remain available, but must not be promoted to verified research findings.
- `scripts/knowledge_ingest.py` accepts PDF/MD/HTML/TXT → local candidate → **explicit source-aware approval**. No auto-publishing of model claims. See `knowledge/README.md`.
- Gemini is **off by default**. With a separately configured `config.json`, OS-level `GEMINI_API_KEY` and explicit permission for metadata transmission, `scripts/knowledge_research.py 'question' --provider gemini --approve-external --json` may select local card IDs. Gemini is advisory; unrecognized IDs are rejected. No cloud File Search or new-paper discovery is claimed.

## Visual and task verification

- `python scripts/visual_critique.py start page.html --out /tmp/visual-review` — screenshots at 1440/390/320 and geometric issue candidates. **You must actually view the images** and edit `critique.json`; no automatic aesthetic scores. `python scripts/visual_critique.py validate /tmp/visual-review/critique.json` checks that "fixed" issues have after-evidence. See `docs/visual-critique.md`.
- `python scripts/ux_scenarios.py validate my-tasks.json` and `python scripts/ux_scenarios.py run page.html my-tasks.json --out /tmp/task-review` — scripted browser task assertions, **not** observation of a human participant. See `docs/ux-validation.md`.
- `python scripts/decision_trace.py new trace.json --goal '...'` and `python scripts/decision_trace.py validate trace.json` — evidence-to-decision links with observed revision proof.
- Existing `static_page_audit.py`, `visual_qa_capture.py`, `browser_smoke.py` remain available. If browser tools are missing, mark screenshots/interactions as `NOT TESTED`, never as passed.

## Non-negotiable boundaries

- **No forced branch** between homepage, dashboard, admin or editor. No canonical aesthetic, mandatory hero/cards/charts, visual reference gallery, fixed UI-type decision tree, invented copy, or research-citation stuffing.
- Keep user-facing meaning and task performance primary. Do not equate novelty with visual noise or minimalism with correctness.
- Check semantics, keyboard, contrast, error states and applicable WCAG success criteria with their exceptions; no universal numeric CSS "scientific constants".
- Verify image rights and private-data boundaries. Do not send client information, unpublished source texts or credentials to external services without explicit authorization.
- Use only the few relevant cards and tools. The point is *learning from evidence and revising an artifact*, not maximizing research references or checklist length.
