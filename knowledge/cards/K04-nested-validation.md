# K04 — Validate the correct layer of a visualization design

**Knowledge type:** FRAMEWORK  
**Source IDs:** V02  
**Verification level:** SOURCE-IDENTITY + PUBLISHER/INSTITUTION ABSTRACT (or OFFICIAL NORMATIVE TEXT for WCAG). Full paper review is **not** claimed.  
**Verified claim IDs:** VC05

## When to retrieve
The chart renders correctly but users cannot answer their actual question.

## Verified source findings and study scope
- **Evidence — V02 (author abstract, peer-reviewed publication):** Munzner differentiates four nested levels: understand the domain problem/tasks/data; abstract into data and operations; choose encoding and interaction; implement algorithms. Upstream assumptions affect downstream validity.
- **Selected primary-paper sections checked:** The author explicitly cautions that the four levels are not a strictly linear process; confusing the problem/domain level with a graph encoding problem leads to downstream mismatches.
- **Evidence type:** A proposed and argued design-validation framework, not a controlled experiment establishing optimal layouts.

## Transferable reasoning moves — *derived design advice, not direct experimental findings*
1. Diagnose the earliest plausible failing layer; do not fix visual style if the task/data abstraction is wrong.
2. Write the intended user question and needed information before selecting chart or interface primitives.
3. Validate at the relevant level: domain-expert relevance, abstract data mapping, perceptual encoding, or computational performance. Iterate freely between levels.

## Countercases and overclaim guard
- Explicitly review source-specific constraints in `knowledge/claims.json` and source access levels in `knowledge/sources.json`.
- Do not turn a studied observation into a mandatory style rule, numerical CSS constant, or general guarantee of user performance.
- The agent must not assert that this study validated AI-generated UI, unless such testing exists elsewhere.

## Verification in a live design
Check task relevance with stakeholders, mapping against sample data, visual interpretation and actual performance separately.

## Provenance
- `V02` — A Nested Model for Visualization Design and Validation. https://doi.org/10.1109/TVCG.2009.111 (checked: 2026-11-14; author_abstract_verified)
