# Design Engineering — Knowledge → Design → Critique

Codex용 범용 디자인공학 Skill. 논문·학술 연구·디자이너의 문제 해결 방식에서 **판단 근거**를 찾고, 실제 UI 제작과 시각적 비평·사용자 과제 검증을 연결합니다. 특정 홈페이지, 대시보드, 관리자 화면을 정해진 스타일로 만드는 템플릿이 아닙니다.

**v3.8 주요 변화:** 검색 실패 개선, 출처·주장 단위 검증, 설계 결정 추적, 실제 스크린샷 비평과 재검증, 의미 중심 콘셉트 탐색, 브라우저 과제 시나리오 테스트. 연구 카드 수를 늘리지 않고 이미 존재하는 지식을 제대로 적용하는 데 집중했습니다.

## 설치

이 폴더를 `.agents/skills/design-engineering/`에 설치하거나 GitHub 저장소를 해당 위치에 복제합니다. `SKILL.md`는 항상 현재 실행 절차만 설명하며 버전 이력은 Git 커밋/릴리스에서 관리합니다.

```bash
mkdir -p .agents/skills
git clone <YOUR_REPO_URL> .agents/skills/design-engineering
```


## Claude Code 플러그인 설치

Claude Code에서 이 저장소를 마켓플레이스로 등록한 뒤 스킬을 설치할 수 있습니다.

```bash
claude plugin marketplace add ByeonDoHyeon06/design-engineering
claude plugin install design-engineering@design-engineering-marketplace
```

**중요:** Claude Code에서 플러그인을 설치해야 `knowledge/`, `scripts/`, `methods/`, `templates/` 등이 함께 제공됩니다. `skills/design-engineering/SKILL.md` 파일만 복사하거나 별도의 단일 스킬 가져오기 방식으로 설치하면 연구 검색 도구는 포함되지 않습니다. 이번 구성은 정식 `.claude-plugin/plugin.json`을 이용하는 전체 저장소 플러그인입니다.

기존 설치를 갱신하려면 Claude Code에서 아래 순서로 실행하세요.

```text
/plugin marketplace update design-engineering-marketplace
/plugin uninstall design-engineering@design-engineering-marketplace
/plugin install design-engineering@design-engineering-marketplace
```

설치 후 Claude에게 **설치된 플러그인 루트**에서 `SKILL.md`, `scripts/knowledge_index.py`, `knowledge/catalog.json`, `methods/`, `templates/`의 존재 여부를 확인하게 하고, 다음 명령을 실행하게 하세요.

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/knowledge_index.py" rebuild
python "${CLAUDE_PLUGIN_ROOT}/scripts/knowledge_index.py" search '행사 홈페이지에서 정보를 명확하게 전달하는 방법' --top 5 --json
```

일부 파일이 누락되면 설치 완료로 보지 말고 `/doctor`와 실제 플러그인 설치 경로를 확인하세요. 설치 방법(마켓플레이스 플러그인인지 단일 스킬 가져오기인지)에 따라 결과가 다를 수 있습니다.

Claude Code 세션에서는 `/design-engineering:design-engineering`으로 호출하거나 디자인 작업에 스킬 사용을 요청하세요. 기존 루트 `SKILL.md`가 공통 원본이며, `skills/design-engineering/SKILL.md`는 Claude Code용 진입점입니다. 설치 후 `claude plugin list`와 `claude plugin details design-engineering`으로 로딩 상태를 확인할 수 있습니다. 저장소에서 `claude plugin validate .`를 실행해 마켓플레이스를 검증할 수 있습니다. Claude Code CLI에서 실제 설치/검증 실행은 별도로 필요합니다.

## 빠른 시작

아래 명령들은 Skill 루트에서 실행합니다. 로컬 경로에서는 **외부 통신·API 키가 필요 없습니다.**

```bash
python scripts/knowledge_index.py rebuild
python scripts/knowledge_index.py search '행사 홈페이지에서 정보를 명확하게 전달하는 방법' --top 5 --json
python scripts/knowledge_index.py search '데이터 차트 비교 정확도' --verified-only --top 5
python scripts/retrieval_benchmark.py
```

결과의 `verified_claims`는 학술 연구 또는 표준의 **확인 범위**이지, 현 프로젝트에서 그 디자인을 썼을 때 효과가 입증된 것은 아닙니다. `--verified-only`는 카드 이름이 아닌 검증된 주장 ID 연결을 검사합니다.

### 디자인 의사결정 및 반복 검토

```bash
python scripts/decision_trace.py new /tmp/design-decisions.json --goal '행사 내용을 이해하고 프로그램을 찾도록 설계'
# 실제 문제·선택·근거·구현·검증 결과를 채워 넣고
python scripts/decision_trace.py validate /tmp/design-decisions.json

