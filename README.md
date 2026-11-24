<p align="center">
  <img src="assets/model-routing-banner.png" alt="model-routing — 서브에이전트를 알맞은 모델로 보내는 플러그인" width="560">
</p>

<p align="center"><b>한국어</b> · <a href="README.en.md">English</a></p>

# model-routing

서브에이전트마다 작업 종류와 난이도에 맞는 모델과 추론강도를 골라 주는 Claude Code · Codex CLI 플러그인이에요.

서브에이전트를 쓰다 보니 파일 하나 찾는 일까지 제일 비싼 모델로 돌리고 있더라고요. 그래서 어떤 일에 어떤 모델이 맞는지
표로 정리하고, 그 표를 따르는 에이전트를 플러그인으로 묶었어요. 제 작업에서 매일 켜 두고 씁니다. 플러그인마다 자기 회사
모델만 쓰고, 난이도 기준과 위임 체크리스트, 승급 순서는 [`core/RULES.md`](core/RULES.md)에서 같이 써요.

| 등급 | 쓰는 곳 | Claude Code | Codex |
|---|---|---|---|
| T0 탐색 | 파일, 심볼, 설정, 로그 찾기 | `scout` haiku / low | `scout` terra / low |
| T1 읽기 | 파일, 로그, 붙여 넣은 문서, URL 하나에서 사실 뽑기 | `reader` haiku / high | `reader` terra / high |
| T2 범위 작업 | 메일·채팅·드라이브 조사, 테스트 있는 2-5개 파일 수정·리뷰 | `extractor`, `implementer`, `reviewer-lite` sonnet / medium | sol / medium |
| T3 어려움 | Hard: 원인 불명, 동시성, 모듈 경계, UI, 테스트 없음, 성능 | `implementer-hard`, `reviewer` opus / high | `implementer-hard`, `reviewer` sol / high |
| T4 최상 | Architecture, Critical (운영·하드웨어 제어, 보안, 데이터 손실, 릴리스) | 같은 에이전트, opus / xhigh | `implementer-xhigh`, `reviewer-xhigh` sol / xhigh |
| T5 승급 | 같은 작업에서 T4가 두 번 실패한 뒤에만 | `architect` / `critical` fable | `astra-hard` / `architect` astra |

할 수 있는 것:

- **작업에 맞는 모델 고르기** — 탐색은 가장 싼 모델, 범위가 정해진 수정은 중간 모델, 원인 불명이나 운영 경로는 강한 모델로
  보내요. 1-2개 파일짜리 쉬운 일은 위임하지 않고 메인 세션에서 끝내요.
- **위임 체크리스트** — 맡기기 전에 목표, 성공 기준, 비목표, 허용 파일, 돌려 볼 검사 명령을 정하고, 끝나면 diff와 검사를 직접
  확인해요. 검사 명령이 없으면 맡기지 않아요.
- **단계별 승급** — 실패하면 같은 워커에게 한 번 더 고치게 하고, 그다음 한 등급 위로, 가장 비싼 모델은 두 번 실패한 뒤에만 써요.
  `max`는 사용자가 이름으로 부를 때만 써요.
