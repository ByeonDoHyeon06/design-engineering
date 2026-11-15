# v4 Knowledge operations

The root SKILL.md remains the only agent instruction file (Claude + Codex). The v3 registries retain the only copy of research and card contents. The v4 graph is a typed **projection**, not a second catalog.

## Storage
- `knowledge/catalog.json`, `cards/`, `sources.json`, `verified/claims.json`, `concepts.json`: canonical text and provenance
- `knowledge/v4/governance.json`: sparse, human-reviewed lifecycle overrides, aliases, source equivalences, optional public-safe observations and concept relations
- `knowledge/v4/schema.json`: allowed node types and relations
- `scripts/knowledge_graph.py`: materialize graph, audit dependencies and export disposable snapshots
- `scripts/knowledge_governance.py`: manual proposal and explicit apply

IDs have typed prefixes in the graph: source:, claim:, concept:, method:, practice:, observation:. Legacy IDs are unchanged in their original files. A lifecycle state of `active` means searchable, **not scientifically verified**.

## Inspection

```bash
python scripts/knowledge_health.py --json
python scripts/knowledge_graph.py validate
python scripts/knowledge_graph.py impact source:N39
python scripts/knowledge_graph.py export --out .cache/v4-graph.json
python scripts/knowledge_index.py search '한글 타이포그래피 줄바꿈' --json
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-v4.json
python scripts/knowledge_scale_benchmark.py --size 1000 --size 10000
```

Exports are derived artifacts and should not be edited. Search hides `archived` and `superseded` methods by default; `--include-inactive` allows audit retrieval. `needs_review` remains visible with an explicit label.

## Reviewed lifecycle (never automatic)

```bash
python scripts/knowledge_governance.py propose-status method:K16 --status needs_review --reviewer maintainer --reason 'Recheck source scope' --out .local/k16-review.json
python scripts/knowledge_governance.py apply .local/k16-review.json --reviewer maintainer --confirm
python scripts/knowledge_governance.py propose-alias source:old-N39 source:N39 --reviewer maintainer --reason 'Known ID alias' --out .local/alias.json
python scripts/knowledge_governance.py propose-equivalence source:E4 source:A7 --reviewer maintainer --reason 'Same DOI; review editions' --out .local/equivalence.json
```

Proposals carry the governance file SHA-256 and cannot overwrite newer changes. All changes need explicit reviewer, explanation and --confirm. An equivalence link does **not** merge or delete either source. Store confidential observations outside the public skill repository; never upload raw study data without permission.

The existing `knowledge_ingest.py` still requires source excerpts and human review. v4 prevents duplicate normalized DOI/URL registration. Prefer connecting an existing source/claim/method rather than adding another card.

## Quality and limits

- CI runs full installation smoke, typed graph validation, tests and v3.8/v3.9 regression suites; v4 diagnostic queries include out-of-domain negatives.
- Synthetic 1k/10k graph benchmark does not measure real retrieval speed or human usefulness.
- Source type, claim support, transfer hypothesis, lifecycle status and implementation result are independent. Don't combine them into a made-up confidence score.
- v4 intentionally keeps existing files readable; a destructive mass migration is neither needed nor performed.

## Search capacity rehearsal

```bash
# Bounded synthetic relationship-graph measurements (1k/10k)
python scripts/knowledge_scale_benchmark.py --size 1000 --size 10000
# Actual synthetic SQLite FTS build and query (not academic papers)
python scripts/knowledge_scale_benchmark.py --size 1000 --search-size 1000
# Optional heavier manual run
python scripts/knowledge_scale_benchmark.py --size 10000 --search-size 10000
```

These numbers depend on the runner, filesystem, Python and SQLite versions. Do not extrapolate simulated graph timings into actual 10k-paper performance. For archived source IDs, use `impact` to review dependent methods and claims; an obsolete source must not silently retain the same verified-only search presentation.
