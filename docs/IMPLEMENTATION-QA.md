# Current implementation QA — 2026-11-14

## Scope

This is an engineering smoke/regression record, NOT proof that v3.8 improves design quality over previous Skill versions. No new research source has been externally peer-reviewed or replicated during this refactor.

| Area | Result | Verified scope |
| --- | --- | --- |
| Existing + new unit tests | 44/44 passed | Offline parser/metadata/validation compatibility tests |
| Prior missing question | P05 and P06 retrieved in top 3 | Local Korean natural-language concept expansion + retrieval |
| Retrieval regression | 20/20 hit@3, MRR 0.925 | Small, explicitly curated in-domain dataset, not held-out evaluation |
| Claim-scoped filter | Passed | Explicit claim linkage and verified source required, not K filename prefix |
| Design trace | Passed | Rejects simulated completion without a recorded outcome/evidence path |
| Visual critique record | Passed | Real Chromium screenshot capture at 1440/390/320 for an existing LAYER / 27 HTML, with geometry-review candidates; visual judgment not automated |
| Scripted UX task checks | 2/2 passed | A previously supplied LAYER / 27 HTML: workshop filter and form error/focus at 390px. No real-user testing |
| Gemini API live call | NOT TESTED | No account key; local selection and mock-based legacy tests only |
| Sentence-transformers semantic reranking | NOT TESTED | Optional dependency/model is absent; runtime guards covered |
| Actual design-quality A/B gain | NOT TESTED | Requires independent repeated creation and blinded rendered evaluation |

## Known limits and backlog

1. Local default meaning expansion is curated bilingual rules, SQLite FTS5 and n-gram similarity; it is not a general-purpose embedding model. Synonym gaps and ranking misses remain possible.
2. 20 regression questions were authored to cover known problems and should not be cited as independent statistical retrieval accuracy. Add genuinely new held-out questions and an adversarial relevance set.
3. Claim status means publisher/author abstract, official standard or selected source scope was checked; it does not imply full-text independent replication or project-specific causal effect.
4. Screenshot critiques need an agent/human who actually views images and records observations. The tool is only an evidence contract and iteration ledger.
5. DOM assertions and automated keyboard events cannot substitute for representative user studies or real assistive technology testing.
6. Pre-commit and CI workflows are deliberately offline and do not validate optional Gemini connectivity or playwright browser installation.