python scripts/visual_critique.py start path/to/page.html --out /tmp/visual-qa
# 이미지 실제 열람 후 /tmp/visual-qa/critique.json에 관찰·수정·재확인을 기록
python scripts/visual_critique.py validate /tmp/visual-qa/critique.json

python scripts/ux_scenarios.py validate my-tasks.json
python scripts/ux_scenarios.py run path/to/page.html my-tasks.json --out /tmp/ux-check --width 390
```

`Visual Critique`는 예쁨을 자동 점수화하지 않습니다. UI에 대한 시각적 판단은 화면을 직접 관찰한 뒤 기록해야 하며, **클릭·폼 테스트가 정상이어도 실제 방문자가 내용을 이해했다고 주장할 수는 없습니다.** 시나리오는 사용자의 목적에 맞게 직접 작성합니다.

### 의미 기반 검색의 정확한 범위

로컬 기본 검색은 **한영 설계 개념 확장 + SQLite FTS5 + 문자 유사도**입니다. 기존의 키워드 검색보다 자연어 변화에 견딜 수 있지만 완전한 의미 이해나 학술 주장 검증을 수행하지 않습니다. 기존 모델을 로컬에 갖고 있다면 선택형 문장 임베딩 재정렬도 가능합니다.

```bash
# 선택 사항; 별도 준비한 로컬 모델만 허용하며 다운로드하지 않음
python -m pip install sentence-transformers
python scripts/knowledge_index.py search '복잡한 관리자 화면의 정보 위계' \
  --embedding-model /LOCAL/MODEL/DIRECTORY --top 5
```

### Gemini (선택)

사용할 때만 `config.example.json`을 `config.json`으로 복사해 `gemini.mode = ask`, OS 환경변수 `GEMINI_API_KEY`를 설정합니다. 질문과 제한된 로컬 카드 메타데이터를 외부로 보내는 데 명시적 동의가 필요합니다.

```bash
python scripts/knowledge_research.py '특정 사용자 과제에서 필요한 근거' \
  --provider gemini --approve-external --json
```

API 키가 없어도 전체 로컬 검색과 QA 도구는 작동합니다. Gemini 실서비스 호출은 **이 패키지의 자동 테스트에서 인증되지 않았습니다**. 모델이 제안한 출처 ID는 로컬 등록 데이터와 대조합니다.

### 자료 등록

`knowledge/README.md`와 `knowledge/VERIFICATION-POLICY.md` 참조. PDF/Markdown/HTML/TXT를 검토 대기열에 준비한 뒤 출처·인용·페이지를 확인한 후보만 승인합니다. 불특정 AI 추측은 승인 자료가 아닙니다.

## 구조

```text
design-engineering/
├── SKILL.md                 # 짧은 실행 지침
├── knowledge/
│   ├── catalog.json         # 지식 카드 메타데이터
│   ├── concepts.json        # 범용 설계 개념 및 동의어(스타일 처방 아님)
│   ├── verified/claims.json # 연구 주장 및 적용 범위
│   ├── sources.json         # 출처·검토 수준
│   └── cards/               # 연구·방법론 38개 카드
├── scripts/
│   ├── knowledge_index.py   # 혼합 로컬 검색
│   ├── query_understanding.py
│   ├── knowledge_research.py
│   ├── knowledge_ingest.py
│   ├── decision_trace.py
│   ├── concept_exploration.py
│   ├── visual_critique.py
│   └── ux_scenarios.py
├── docs/                    # 시각 비평·사용자 과제 운영
├── templates/               # 중간 판단 기록 (UI 출력 아님)
└── benchmarks/              # 연구용 회귀 질의
```

개발용 GitHub 저장소에는 `tests/`, `.github/workflows/validate.yml`, `CONTRIBUTING.md`가 추가로 포함됩니다. 설치용 ZIP은 개발 파일을 제외한 배포본으로 제공합니다.

## 검증 한계

지식 검색 20문항의 재현용 회귀셋 결과는 제작한 소규모 도메인 질의에 대한 **회귀 테스트**로, 새로운 사용자 질의나 모델 전반으로 일반화할 수 없습니다. 브라우저 QA는 실제 Playwright/Chromium으로 실행할 수 있으나 시각적 취향, WCAG 전체, 스크린리더나 실제 사용자 테스트를 인증하지 않습니다.
