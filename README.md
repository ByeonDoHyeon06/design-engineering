<div align="center">

<img src="assets/design-engineering-mark.webp" width="76" height="76" alt="Design Engineering logo: intersecting precision frames" />

# Design Engineering

**From evidence to intentional design.**

A research-informed design engineering skill for **Codex and Claude Code**.  
Find relevant knowledge, design for actual context, and validate the result.

<p>
  <a href="README.md"><strong>English</strong></a> ·
  <a href="i18n/README.ko.md">한국어</a>
</p>

<p>
  <a href="#overview">Overview</a> ·
  <a href="#approach">Approach</a> ·
  <a href="#getting-started">Get started</a> ·
  <a href="#documentation">Documentation</a>
</p>

</div>

<p align="center">
  <picture>
    <source media="(max-width: 640px)" srcset="assets/hero-system-mobile.svg" />
    <img src="assets/hero-system.svg" width="100%" alt="Editorial illustration of research evidence becoming a deliberate interface, with visual review annotations." />
  </picture>
</p>

## Overview

**Design Engineering** helps AI coding agents make more deliberate design decisions. It connects source-aware research, content and layout reasoning, hands-on implementation, and inspection of the actual rendered interface.

It does **not** impose a house style, component library, or universal page template. The question is not only *what should we build?*, but also *why does this approach fit, and what did we actually verify?*

<table>
  <tr>
    <td width="50%" valign="top">
      <strong>◈ &nbsp; Research-informed</strong>
      <p>Retrieve relevant papers, standards, and practitioner methods while preserving their limitations and provenance.</p>
    </td>
    <td width="50%" valign="top">
      <strong>◇ &nbsp; Context-driven</strong>
      <p>Let content, brand, user needs, and real constraints shape the composition instead of forcing generic patterns.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <strong>↗ &nbsp; Inspect &amp; refine</strong>
      <p>Review browser captures and task flows, document issues, make changes, and check the result again.</p>
    </td>
    <td valign="top">
      <strong>◎ &nbsp; Personal knowledge</strong>
      <p>Let people and agents propose preferences and observations without mixing them into the verified research library.</p>
    </td>
  </tr>
</table>

## Approach

<p align="center">
  <picture>
    <source media="(max-width: 640px)" srcset="assets/process-loop-mobile.svg" />
    <img src="assets/process-loop.svg" width="100%" alt="The six-stage Design Engineering loop: Understand, Research, Explore, Build, Validate, and Refine." />
  </picture>
</p>

Start with the question and the real content. Look up only the knowledge needed, compare meaningful directions, build a working artifact, and inspect the rendered result. A passing automated test is **not** automatically a successful user experience.

### Knowledge is contextual, not a pile of prompts

#### Separate evidence from personal direction

<p align="center">
  <picture>
    <source media="(max-width: 640px)" srcset="assets/knowledge-context-mobile.svg" />
    <img src="assets/knowledge-context.svg" width="100%" alt="Conceptual diagram: source-backed research and separately scoped personal preferences inform a design decision without being conflated." />
  </picture>
</p>

Core evidence stays separate from user, project, and session preferences. AI-assisted additions begin as drafts and require review before they become active guidance.

#### Inspect, revise, and verify

<p align="center">
  <picture>
    <source media="(max-width: 640px)" srcset="assets/validation-study-mobile.svg" />
    <img src="assets/validation-study.svg" width="100%" alt="Conceptual before-and-after interface views: a problem is identified, the layout is revised, and the result is inspected again." />
  </picture>
</p>

Visual critique examines hierarchy, typography, spacing, and interaction states. These illustrations explain the **review workflow**, not real product test results.

## Getting started

Install the **complete repository**, not just `SKILL.md`. The knowledge library and validation tools live alongside it.

### <img src="assets/integrations/claude.svg" width="24" height="24" alt="" /> Claude Code

Run these commands in Claude Code:

```text
/plugin marketplace add ByeonDoHyeon06/design-engineering
/plugin install design-engineering@design-engineering-marketplace
```

### <img src="assets/integrations/codex.svg" width="24" height="24" alt="" /> Codex

Clone the skill into your project's skills directory:

```bash
mkdir -p .agents/skills
git clone https://github.com/ByeonDoHyeon06/design-engineering.git .agents/skills/design-engineering
```

### Unified CLI

From a full, editable checkout:

```bash
python -m pip install -e .
de search "How should mixed Korean and Latin headings wrap?"
de check
```

For managed plugin installations where editing the plugin is undesirable, use the portable launcher: `python /path/to/design-engineering/scripts/de.py --help`.

<details>
<summary><strong>Add your own design direction</strong></summary>

Preferences and project notes start as **reviewable drafts**, not automatically applied instructions.

```bash
de add "Prefer precise square layouts and clear typography" --scope project
de review --list
de review <proposal-path> --approve --reviewer owner
de context
```

Personal guidance is stored locally and labeled separately from scientific evidence. For scopes, permissions, and more commands, see [Personal knowledge & CLI](docs/personal-knowledge.md).

</details>

## Documentation

| Guide | What you'll find |
| :--- | :--- |
| [Architecture](docs/architecture.md) | System layout, retrieval, and knowledge relationships |
| [CLI & personal knowledge](docs/personal-knowledge.md) | Commands, local preferences, and review workflow |
| [Knowledge management](docs/knowledge-management.md) | Source ingestion, provenance, duplication, and lifecycle |
| [Evidence policy](knowledge/VERIFICATION-POLICY.md) | What a source or claim does—and does not—establish |
| [Typography & writing](docs/typography-writing.md) | Korean text layout, microcopy, and content structure |
| [Visual critique](docs/visual-critique.md) · [UX validation](docs/ux-validation.md) | Rendered-screen and task-based review |
| [Design evaluation](docs/design-evaluation.md) | How to run transparent, blinded skill vs baseline studies |
| [Contributing](CONTRIBUTING.md) | Contribution process and required checks |

<details>
<summary><strong>Repository map</strong></summary>

```text
SKILL.md                Canonical instructions for both agents
design_engineering/      Unified CLI and locally scoped knowledge
knowledge/               Cards, sources, claims, and governance
methods/                 Practitioner methods
scripts/                 Retrieval and verification tools
templates/               Review and workflow templates
assets/                  Original README artwork and project mark
docs/ · i18n/            Guides and translations
tests/ · benchmarks/     Automated checks and retrieval regressions
.claude-plugin/ · agents/ Integration metadata
```

</details>

## Contributing

Contributions to design reasoning, research quality, accessibility, validation, and documentation are welcome. Check existing records before adding more knowledge, and distinguish source-backed findings from interpretation. See [CONTRIBUTING.md](CONTRIBUTING.md).

<sub>Research retrieval is not automatic scientific certification. Screenshots and scripted browser checks do not replace usability studies. The goal is better-informed, testable design—not a universal aesthetic score.</sub>
