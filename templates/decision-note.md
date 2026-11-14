# Decision trace — a working record, not a research citation in the UI

For a major design decision, prefer `python scripts/decision_trace.py new <path> --goal '...'`
and validate with `python scripts/decision_trace.py validate <path>`.
For a trivial fix, a short internal note is enough; no universal paperwork quota.

| Stage | Short question |
| --- | --- |
| Problem | What does the user actually need? What remains uncertain? |
| Evidence | Which source claim IDs are relevant? What did the study **actually** test? |
| Hypothesis | What design move might transfer here, and what could falsify it? |
| Alternatives | Did different concepts express different meanings, or just colors? |
| Implement | Which code/artifact changed? |
| Critique | What was observed on actual screens or flows? |
| Revision | What changed because of critique? |
| Verification | What passed/failed, and what was not tested? |

`SOURCE_FINDING` (claim supported within a study's scope), `FRAMEWORK`, `STANDARD`,
`PRACTITIONER`, and `DESIGN_HYPOTHESIS` are **not interchangeable**.
Do not claim a passing test without an associated observation and inspection artifact.
