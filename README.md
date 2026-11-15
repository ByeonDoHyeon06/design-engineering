<div align="center">

# Design Engineering

**From evidence to intentional design.**

디자인의 근거를 탐색하고, 맥락에 맞게 설계하고, 실제 결과로 검증하는  
**Codex · Claude Code 공통 디자인 엔지니어링 스킬**

<p>
  <a href="#overview">Overview</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#getting-started">Getting started</a> ·
  <a href="#documentation">Documentation</a>
</p>

</div>

---

## Overview

**Design Engineering**은 AI가 더 신중하게 디자인하도록 돕는 에이전트 스킬입니다. 논문과 표준, 디자이너의 방법론에서 필요한 지식을 찾고, 콘텐츠와 사용자의 목적에 맞는 화면을 설계한 뒤, 실제 렌더링과 동작을 검토하는 과정을 하나의 워크플로로 연결합니다.

특정한 디자인 스타일이나 컴포넌트 라이브러리를 강제하지 않습니다. **무엇을 만들 것인가**뿐 아니라 **왜 그렇게 만들었고, 실제로 효과가 있었는가**를 함께 다룹니다.

<table>
  <tr>
    <td width="50%" valign="top">
      <p><strong>◈ &nbsp; Research-informed</strong></p>
      <p>논문·공식 표준·실무 견해를 필요한 순간에 검색합니다. 출처의 검증 범위와 설계 가설을 구분합니다.</p>
    </td>
    <td width="50%" valign="top">
      <p><strong>◇ &nbsp; Context-driven</strong></p>
      <p>브랜드, 실제 콘텐츠, 사용자 목표에 맞춰 정보 구조와 시각적 표현을 결정합니다.</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <p><strong>↗ &nbsp; Inspect &amp; refine</strong></p>
      <p>브라우저 스크린샷과 사용자 과제 시나리오로 결과를 확인하고 개선 과정을 추적합니다.</p>
    </td>
    <td valign="top">
      <p><strong>◎ &nbsp; Your design knowledge</strong></p>
      <p>사람과 AI가 디자인 선호·원칙·관찰을 등록하고 활용합니다. 개인 정보와 공통 연구 자료는 분리합니다.</p>
    </td>
  </tr>
</table>

## How it works

```text
Understand → Research → Explore → Build → Validate → Refine
```

디자인 과제를 정의한 뒤 관련 근거와 프로젝트별 선호를 확인합니다. 여러 방향을 탐색하고 실제 결과물을 구현한 다음, 화면과 상호작용을 검사해 개선합니다.

공통 Knowledge는 **출처·주장·개념·설계 방법**을 연결하며, 개인 취향은 **사용자·프로젝트·세션** 범위로 별도 관리합니다. AI가 만든 제안도 검토와 승인을 거치기 전에는 자동으로 공통 연구 근거가 되지 않습니다.

## Getting started

전체 저장소가 필요합니다. `SKILL.md`만 복사하면 Knowledge와 검사 도구를 사용할 수 없습니다.

### Claude Code

Claude Code에서 마켓플레이스를 등록하고 설치합니다.

```text
/plugin marketplace add ByeonDoHyeon06/design-engineering
/plugin install design-engineering@design-engineering-marketplace
```

### Codex

프로젝트의 스킬 디렉터리에 저장소를 설치합니다.

```bash
mkdir -p .agents/skills
git clone https://github.com/ByeonDoHyeon06/design-engineering.git .agents/skills/design-engineering
```

### Unified CLI

전체 저장소에서 CLI를 설치할 수 있습니다.

```bash
python -m pip install -e .
de search "한글과 영문이 섞인 타이포그래피"
de check
```

플러그인 폴더를 수정하기 어려운 환경에서는 설치 없이 `python /path/to/design-engineering/scripts/de.py`를 사용할 수 있습니다. 자세한 환경별 사용법은 [CLI & personal Knowledge](docs/personal-knowledge.md)를 참고하세요.

<details>
<summary><strong>자연어로 나만의 디자인 방향성 등록하기</strong></summary>

<p>아래 명령은 즉시 저장하지 않고 검토용 초안을 생성합니다.</p>

```bash
de add "정교한 사각형과 명확한 타이포그래피를 선호해" --scope project
de review --list
de review <proposal-path> --approve --reviewer owner
de context
```

<p>개인 취향은 연구 결과로 취급하지 않으며, 명시적인 승인 없이 영구 적용하지 않습니다.</p>

</details>

## Documentation

| Guide | Description |
| :--- | :--- |
| [Architecture](docs/architecture.md) | 시스템 구성, 검색과 지식 관계 모델 |
| [CLI & Personal Knowledge](docs/personal-knowledge.md) | CLI 사용법, 사용자별 지식 등록과 저장 범위 |
| [Knowledge management](docs/knowledge-management.md) | 자료 등록·검토·중복 관리와 출처 추적 |
| [Evidence policy](knowledge/VERIFICATION-POLICY.md) | 근거 수준과 검증 범위의 구분 |
| [Typography & Writing](docs/typography-writing.md) | 한글 조판, 문장 품질, 콘텐츠 배치 |
| [Visual critique](docs/visual-critique.md) · [UX validation](docs/ux-validation.md) | 실제 화면과 동작을 검토하는 방법 |
| [Contributing](CONTRIBUTING.md) | 기여 절차와 검증 기준 |

<details>
<summary><strong>Repository structure</strong></summary>

```text
SKILL.md                Shared agent instructions
design_engineering/      Unified CLI and personal Knowledge
knowledge/               Research cards, sources, claims and governance
methods/                 Practitioner methods
scripts/                 Retrieval, inspection and validation tools
templates/               Review and workflow templates
docs/                    Guides and architecture
tests/ · benchmarks/     Regression and quality checks
.claude-plugin/ · agents/ Agent integration metadata
```

</details>

## Contributing

버그 수정, Knowledge 품질 개선, 접근성·검증 도구 개선, 문서화 기여를 환영합니다. 새로운 지식을 추가하기 전에 기존 자료와 중복되지 않는지 확인하고, 주장과 출처의 검토 범위를 명시해 주세요. 자세한 기준은 [Contribution guide](CONTRIBUTING.md)에 있습니다.

<sub>Design Engineering은 연구의 자동 인증기나 특정 미적 스타일을 강제하는 도구가 아닙니다. 검색 결과는 설계 판단을 돕는 자료이며, 실제 제품에서의 유용성과 사용성은 별도로 검증해야 합니다.</sub>
