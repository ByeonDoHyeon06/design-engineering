---
name: design-engineering
description: Research-informed, context-flexible design engineering for websites and interfaces. Retrieve source-scoped research, explore distinct design hypotheses, implement, inspect actual rendered UI, test user tasks, and revise.
---

# Design Engineering (Claude Code entry point)

This is the Claude Code adapter for the canonical skill at `SKILL.md` in the plugin root.

**Before beginning design work, read the full canonical instructions at `${CLAUDE_PLUGIN_ROOT}/SKILL.md` and follow them.** The root file is the single source of truth; this entry point does not replace or summarize its working loop.

Use paths relative to `${CLAUDE_PLUGIN_ROOT}` when reading `knowledge/`, `methods/`, `templates/`, and `docs/`, or invoking `scripts/`. For example:

```bash
cd "${CLAUDE_PLUGIN_ROOT}"
python scripts/knowledge_index.py rebuild
python scripts/knowledge_index.py search 'design question' --top 5 --json
```

Use the repository's actual research claims and applicability limits; do not fabricate research findings. Use screenshot and task-validation tools only when their runtime dependencies are available, and report untested checks plainly. Preserve the user's project requirements and design system.
