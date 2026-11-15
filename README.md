# Design Engineering

**Research-informed design engineering for Codex and Claude Code.**

Design Engineering은 정해진 UI 템플릿을 제공하는 스킬이 아닙니다. 디자인 과제를 정의하고, 검증 범위를 알 수 있는 근거를 찾고, 설계 가설을 구현한 뒤 실제 화면과 사용자 과제로 평가하도록 돕습니다.

- **근거 중심 판단** — 출처·주장·적용 범위를 구분하고, 근거가 없는 설계 판단은 가설로 표시합니다.
- **의미 중심 구성** — 화면 유형이나 트렌드보다 정보의 역할, 브랜드 맥락, 사용자 행동에 따라 구조를 설계합니다.
- **실제 결과 검증** — 브라우저 스크린샷과 동작 테스트를 수행하고, 수정 전후를 기록합니다.
- **관리 가능한 지식** — 중복과 관계를 추적하고 자료의 변경·보관을 검토자 승인 아래 관리합니다.

> **v4.0** · 단일 `SKILL.md` · 로컬 우선 · 공개 연구 데이터는 참조 정보로만 제공 · 선택적 외부 AI

## Quick start

모든 기능을 사용하려면 **저장소 전체**가 필요합니다. `SKILL.md`만 복사하면 Knowledge 검색과 검증 스크립트를 사용할 수 없습니다.

### Codex

```bash
mkdir -p .agents/skills
git clone https://github.com/ByeonDoHyeon06/design-engineering.git .agents/skills/design-engineering
```

### Claude Code

Claude Code에서 마켓플레이스를 등록하고 플러그인을 설치합니다.

```text
/plugin marketplace add ByeonDoHyeon06/design-engineering
/plugin install design-engineering@design-engineering-marketplace
```

업데이트 시 `/plugin marketplace update design-engineering-marketplace`를 실행한 뒤 설치된 플러그인도 갱신하세요. 플러그인 루트의 `SKILL.md`, `knowledge/`, `scripts/`를 확인합니다. 공통 스킬은 **루트 `SKILL.md` 하나**이며 Claude 전용 복제본은 없습니다.

### 설치 확인

아래 명령은 설치된 스킬의 **루트 디렉터리**에서 실행합니다. 기본 검색에는 API 키와 외부 네트워크가 필요 없습니다.

```bash
python scripts/validate_install.py --root . --smoke
python scripts/knowledge_index.py search '한글 타이포그래피와 줄바꿈' --top 5 --json
```

## How it works

```text
과제 정의 → 필요한 Knowledge 검색 → 출처·적용 범위 검토
    → 의미 있는 대안 탐색 → 구현 → 실제 화면·사용자 과제 검증
    → 발견한 문제 수정 → 재검증 및 한계 보고
```

AI에게 "이 디자인을 Design Engineering 스킬을 활용해 제작하고, 관련 근거와 실제 검증 결과를 구분해 보고해 줘"라고 요청할 수 있습니다. 스킬은 **고정된 폰트·Hero·레이아웃을 강제하지 않으며**, 프로젝트의 기존 디자인 시스템과 사용자 요구가 우선입니다.

### 주요 도구

| 목적 | 명령어 |
| --- | --- |
| 근거 탐색 | `python scripts/knowledge_index.py search 'question' --top 5 --json` |
| 검증된 주장만 검색 | `python scripts/knowledge_index.py search 'question' --verified-only` |
| 출처 관계 검사 | `python scripts/knowledge_graph.py validate` |
| 출처 영향 추적 | `python scripts/knowledge_graph.py impact source:N39` |
| 중복·연결 상태 점검 | `python scripts/knowledge_health.py --json` |
| 설계 의사결정 검토 | `python scripts/decision_trace.py --help` |
| 실제 화면 비평 | `python scripts/visual_critique.py start page.html --out /tmp/visual-review` |
| 브라우저 사용자 과제 | `python scripts/ux_scenarios.py run page.html tasks.json --out /tmp/task-review` |
| 검색 품질 평가 | `python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-relevance.json` |

일반 검색은 보관·대체된 방법 카드를 제외합니다. 감사 목적의 과거 검색에는 `--include-inactive`를 사용합니다. 검색의 점수는 **관련도 휴리스틱**일 뿐, 연구 신뢰도를 의미하지 않습니다.

## Repository layout