- **벤치마크 갱신** — `scripts/refresh.py`가 [Artificial Analysis](https://artificialanalysis.ai)에서 지능 지수, Terminal-Bench,
  환각률, 작업당 비용과 시간을 다시 가져와요.
- **실제 사용량 집계** — `scripts/usage.py`가 이 PC의 기록을 읽어서 서브에이전트가 어떤 모델과 추론강도로 몇 번 돌았는지 보여 줘요.

만들면서 신경 쓴 것도 몇 가지 있어요.

- 숫자는 다 AA 기준이에요. Claude Opus xhigh는 high보다 작업당 1.75배 비싸고($6.05 vs $3.47) Terminal-Bench는 0.03 높아요
  (0.596 vs 0.566). 그래서 xhigh는 Architecture와 Critical에만 써요.
- Codex sol은 xhigh가 high보다 Terminal-Bench가 오히려 낮아요(0.561 vs 0.586, 비용은 16% 더). 그래서 Hard는 sol high로 돌리고,
  xhigh는 Architecture·Critical 첫 시도에만 남겨 뒀어요. Hard가 막히면 xhigh를 건너뛰고 바로 astra로 올려요.
- 추출과 요약은 환각률이 낮은 쪽으로 보냈어요. Haiku high 0.389, Codex terra high 0.370이고, Opus는 0.64~0.67이에요.
- Critical은 "변경이 하드웨어나 운영에 닿는 것"만이에요. 로봇 저장소 안이라도 로컬 벤치마크, 프로파일링, 읽기 전용 측정,
  UI 스타일 작업은 Hard로 둬요. 저장소 이름만 보고 다 Critical로 올리는 일을 막으려고 넣었어요.
- Codex 사용량은 rollout 파일이 아니라 `state_<n>.sqlite`에서 읽어요. 지금 Codex는 서브에이전트 기록을 DB에 두기 때문에,
  파일만 읽으면 329건 중 1건만 잡혔어요.

## 구성

| 경로 | 내용 |
|---|---|
| `core/` | 공통 규칙, AA 수집 코드 `aa.py`, 그걸 각 플러그인에 복사하는 `sync.py` |
| `claude/` | Claude Code 플러그인: 스킬, 에이전트 12개, `routing/routing.json` |
| `codex/` | Codex 플러그인: 스킬, 역할 파일 11개 + `install.sh`, `routing/gpt_rows.json` |

`core`, `claude`, `codex` 브랜치에 각 부분의 기록이 있고, `main`이 이걸 합쳐요.

## Claude Code

| 에이전트 | 모델 | 추론강도 | 쓰는 곳 |
|---|---|---|---|
| `scout` | haiku | low | 파일, 심볼, 호출처, 설정값, 로그 찾기 (읽기 전용) |
| `classifier` | haiku | medium | 짧은 항목 여러 개 분류, 태깅, 필드 추출 |
| `reader` | haiku | high | 파일, 로그, 붙여 넣은 문서, URL 하나에서 사실이나 요약 |
| `extractor` | sonnet | medium | 메일, 채팅, 드라이브, 여러 웹 페이지 조사 (읽기 전용) |
| `implementer` | sonnet | medium | Standard 수정: 2-5개 파일, 명확한 스펙, 테스트 |
| `reviewer-lite` | sonnet | medium | Standard 리뷰, 수정 없음 |
| `writer` | sonnet | high | 문서, 슬라이드, 스프레드시트, 보고서 |
| `implementer-hard` | opus | high (Architecture / Critical은 xhigh) | Hard 수정: 원인 불명, 동시성, 모듈 경계, UI, 테스트 없음, 성능 |
| `reviewer` | opus | high (Architecture / Critical은 xhigh) | Hard 리뷰, 감사, 버그 찾기, 수정 없음 |
| `vision` | opus | medium | 브라우저, 컴퓨터 사용, 스크린샷·이미지가 많은 작업 |
| `architect` | fable | medium | Architecture 승급, Opus xhigh가 두 번 실패한 뒤에만 |
| `critical` | fable | high | Critical 승급, Opus xhigh가 두 번 실패한 뒤에만 |
| 메인 세션 | opus | medium | 1-2개 파일 쉬운 수정, 계획, 최종 확인 |

## Codex CLI

| 역할 | 모델 | 추론강도 | 샌드박스 | 쓰는 곳 |
|---|---|---|---|---|
| `scout` | gpt-6.1-terra | low | read-only | 파일, 심볼, 호출처, 설정 찾기 |
| `reader` | gpt-6.1-terra | high | read-only | 가진 텍스트에서 사실이나 요약 |
| `extractor` | gpt-6.2-sol | medium | read-only | 메일, 채팅, 드라이브, 여러 웹 페이지 조사 |
| `implementer` | gpt-6.2-sol | medium | workspace-write | Standard 수정: 2-5개 파일, 명확한 스펙, 테스트 |
| `reviewer-lite` | gpt-6.2-sol | medium | read-only | Standard 리뷰, 수정 없음 |
| `implementer-hard` | gpt-6.2-sol | high | workspace-write | Hard 수정 (첫 시도) |
| `reviewer` | gpt-6.2-sol | high | read-only | Hard 리뷰 (첫 시도) |
| `implementer-xhigh` | gpt-6.2-sol | xhigh | workspace-write | Architecture, Critical 수정 (첫 시도) |
| `reviewer-xhigh` | gpt-6.2-sol | xhigh | read-only | Architecture, Critical 리뷰 (첫 시도) |
| `astra-hard` | gpt-6.2-astra | high | workspace-write | Hard 승급, sol high가 두 번 실패한 뒤에만 |
| `architect` | gpt-6.2-astra | xhigh | workspace-write | Architecture, Critical 승급, sol xhigh가 두 번 실패한 뒤에만 |
| 메인 세션 | gpt-6.2-sol | medium | - | 1-2개 파일 쉬운 수정, 계획, 최종 확인 |

## 설치

Claude Code:

```
/plugin marketplace add lsy041015/model-routing
/plugin install model-routing@model-routing
```

에이전트 이름은 `model-routing:<agent>`예요(예: `model-routing:scout`). Claude Code v2.1.293 이상이 필요해요.
플러그인이 대신 못 해 주는 설정도 있어요.

- 내장 `general-purpose`와 `Plan`은 메인 모델을 그대로 써요. `~/.claude/settings.json`에서 싸게 바꿔 두세요:
  `{ "env": { "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet" } }`
- 내장 `Explore`를 Haiku로 돌리려면 [`claude/extras/Explore.md`](claude/extras/Explore.md)를 `~/.claude/agents/Explore.md`로 복사하세요.
- Fable을 못 쓰면 `architect`와 `critical`에서 `model: fable`을 `model: opus`로, `effort`를 `xhigh`로 바꾸세요.
- 규칙을 항상 켜 두려면 `~/.claude/CLAUDE.md`에 `Before any Agent call, follow the model-routing skill.` 한 줄을 넣으세요.

Codex CLI:

```
codex plugin marketplace add lsy041015/model-routing
codex plugin add model-routing@model-routing
sh codex/install.sh        # 클론한 폴더에서: 역할 파일을 ~/.codex/agents로 복사
```

Codex 플러그인은 서브에이전트를 등록할 수 없어서, `install.sh`가 `codex/agents/*.toml`을 `$CODEX_HOME/agents`로 복사해요.
이미 있는 파일은 `--force`를 줄 때만 덮어써요. `config.toml`에 넣을 `[agents]` 블록은 화면에 출력만 하고, `config.toml`은
직접 고치지 않아요. 메인 세션은 `gpt-6.2-sol` medium을 추천해요. 규칙을 항상 켜 두려면 `~/.codex/AGENTS.md`에
`Before spawning a subagent, follow the model-routing skill.` 한 줄을 넣으세요.

## 측정

```
python3 -I claude/scripts/usage.py 2026-11-01 [CUTOFF]   # ~/.claude/projects
python3 -I codex/scripts/usage.py 2026-11-01 [CUTOFF]    # ~/.codex/state_<n>.sqlite
python3 -I <plugin>/scripts/refresh.py --dry-run         # AA 숫자 다시 받기
```

`CUTOFF`를 주면 규칙을 바꾸기 전과 후로 나눠서 보여 줘요. Claude는 출력 토큰, Codex는 Codex가 기록한 입력+출력 합계를 세요.

## 아쉬운 점

- AA 숫자는 API 가격과 공개 벤치마크라서 제 작업과 똑같지는 않아요. 자주 하는 일이라면 결과를 확인할 수 있는 실제 작업 몇 개를
  두 모델로 돌려 보고 점수와 비용을 비교하는 게 정확해요.
- `writer`와 `vision`은 AA에 맞는 벤치마크(문서 작성, 컴퓨터 사용)가 없어서 숫자로 검증하지 못했어요.
- `extractor`는 커넥터 쓰기 도구를 CLI 이름(`mcp__claude_ai_Gmail__send_message` 등)으로 막아요. 커넥터를 id로 부르는
  앱에서는 지침으로만 막혀요.
- AA는 API가 없어서 웹 페이지에 든 데이터를 읽어요. 페이지 구조가 바뀌면 `refresh.py`가 "no records found"로 멈춰요. 틀린 숫자를 쓰지는 않아요.

MIT 라이선스.
