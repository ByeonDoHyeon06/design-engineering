# Knowledge verification policy

## Status definitions

| Status | Guaranteed | Not guaranteed |
|---|---|---|
| `official_normative_standard_verified` | W3C original requirements and their conditions are checked | Full conformance of a generated UI |
| `official_standard_scope_verified` | ISO metadata, current edition and scope from ISO site | Full proprietary standard clauses/ISO compliance |
| `publisher_abstract_verified` | Publication identity, authorship and claim supported by publisher abstract | Full methods, effect sizes, replication |
| `author_abstract_verified` / `institutional_abstract_verified` | Author/institution summary and publication identity | Independently verified causal impact |
| `prior_register_not_reverified` / `abstract_or_metadata` | Legacy breadcrumb only | Fresh verified finding |

## Claim protocol

1. Start with an unresolved design question. Retrieve a relevant K-card (not all papers).
2. Check `verified/claims.json`: direct source summary, study scope, `do_not_infer` limitations.
3. Apply a practical design move as a **hypothesis**. Do not make a universal rule from one context.
4. Validate with actual data, screens, tasks and users where feasible. Report exactly what was tested.
5. Any new source needs DOI or institutional/publisher identity, actual review scope, exact provenance URL, and explicit claim scope before publication.

## Reliability notes

- No statistical strength grade is assigned by intuition; experimental design, populations, sample sizes and replication must be read before confidence ratings can be upgraded.
- A peer-reviewed paper may still be context-bound; publication status is not proof of general effect.
- Two records pointing to the same original study do not count as independent replication.
- A synthesis of two studies is **AI/practitioner inference** unless the synthesis was directly tested.
- Use `python scripts/audit_evidence.py` for structural checks. This is not an external scholarly validation service.

## Selected primary-text checks

For `A2`, `V02` and `V03`, selected sections of publicly accessible author/institutional manuscripts were additionally inspected on 2026-11-14. Scope is recorded in `knowledge/sources.json`; this does not mean all appendices, datasets or statistical analyses were independently replicated.

## Retrieval provenance contract (current)

- `verified-only` requires a `**Verified claim IDs:** VCxx` reference in the **actual card body** and matching `source_id` in that card's catalog entry. The source record must have a `reverified_at` value. A K prefix, source list alone, or model opinion is insufficient.
- Returned result objects include `verified_claims` with `verification_basis`, `source_scope` and `do_not_infer`. A single card can contain source-supported findings and novel design advice: only the registered claims are source-scoped.
- Verified publication metadata or abstract is **not** peer-review of an AI summary, full-text analysis, replication or evidence of a specific generated UI improvement.
- Retrieval ranking is not an evidence-quality grade. Claim relevance and strength need separate critical review, including contradictory or unavailable studies.
- The optional Gemini selector may rank local registered cards, but cannot change verification status or create an approved source.
