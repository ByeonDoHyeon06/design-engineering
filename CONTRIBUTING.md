# Contributing

- Keep `SKILL.md` current and concise; Git commits/releases, not historical prose, track versions.
- Do not add third-party design galleries, unlicensed fonts, copied layouts or style presets.
- Every verified research finding must link to a source, real review scope, `do_not_infer`, and the actual card's verified claim IDs.
- Novel design prescriptions derived from papers remain `DESIGN_HYPOTHESIS` until independently tested.
- For retrieval changes, extend `benchmarks/retrieval-v38.json` with new natural queries, include negative examples, and run `python scripts/retrieval_benchmark.py`.
- For each new test or script, avoid network calls, secret exposure, forced style branches, fabricated UX outcomes, or version records in the runtime package.
- Run `python -m unittest discover -s tests -q` and `python scripts/audit_evidence.py`. Browser tests are optional and should report NOT TESTED if unavailable.
- Do not commit `.cache`, `.local`, API keys, collected copyrighted PDFs or user data.

## v4 Knowledge contribution gate

Do **not** create one new card per paper or add arbitrary synonyms to pass one curated query. Before proposing Knowledge:
1. Search existing concepts, source IDs, verified claims and methods. Explain why a new claim or method is necessary.
2. Check normalized DOI/URL and edition/translation differences with `python scripts/knowledge_health.py --json`; potential duplicates need human review, not automatic merging.
3. Clearly separate publication verification, exact claim support, applicability and design hypothesis. `active` lifecycle status is never a truth grade.
4. Use `python scripts/knowledge_graph.py impact source:<id>` to assess affected methods before revising or deprecating a source. Lifecycle changes require a reviewer, reason and explicit approval.
5. Add a retrieval regression **and a no-answer/negative example** when retrieval rules change; do not tune only to training-like examples. Record false positives and precision as well as hit rate.
6. Confirm old catalog IDs stay readable, Claude/Codex still use one root `SKILL.md`, and no private observations or screenshots are committed.

Required checks: `python scripts/knowledge_graph.py validate`, `python scripts/knowledge_health.py --json`, `python scripts/retrieval_evaluation.py`, and `python -m unittest discover -s tests -v`. Run the optional `knowledge_scale_benchmark.py --search-size 1000` when changing the index.