```text
design-engineering/
├── SKILL.md                     # 모든 에이전트가 공유하는 유일한 스킬 지침
├── .claude-plugin/              # Claude Code 배포 메타데이터
├── agents/                      # Codex 에이전트 메타데이터
├── knowledge/
│   ├── cards/                   # 실제 설계 문제에 적용하는 지식 카드
│   ├── catalog.json             # 카드 메타데이터 및 검색 힌트
│   ├── concepts.json            # 한국어·영어 설계 개념
│   ├── sources.json             # 출처 및 검토 범위
│   ├── claims.json              # 출처가 명시된 검증 주장
│   └── governance.json          # 수명주기·별칭·관계의 승인 메타데이터
├── methods/                     # 디자이너 방법론
├── scripts/                     # Knowledge · 설계 · 브라우저 QA 도구
├── templates/                   # 의사결정·시나리오·자료 수집 예시
├── docs/                        # 아키텍처 및 운영 가이드
├── benchmarks/                  # 검색 회귀 및 부정 질의 평가 데이터
├── tests/                       # 자동 테스트
└── .github/workflows/           # CI
```

각 파일은 고유 목적을 갖습니다. 논문 1편을 추가할 때마다 카드를 새로 만들지 않으며, 원래 출처와 주장은 `sources.json` 및 `claims.json`에 유지됩니다. 관계 그래프는 이를 읽어서 **필요할 때 생성**합니다.

## Documentation

| 문서 | 내용 |
| --- | --- |
| [Architecture](docs/architecture.md) | 저장소 구성, 관계 그래프, 검색 구조 |
| [Knowledge governance](docs/knowledge-management.md) | 자료 등록·중복·검토·보관 및 영향 추적 |
| [Evidence policy](knowledge/VERIFICATION-POLICY.md) | 출처 검증과 주장 해석의 한계 |
| [Typography & Korean UX writing](docs/typography-writing.md) | 한글 조판과 문장·레이아웃 검토 |
| [Visual critique](docs/visual-critique.md) | 실제 스크린샷 비평과 수정 검증 |
| [UX validation](docs/ux-validation.md) | 브라우저 과제와 관찰 가능한 성공 조건 |
| [Contributing](CONTRIBUTING.md) | 자료·코드 기여 및 필수 검사 |

### 자료 추가와 관리

`knowledge_ingest.py`는 PDF·Markdown·HTML·텍스트에서 **검토 후보**를 만듭니다. 출처의 원문 구간, 저작권, 해석 범위를 사람이 확인해야 하며 승인 전에는 공식 Knowledge로 등록되지 않습니다.

```bash
python scripts/knowledge_ingest.py --help
python scripts/knowledge_governance.py --help
python scripts/knowledge_graph.py impact source:N39
```

Gemini는 선택 사항입니다. `config.example.json`을 참고하고 `GEMINI_API_KEY`를 별도 설정한 뒤, 외부 전송에 명시적으로 동의한 경우에만 사용합니다. 기본 검색과 자동 검증에는 필요하지 않습니다.

## Development & checks

Python 3.10 이상을 권장합니다. 로컬 검색과 Knowledge 관련 테스트는 표준 라이브러리 위주로 동작합니다. 시각·브라우저 검사는 별도로 Playwright와 Chromium이 필요합니다. PDF 추출에는 `requirements-optional.txt`의 선택 의존성을 사용합니다.

```bash
python scripts/validate_install.py --root . --smoke
python scripts/knowledge_graph.py validate
python scripts/knowledge_health.py --json
python -m unittest discover -s tests -v
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-core.json
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-typography.json --top 5
python scripts/retrieval_evaluation.py --dataset benchmarks/retrieval-relevance.json
```

CI는 설치 구성, 지식 그래프, 전체 단위 테스트, 검색 회귀 및 합성 데이터 규모 테스트를 실행합니다. `tests/`와 `benchmarks/`의 데이터는 **작은 개발용 평가 집합**이며, 독립적인 사용자 연구나 논문 재현 실험이 아닙니다.

## Limits & principles

연구 출처 등록은 학술적 타당성의 자동 인증이 아닙니다. 공식 표준, 초안, 논문 초록, 디자이너 견해는 서로 다른 근거 수준으로 취급합니다. 스크린샷 점검은 미적 품질의 객관적 채점이 아니며, 브라우저 시나리오 통과는 실제 사용자 이해도 검증이 아닙니다. 저작권을 가진 이미지·서체, 개인 데이터, 비공개 고객 자료를 허가 없이 Knowledge에 추가하지 마세요.
