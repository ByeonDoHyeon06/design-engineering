# P06 — Make paths and destinations predictable

**Type:** RESEARCH  — **Source IDs:** R1, R2, H1

## Use when
Users must select among navigation routes, filters, search results or destination links.

## Evidence and scope
Model-based information-scent work informs hypotheses about user paths, not a fixed navigation layout. Refer to `knowledge/sources.json` for original source URLs and access limits.

## Transferable reasoning moves
1. Make link language predict what is at the destination.
2. Check whether repeated content references represent distinct jobs or redundant copies.
3. Inspect routes when filters or hidden states change content availability.
4. Validate deep links and return paths, not just click handlers.

## Do not infer
- Information foraging is not a universal rule that items must never repeat.
- UI labels in source do not prove users will predict destinations accurately.

## Verify the output
Give a representative information-finding task and log whether the expected destination was reached.
