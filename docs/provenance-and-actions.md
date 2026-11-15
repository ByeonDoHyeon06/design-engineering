# Source attribution and Knowledge-to-Action

Design Engineering records the actual **skill source** and separately reports what an operator says an agent used. Search results still distinguish source-registered research from practical design hypotheses.

## Verify which skill you are using

```bash
de provenance inspect --skill-root /absolute/path/to/design-engineering --json

de provenance capture \
  --skill-root /absolute/path/to/design-engineering \
  --out .local/skill-execution.json \
  --usage skill_invoked \
  --execution-log /path/to/raw-agent-session.log \
  --knowledge-log /path/to/actual-search.json \
  --browser-log /path/to/actual-browser-check.json

de provenance verify .local/skill-execution.json --json
```

The capture contains the **resolved absolute skill root**, `SKILL.md` SHA-256, installation completeness, Git origin and HEAD SHA (if available), tracked Git cleanliness, the expected repository, and SHA-256 hashes of any supplied execution/search/browser logs. The expected repository defaults to `ByeonDoHyeon06/design-engineering`. The tool **does not run an agent or verify its internal instruction loading**. Invocation is always **operator-reported**, even if a log was supplied.

| Recorded source or usage | Attribution |
| --- | --- |
| Matching Git origin, clean tracked files, complete install, real skill-invocation log | Locally source-verified and *operator-reported* invocation; not independently attested |
| The correct full skill exists but was not invoked | `NOT_EXECUTED`, not a valid skill-run attribution |
| Only GitHub docs or public excerpts were read | `documentation_only`, not an installed skill execution |
| Different remote repository or modified tracked files | `MISMATCHED_REPOSITORY` or `UNVERIFIED_SOURCE_IDENTITY` |
| Installed wheel without Git metadata | May be functional, but its **Git commit identity is unverified** |
| Alternate material was used | Disclose; do not attribute the full result exclusively to the selected skill |

Do not create fabricated agent logs, falsify a `git` remote, or label a document-reading session as an executed skill. Saved manifests and all supporting logs are **local private evidence**; do not put them in the blind evaluator packet.

### Use during a controlled A/B evaluation

After `de eval init`, record a manifest *for each task and arm*:

```bash
# Skill condition: recorded source must match, usage must be operator-reported invocation.
de eval provenance --run .local/evaluation/pilot-01 \
  --task corporate-home --condition skill \
  --manifest .local/skill-execution.json

# Baseline condition: make a separate manifest with --usage not_executed.
de eval provenance --run .local/evaluation/pilot-01 \
  --task corporate-home --condition baseline \
  --manifest .local/baseline-not-executed.json

de eval validate --run .local/evaluation/pilot-01 \
  --require-provenance --require-complete --json
```

The operator-only mapping and provenance pointers stay in `private/assignments.json`. **Nothing identifying the arm is added to `blind/packet.json`.** A later changed log or `SKILL.md` hash is flagged. A missing manifest does not silently turn into `VERIFIED`: default reports disclose incomplete attribution. Existing studies can still run without manifests; they should not claim a fully verified skill comparison.

**Limitation:** Local source identity does not prove that an agent used those instructions. To establish that strongly, an external evaluator must examine authentic raw session logs and execution traces.

## Turn relevant Knowledge into candidate actions

The opt-in `--actions` flag adds **practice suggestions** to the existing search response without changing the research or personal-guidance results:

```bash
de search "72개 세션이 있는 행사 프로그램에서 연사를 빠르게 찾으려면?" \
  --scope core --actions --explain --json
```

- `research`: existing source-scoped Knowledge results with card/source/claim references, evidence status and search signals; unchanged.
- `practice_guidance`: **distinct practitioner design hypotheses**, filtered by the question *and* actually retrieved Knowledge card IDs. Each provides when-to-consider, alternatives, likely failure modes, **counterexamples**, screen-level verification tasks, and explicitly linked card references.
- `coverage` when `--explain` is also used: what was found in **this installed library**, not an assertion about all academic research.

Initial topics are dense schedules, information density, mobile composition, Korean UX typography, forms and states, exploration of meaningful alternatives, and screenshot critique. The canonical rules live in `methods/action-guidance.json`. They are conditional guidance, **not verified universal layout laws**, and are not copied from an external skill.

### Selection and failure behavior

A suggestion is eligible only when (1) a topic cue appears in the *user's actual query* and (2) at least one of its linked cards appears among the retrieved `research` rows. No retrieved research, no matching cue, or an unrelated result returns an empty suggestion list. Suggestions are capped and keep their explicit provenance. There is no default card grid, brand aesthetic, typography score or automatic UI code generation.

This first version intentionally uses conservative lexical matching. It can miss paraphrased intent or overmatch broad terms. To improve it, add reviewed examples and test questions before introducing expensive semantic reranking or auto-created claims.

When implementing a suggested action, **inspect the full Knowledge card and its source limitations**, then use the actual project content and browser validation. A suggestion does not prove its proposed layout or a user's success.

## Implementation safeguards

- New guidance references existing catalog IDs and lives beside existing `methods/` content; no duplicate scientific source registry.
- Source identity, operator assertion and design evidence remain different records.
- Search outputs remain backward compatible unless `--actions` is requested.
- No automatic preference persistence, Knowledge ingestion, runtime model call, benchmark score or visual change.
