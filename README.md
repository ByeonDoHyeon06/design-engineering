# Design Engineering — Knowledge → Design → Critique

Codex·Claude Code 등 다양한 에이전트에서 사용할 수 있는 범용 디자인공학 Skill. 논문·학술 연구·디자이너의 문제 해결 방식에서 **판단 근거**를 찾고, 실제 UI 제작과 시각적 비평·사용자 과제 검증을 연결합니다. 특정 홈페이지, 대시보드, 관리자 화면을 정해진 스타일로 만드는 템플릿이 아닙니다.

**v3.9:** 실제 한글 조판·타이포그래피(K16), 자연스러운 한국어 UX Writing(K17), 콘텐츠와 레이아웃 통합 설계(K18)를 공통 스킬에 연결했습니다. W3C 초안과 GOV.UK 실무 지침은 각각 원문 지위와 전이 한계를 구분하며, 새로운 경험적 효과가 입증됐다고 주장하지 않습니다. `docs/type-language-content-review.md`에 적용·검토 절차가 있습니다.

**v3.8 주요 변화:** 검색 실패 개선, 출처·주장 단위 검증, 설계 결정 추적, 실제 스크린샷 비평과 재검증, 의미 중심 콘셉트 탐색, 브라우저 과제 시나리오 테스트. 연구 카드 수를 늘리지 않고 이미 존재하는 지식을 제대로 적용하는 데 집중했습니다.

## 설치 (공통 Skill 원본)

실행 지침은 저장소 루트의 `SKILL.md` **하나뿐**입니다. `knowledge/`, `scripts/`, `methods/`, `templates/` 등 모든 경로는 이 스킬 루트를 기준으로 합니다. 단일 `SKILL.md`만 복사하면 연구 검색과 검증 기능을 사용할 수 없으므로 **저장소 전체를 설치**하세요.

### Codex

```bash
mkdir -p .agents/skills
git clone https://github.com/ByeonDoHyeon06/design-engineering.git .agents/skills/design-engineering
```

### Claude Code (마켓플레이스)

```text
/plugin marketplace add ByeonDoHyeon06/design-engineering
/plugin install design-engineering@design-engineering-marketplace
```

**Claude Code 구성:** `.claude-plugin/plugin.json`에서 `"skills": ["."]`로 루트 `SKILL.md`를 명시합니다. 마켓플레이스는 전체 저장소를 `source: "./"`로 참조하며, 별도 Claude용 스킬 복제본은 없습니다. 이 설정은 Claude Code 플러그인용이며, Codex는 기존 저장소 설치를 그대로 사용합니다.

**이전 설치가 1,243바이트 단독 SKILL.md를 표시하는 경우:** 현재 정식 루트 파일과 다른 구버전/단독 스킬입니다. 먼저 Claude에게 실제로 읽은 **절대 경로**를 보고하도록 하세요. `~/.claude/skills/design-engineering/`처럼 직접 복사한 위치와 `~/.claude/plugins/cache/`에 있는 플러그인 설치는 다릅니다. 파일이 하나뿐인 경로를 플러그인 루트로 착각하지 마세요. 정확한 설치 유형을 확인한 다음 오래된 중복 스킬 등록을 비활성화하거나 제거해야 합니다. 다른 파일을 무차별 삭제하지 마세요.

설치 갱신은 Claude Code 안에서 `/plugin marketplace update design-engineering-marketplace`를 실행하고 설치된 플러그인을 업데이트하거나 제거 후 재설치하세요. 새 세션에서 `/plugin`의 Installed 탭 또는 `claude plugin list`로 **플러그인 이름·버전·상태**를 확인하세요. 마켓플레이스 갱신만으로 설치된 플러그인이 갱신됐다고 가정하지 마세요.

### 공통 설치 검증

**설치된 스킬 루트**에서 실행하세요. Claude Code에서는 설치된 플러그인/스킬이 실제로 어디에 있는지 먼저 확인해야 하며, 현재 작업 프로젝트 디렉터리에서 실행해서는 안 됩니다.

```bash
test -f SKILL.md
test -f scripts/knowledge_index.py
test -f knowledge/catalog.json
test -d methods
test -d templates
python scripts/knowledge_index.py rebuild
python scripts/knowledge_index.py search '행사 홈페이지 정보를 명확히 전달하는 방법' --top 5 --json
python scripts/validate_install.py --root . --smoke
```

실행에 필요한 자료가 누락되면 Knowledge 검색을 수행한 것으로 취급하지 않습니다. 스킬의 기능과 실제 설치 환경의 검증 결과를 구분해서 보고하세요.

Claude Code에서 검증할 때는 다음을 그대로 요청하는 것이 좋습니다.

> 지금 사용 중인 design-engineering 스킬 파일의 **절대 경로, 실제 바이트 크기, 파일 내용의 첫 제목**을 출력하고, `claude plugin list`에서 설치된 플러그인 상태와 경로를 확인하세요. 검사 대상이 개별 스킬 폴더인지 전체 플러그인 루트인지 구분하세요. **플러그인 루트**에 있는 `scripts/validate_install.py`를 `--root <plugin-root> --smoke`로 실행하고 결과와 오류를 보고하세요. 새 파일을 임의로 설치하거나 잘못된 연구 인용을 생성하지 마세요.

마켓플레이스 설치가 계속 실패할 때는 로컬에서 저장소 전체를 클론하여 `claude --plugin-dir /absolute/path/to/design-engineering` 방식으로 별도로 테스트할 수 있습니다. 이렇게 하면 마켓플레이스 캐시 문제와 플러그인 자체 문제를 분리할 수 있습니다. `claude plugin validate .`로 플러그인/마켓플레이스 메타데이터도 확인하세요.

## 빠른 시작

아래 명령들은 Skill 루트에서 실행합니다. 로컬 경로에서는 **외부 통신·API 키가 필요 없습니다.**

```bash
python scripts/knowledge_index.py rebuild
python scripts/knowledge_index.py search '행사 홈페이지에서 정보를 명확하게 전달하는 방법' --top 5 --json
python scripts/knowledge_index.py search '데이터 차트 비교 정확도' --verified-only --top 5
python scripts/retrieval_benchmark.py
python scripts/retrieval_benchmark.py --dataset benchmarks/retrieval-v39.json --top 5
python -m unittest discover -s tests -p 'test_v39.py'
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
│   └── cards/               # 연구·방법론 카드 (v3.9에서 3개 추가)
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
