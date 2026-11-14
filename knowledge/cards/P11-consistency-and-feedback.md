# P11 — Use consistency for predictability, not uniformity

**Type:** RESEARCH  — **Source IDs:** R3, H1, S1

## Use when
Multiple actions or states are similar, inconsistent, hidden, destructive or confusing.

## Evidence and scope
Heuristic and standards-based guidance must be separated from empirical outcome measurements. Refer to `knowledge/sources.json` for original source URLs and access limits.

## Transferable reasoning moves
1. Describe control intent, initial state, action, success/error/empty/retry states and reversibility.
2. Keep the mental model coherent across labels, links, keyboard operation and status announcements.
3. Allow meaningful differences where exact sameness harms the workflow.
4. Test interacting states (filter + deep link + back navigation), not isolated components.

## Do not infer
- Grudin critiques simplistic interpretations of consistency.
- Not all forms must reset on success; not all interfaces need the same error UI.

## Verify the output
Exercise state transitions in a running browser, including undo and keyboard paths where applicable.
