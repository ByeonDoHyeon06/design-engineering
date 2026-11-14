---
name: design-engineering
description: Research-informed, context-flexible design engineering for websites and interfaces. Retrieve source-scoped research, explore meaningful design hypotheses, implement, inspect real rendered UI, validate user tasks, and revise.
---

# Design Engineering — Claude Code entry point

This adapter uses the canonical skill and resources bundled **at the plugin root**. Before applying the skill:

1. Resolve the installed plugin root with `${CLAUDE_PLUGIN_ROOT}`. Do not assume the current project is the plugin.
2. Verify the following files exist:
   - `${CLAUDE_PLUGIN_ROOT}/SKILL.md`
   - `${CLAUDE_PLUGIN_ROOT}/scripts/knowledge_index.py`
   - `${CLAUDE_PLUGIN_ROOT}/knowledge/catalog.json`
   - `${CLAUDE_PLUGIN_ROOT}/methods/`
   - `${CLAUDE_PLUGIN_ROOT}/templates/`
3. If any required resource is missing, **stop and report an incomplete plugin installation**. Do not claim Knowledge retrieval was performed; do not invent or silently substitute research references. Suggest reinstalling from the GitHub marketplace as a full Claude Code plugin. A standalone `SKILL.md` import is not a full installation.
4. If resources exist, read the entire `${CLAUDE_PLUGIN_ROOT}/SKILL.md` and follow its working loop. This canonical file remains the source of truth.

For retrieval and verification use absolute plugin-root paths, not relative paths from a consumer project:

```bash
test -f "${CLAUDE_PLUGIN_ROOT}/SKILL.md" &&
test -f "${CLAUDE_PLUGIN_ROOT}/scripts/knowledge_index.py" &&
test -f "${CLAUDE_PLUGIN_ROOT}/knowledge/catalog.json" &&
test -d "${CLAUDE_PLUGIN_ROOT}/methods" &&
test -d "${CLAUDE_PLUGIN_ROOT}/templates"
python "${CLAUDE_PLUGIN_ROOT}/scripts/knowledge_index.py" rebuild
python "${CLAUDE_PLUGIN_ROOT}/scripts/knowledge_index.py" search 'design question' --top 5 --json
```

Run auxiliary scripts with their documented dependencies available. Cite actual cards and verified claim scope; report untested UI checks as `NOT TESTED`. This adapter is an entry point, not a replacement for the full repository.
