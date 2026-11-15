# Personal Knowledge and the unified CLI

Design Engineering 4.1 supports **local, reviewed user/project/session preferences, principles, observations and reference bookmarks**. A personal preference is never peer-reviewed evidence, and no private Knowledge is published to the repository automatically.

## Install and use

From an editable full repository: `python -m pip install -e .`, then use the `de` or `design-engineering` command. In a managed Claude/Codex plugin where installation is undesirable, run `python /absolute/path/to/design-engineering/scripts/de.py` from the consumer project's directory. The portable launcher uses the plugin root for research resources, and the working directory for project-specific Knowledge. `python -m design_engineering` also works in the repository.

| Command | What it does |
| --- | --- |
| `de search "question"` | Returns separate `research` and `personal_guidance` collections |
| `de add "natural-language statement"` | Creates a **review draft**, not an active record |
| `de review --list` | Lists pending local and core research proposals |
| `de review <path>` | Previews a proposed change |
| `de review <path> --approve --reviewer owner` | Applies reviewed local guidance or approved source evidence |
| `de context` | Lists active session → project → user preferences |
| `de inspect source:N39` | Shows source/dependency impact |
| `de inspect local:<id>` | Inspects an approved local entry |
| `de check --smoke` | Checks installed resources and real Knowledge retrieval |
| `de qa page.html --out /tmp/critique` | Captures rendered visual evidence |
| `de qa page.html --mode tasks --tasks tasks.json --out /tmp/qa` | Checks scripted user journeys |
| `de qa page.html --mode static` | Performs HTML structure triage |

Legacy Python scripts remain modular implementation libraries and advanced diagnostics; users do not need to remember their names.

## Create a preference in natural Korean

`de add "나는 지나치게 둥근 카드보다 정교한 사각형을 좋아해" --scope project --type preference --tag typography`

The command produces `.design-engineering/drafts/local-<id>.json` and identifies possible related records. It does **not** activate the preference. Preview the JSON and explicitly approve:

`de review .design-engineering/drafts/local-<id>.json --approve --reviewer owner`

`de context --json` returns active preferences. `de search "사각형 인터페이스" --json` returns source-linked academic findings under `research` and separate user-authored statements under `personal_guidance`. No personal guidance is presented as scientific confirmation.

Use `--scope user` for preferences shared across projects. Use `--scope session` plus global `--session-id my_session_01` for temporary session direction; session files remain in the OS temporary directory until cleaned up and are not guaranteed to disappear when a chat closes.

## Other Knowledge kinds

- `preference` — subjective UI/brand preference; default type for natural text.
- `principle` — user/project-authored design principle, without claiming academic verification.
- `observation` — test or review observation; **requires** `--context` and `--outcome`.
- `reference` — private document bookmark; `de add --file notes.md --type reference --scope project --title "Reference notes"`. The original local file is SHA-256 fingerprinted but not uploaded, or automatically treated as reviewed evidence.
- `evidence` — maintainer-reviewed source for the core catalog only. Requires `--scope core --type evidence --file paper.pdf --title "Exact title" --authors "Verified authors"`. The existing ingest process produces an excerpt candidate; a human must inspect the document, mark the candidate approved, record limitations and claims, then use `de review <review-json> --approve --reviewer maintainer`. Publishing core Knowledge inside read-only plugin installations may fail; use an editable repository checkout. Core research cannot be created by merely typing a plausible claim.

For observations: `de add "모바일 제목 잘림" --type observation --context "390px Safari" --outcome "두 번째 줄 잘림"`.

## Storage and safety

| Scope | Storage | Notes |
| --- | --- | --- |
| core | Skill repository `knowledge/` | Curated sources/claims; not editable with a personal preference |
| user | `$DE_HOME/knowledge.json`, else XDG config directory / `~/.config/design-engineering` (or Windows AppData) | Separate from repository and project |
| project | `<consumer-project>/.design-engineering/knowledge.json` | Local to a specific codebase |
| session | OS temp directory `design-engineering-sessions/<session-id>/knowledge.json` | Requires a safe explicit session ID; clean up as needed |

For a consumer project outside the current working directory supply the **global option** `de --project /path/to/project add ...`. Personal data never goes to a network connector just because it was registered.

- Approval requires an explicit CLI flag and reviewer label. This does not cryptographically authenticate a human. AI should only approve when its user clearly authorized persistent registration.
- Approval rejects exact duplicates, stale storage checksums, wrong project/scope and changed reference fingerprints. Similar entries are surfaced for review but complex meaning contradictions are **not reliably detected**.
- `de context` returns session → project → user records as context, not as authoritative research. User instructions and real project requirements still decide what to apply.
- `de review --archive local:<id> --scope project --approve --reviewer owner` hides a local entry but retains its historical record.
- Nothing in this feature verifies an empirical claim, runs a semantic preference inference model or syncs Knowledge across devices.
- Local storage files are written privately where possible; user/project files are not encrypted by this CLI and must be protected through OS permissions. The skill repository ignores its own `.design-engineering/` data; consumer projects should add that directory to their own ignore policies if it contains sensitive material.

## Agent workflow

1. User explicitly requests persistent preference or Knowledge registration.
2. Agent chooses scope and type, preserves the user's original meaning and calls `de add`.
3. Agent shows proposed classification and existing related items. It does not silently treat a session comment as a permanent instruction.
4. After the user approves, agent calls `de review ... --approve --reviewer ...`.
5. Before designing, use `de context` for personal preferences and `de search` for separately labelled research; explain any conflict between saved preference, project constraints and current request.

AI interpretation is useful for drafting/organizing prose, **not** for inventing source identities or autonomously promoting research as verified.
