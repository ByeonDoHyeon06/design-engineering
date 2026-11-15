# Design Engineering

**Research-informed design engineering for Codex and Claude Code.**  
디자인의 근거를 찾고, 맥락에 맞는 시안을 설계하고, 실제 화면과 사용자 과제로 검증하는 범용 Agent Skill.

v4.1은 **하나의 CLI(`de`)** 와 **AI·사람이 함께 관리하는 개인화 Knowledge**를 제공합니다. 공통 학술 자료와 사용자의 디자인 선호는 명확히 분리됩니다.

## Why Design Engineering?

- **Evidence, not templates** — 논문·공식 표준·디자이너 견해의 출처와 한계를 확인합니다.
- **Meaning before layout** — 정보의 역할, 콘텐츠와 사용자의 목표에 맞춰 구성합니다.
- **Actual validation** — 실제 브라우저 화면과 시나리오를 확인하고 수정 전후를 기록합니다.
- **Personalized, not global** — 개인·프로젝트 선호가 공통 연구 근거로 오인되지 않도록 분리합니다.

## Install

**전체 저장소가 필요합니다.** 단일 `SKILL.md` 파일만 복사하면 Knowledge와 CLI를 사용할 수 없습니다.

### Codex

`mkdir -p .agents/skills`  
`git clone https://github.com/ByeonDoHyeon06/design-engineering.git .agents/skills/design-engineering`

### Claude Code

Claude Code에서:

`/plugin marketplace add ByeonDoHyeon06/design-engineering`  
`/plugin install design-engineering@design-engineering-marketplace`

플러그인 업데이트 후 설치본도 갱신하세요. 두 환경은 동일한 루트 `SKILL.md`와 Knowledge를 사용합니다.

### Unified CLI

전체 저장소에서 `python -m pip install -e .`를 실행하면 `de` 또는 `design-engineering` 명령을 사용할 수 있습니다. 로컬 에이전트 환경에서 설치하지 않으려면 **현재 작업 프로젝트에서** 다음처럼 호출하면 됩니다.

`python /absolute/path/to/design-engineering/scripts/de.py --help`

저장소 루트에서는 `python -m design_engineering`도 사용할 수 있습니다. CLI는 스킬 리소스와 사용자 프로젝트의 작업 디렉터리를 분리해 다룹니다.

## Quick start

`de search "한국어 제목의 줄바꿈을 어떻게 다듬을까?"`  
`de check --smoke`

자연어로 **프로젝트 선호를 제안**합니다.

`de add "사각형을 정교하게 사용하고, 의미 없는 그라디언트를 줄이고 싶어" --scope project`

이 단계에서는 실제 선호가 저장·적용되지 않습니다. 출력된 초안 경로를 확인하고 명시적으로 승인합니다.

`de review .design-engineering/drafts/local-<id>.json --approve --reviewer owner`

이제 `de context`로 적용 가능한 선호를 확인하거나 `de search "홈페이지 레이아웃" --json`에서 연구와 개인 지식을 **서로 다른 배열**로 받습니다.

AI는 사용자의 요청에 따라 초안 분류와 CLI 호출을 수행할 수 있습니다. **한 번 언급된 취향을 동의 없이 영구 등록하거나, 취향을 연구 결과로 둔갑시킬 수 없습니다.**

## Commands

| Command | Purpose |
| --- | --- |
| `de search "..."` | 학술 Knowledge와 개인 지식을 분리 검색 |
| `de add "..."` | 사용자·프로젝트 선호/원칙/관찰 초안 작성 |
| `de add --file paper.pdf --scope core --type evidence --title ... --authors ...` | 출처 근거 검토 후보 생성 |
| `de review --list` | 등록 대기 초안 목록 |
| `de review <draft> --approve --reviewer owner` | 승인 후 등록 |
| `de context --json` | session → project → user 선호 읽기 |
| `de inspect source:N39` | 출처와 연결된 주장·방법 조회 |
| `de check` | 설치·Knowledge·그래프 검증 |
| `de qa page.html --out /tmp/review` | 스크린샷 기반 검토 |
| `de qa page.html --mode tasks --tasks tasks.json --out /tmp/tasks` | 브라우저 태스크 검증 |

핵심 명령어는 단일 진입점으로 통합했지만 내부 구현은 작고 독립적인 모듈로 유지합니다. `de --project /other/project ...`를 사용하면 다른 소비자 프로젝트를 지정할 수 있습니다.

개인 문서의 로컬 북마크는 `--type reference --file ...`, 관찰은 `--type observation --context ... --outcome ...`를 사용합니다. 논문을 추가할 경우 **검토되지 않은 주장으로 공통 Knowledge를 자동 갱신하지 않습니다.**

자세한 사용법: [Unified CLI & Personal Knowledge](docs/personal-knowledge.md).

## How it works

`과제 정의 → 출처·개인 선호 검색 → 적용 범위 확인 → 시안 탐색 → 구현 → 렌더링·동작 검증 → 개선`

연구, 개인 취향, 설계 가설과 실제 테스트 결과는 독립적인 정보입니다. 높은 검색 점수는 학술 근거의 신뢰도나 디자인 성공 확률이 아닙니다.

## Repository

`SKILL.md` — Codex·Claude 공통 스킬 진입점  
`design_engineering/` — 단일 CLI와 개인 Knowledge 저장 계층  
`scripts/` — 검색·근거 관리·브라우저 검증 내부 모듈과 설치 없는 CLI 실행기  
`knowledge/` — 검증 범위를 구분한 공통 카드·출처·주장·거버넌스  
`methods/` — 디자이너의 방법론  
`templates/` — 작업·지식 등록 예시  
`docs/` — 아키텍처와 작업 지침  
`tests/`, `benchmarks/` — 단위·회귀 테스트  
`.claude-plugin/`, `agents/` — 에이전트별 배포 메타데이터

**프로젝트 지식은** `<project>/.design-engineering/`에, **개인 지식은** 사용자의 OS 설정 디렉터리에, **세션 지식은** 별도 임시 디렉터리에 보관합니다. 해당 저장소에 공개되거나 GitHub로 자동 업로드되지 않습니다.

## Documentation

- [Architecture](docs/architecture.md) — 데이터 경계, 그래프·검색 구조
- [CLI and personal Knowledge](docs/personal-knowledge.md) — 범위, 승인, 예제, 개인정보
- [Knowledge management](docs/knowledge-management.md) — 자료 등록·출처 검증·수명주기
- [Evidence policy](knowledge/VERIFICATION-POLICY.md) — 연구 검증 수준과 한계
- [Typography and writing](docs/typography-writing.md) — 한글 조판과 UX 문장
- [Visual critique](docs/visual-critique.md) / [UX validation](docs/ux-validation.md)
- [Contributing](CONTRIBUTING.md)

## Development

Python 3.10+를 권장합니다. 기본 검색과 개인 지식 관리는 외부 API 키가 필요 없습니다. PDF 추출 및 브라우저 자동화는 선택적 의존성입니다.

`python -m unittest discover -s tests -v`  
`python -m design_engineering check --smoke`  
`python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-relevance.json`

CI는 Knowledge와 인덱싱·CLI·기본 사용자 흐름을 검증합니다. 이것이 실제 사용자 연구, 디자인의 미적 품질 또는 논문 재현 검증을 의미하지는 않습니다.

Gemini 연동은 기본적으로 꺼져 있으며, 외부 전송에 대한 명시적 동의가 필요한 선택 기능입니다. 소스·이미지·서체의 사용 권한 및 개인 데이터 경계를 존중하세요.
