# Knowledge management

This document describes the **current** Knowledge lifecycle. Use it before adding sources, editing claims, deprecating cards or changing concept links. The original data is in `knowledge/{catalog,concepts,sources,claims,governance}.json`; do not edit generated graph snapshots or SQLite caches.

## 1. Find the existing record first

```bash
python scripts/knowledge_index.py search 'specific unresolved design question' --top 5 --json
python scripts/knowledge_health.py --json
python scripts/knowledge_graph.py impact source:N39
```

A new publication does not automatically require a new card. Check whether an existing concept, claim or method can reference the new source instead. The health report's duplicate-DOI and unreferenced-source warnings are review candidates, not proof of an error.

## 2. Register source evidence

`knowledge_ingest.py` prepares an offline candidate from a local PDF, Markdown, TXT or HTML document. PDF text extraction requires the optional `pypdf` dependency. A candidate may be generated with the optional external model **only with explicit permission to transmit the document**.

```bash
python scripts/knowledge_ingest.py prepare paper.md \
  --title 'Exact source title' --authors 'Verified authors' \
  --url 'https://doi.org/EXAMPLE'
```

Examine the review JSON inside `.local/ingestion/`: source identity, access rights, exact text excerpt, page/location, the supported claim, study scope, limitations and counterexamples. A matching quotation is necessary but not sufficient to approve a causal interpretation. Only a human-reviewed proposal may be committed with `approve --reviewer ... --confirm`. The ingester rejects an existing matching source fingerprint or normalized DOI/URL; do not circumvent this by inventing an ID.

## 3. Keep verification separate from lifecycle

- **Source status** says what was accessed and reverified. Abstracts, drafts, full text and interviews are not interchangeable.
- **Claim verification** says which statement is supported in which population/setting, with a `do_not_infer` boundary.
- **Method relevance** says a design operation may be useful for this task; it does not prove performance.
- **Lifecycle status** (`active`, `needs_review`, `superseded`, `archived`) controls retrieval and review. It is not an evidence strength score.

For claim requirements see [Evidence policy](../knowledge/VERIFICATION-POLICY.md).

## 4. Propose reviewed governance changes

All changes to review status, ID aliases and source equivalence are explicit and auditable.

```bash
python scripts/knowledge_governance.py propose-status method:K16 \
  --status needs_review --reviewer maintainer \
  --reason 'Recheck source interpretation' \
  --out .local/k16-review.json

# Review the JSON and affected dependencies before applying
python scripts/knowledge_graph.py impact source:N39

python scripts/knowledge_governance.py apply .local/k16-review.json \
  --reviewer maintainer --confirm
```

For known aliases use `propose-alias`; for same-work records use `propose-equivalence`. Approved equivalence records **do not merge bibliographic identities**. Proposals carry the current governance SHA-256 to reject stale updates. Do not treat this guard as a substitute for repository permissions or human review.

The ordinary search omits archived/superseded **methods**. `--include-inactive` exposes old material for audits. Verified-only queries do not present archived-source claims as current verified evidence.

## 5. Test and release

```bash
python scripts/knowledge_graph.py validate
python scripts/knowledge_health.py --json
python scripts/audit_evidence.py
python -m unittest discover -s tests -v
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-core.json --top 3
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-typography.json --top 5
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-relevance.json --top 3
```

Include negative/no-answer queries when changing search heuristics, and explain any intentional score tradeoffs. Current benchmark cases are a small, hand-written regression set, not a blinded study. Synthetic 1,000/10,000-record load tests measure local implementation costs, not the accuracy of thousands of genuine research papers.

## Maintenance policy

Do not automatically delete unreferenced sources: they can be historical breadcrumbs awaiting review. When a source is withdrawn, `knowledge_graph.py` flags current dependents for reassessment. Never promote an unreviewed claim because a filename starts with `K` or because an AI model suggested it.

Record public-safe metadata only. Keep project-specific UX observations, original user research, screenshots, API keys and copyrighted full-text documents outside this repository unless sharing is explicitly authorized.

## Personal knowledge (non-academic)

Use `de add` to propose user/project/session preferences, principles, observations or reference bookmarks, then `de review --approve --reviewer ...` after explicit authorization. Personal entries never enter `knowledge/catalog.json` or `knowledge/claims.json` and do not acquire verified-claim IDs. To add source-backed research to the common repository, use `de add --type evidence --scope core --file ...` and the existing reviewed ingester. See [Personal Knowledge](personal-knowledge.md).

## Retrieval coverage, explicit review due dates and gap handling

Use `de search "question" --explain --json` to inspect `why_matched` concept/FTS/lexical signals and registered claim links. A `no_registered_card_match` finding means **this installed library returned no card at the current threshold**; it is not a claim that the academic literature contains no answer. `matched_cards_without_explicit_checked_claim` means retrieved cards have no registered reviewed claim link, not that their practitioner methods are useless.

`de check --review-due --json` reports only **explicitly scheduled** `review_due` records and `needs_review` lifecycle overrides; it does not infer a universal one-year expiry date or silently reclassify research. For absent/weak results, propose new sources through the existing human-reviewed ingestion route. Neither gap reporting nor review queues automatically add, archive or rewrite Knowledge.

## Contextual practice suggestions are not verified claims

`de search "specific task question" --actions --json` adds a separate `practice_guidance` response. Its options, countercases and suggested tests originate from `methods/action-guidance.json` and are **practitioner hypotheses**, selected only when the query and retrieved card IDs both match. They do not modify ranked `research` results, alter `claims.json`, make an unsupported research claim or automatically choose a UI. See [Source attribution & action guidance](provenance-and-actions.md).
