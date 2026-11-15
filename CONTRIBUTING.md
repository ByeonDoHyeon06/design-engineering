# Contributing

Contributions should improve **design decisions, evidence quality, or observable task results**, not simply increase card count.

## Ground rules

- Keep one canonical root `SKILL.md`; do not add a per-agent copy for Codex or Claude Code.
- Before adding Knowledge, search existing cards, concepts, claims and source IDs. Explain what cannot be expressed by existing records.
- Preserve scholarly scope. A publication, verified quote, design hypothesis, and successful user task are **not** the same evidence.
- Never auto-merge sources because of an identical URL/DOI. Distinct editions and translations may be legitimate; record a reviewed equivalence when appropriate.
- Do not commit keys, private observations, third-party PDFs, copyrighted asset collections, generated caches or customer data.
- Keep new Python tools local-first; external provider calls need explicit consent and must remain optional.

## Knowledge changes

1. Run `python scripts/knowledge_health.py --json` and `python scripts/knowledge_graph.py validate`.
2. Check source scope, verification status and dependent methods using `python scripts/knowledge_graph.py impact source:<ID>`.
3. Use `scripts/knowledge_ingest.py` for source candidates. Quotes and interpretations require manual approval.
4. Use `scripts/knowledge_governance.py` for reviewed lifecycle changes, aliases or equivalence links. All changes need a reviewer and reason.
5. Add positive **and** out-of-domain/no-answer regression cases for search changes. Do not optimize solely for the benchmark examples.

## Testing

```bash
python scripts/validate_install.py --root . --smoke
python scripts/knowledge_graph.py validate
python scripts/knowledge_health.py --json
python -m unittest discover -s tests -v
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-core.json
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-typography.json --top 5
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-relevance.json
```

For changes to the search implementation also run `python scripts/knowledge_scale_benchmark.py --search-size 1000`. For visual or UX claims, include actual browser screenshots/scenario results. Record untested items as `NOT TESTED`, never as passed.

## Pull requests

Describe **problem, changes, data provenance, tests, and limitations**. Keep unrelated historical cleanup separate from new research claims. CI and a passing review do not certify real-user comprehension or the aesthetic quality of generated designs.

## Personal Knowledge and CLI contributions

- Keep one CLI entry point in `design_engineering/cli.py`; do not add new user-facing commands as unrelated script executables.
- Personal records belong to OS user, project or explicit session scope, **never** directly to core `knowledge/` files.
- An AI's text classification is a draft; approvals must be explicit. No automatic write from casual conversations or fabricated research claims.
- Include duplicate rejection, cross-project isolation, stale draft handling and agent-neutral CLI smoke tests for additions.
- Document scope, privacy and CLI examples in `docs/personal-knowledge.md`.

## Controlled design evaluation

To demonstrate changes in design quality, use [Design evaluation](docs/design-evaluation.md) rather than only curated retrieval scores. Keep control/skill model and tools matched, collect actual two-viewport screenshots, avoid exposing condition labels to reviewers, and disclose **all missing, negative and tied outcomes**. Do not insert mock human ratings or fake benchmark improvements into the repository. The 12 sample tasks are a development pilot, not independent evidence of success.


## Distribution and release verification

The repository and the wheel must expose the **same canonical Knowledge and script resources**. Packaging is build-only through `setup.py`; do not maintain duplicated Knowledge copies in Git. CI must install the built wheel in a separate virtual environment and **run `de check --smoke` outside the source tree**, including Korean search, to catch missing resources and read-only cache errors. Do not claim a release is portable based solely on editable install tests.
