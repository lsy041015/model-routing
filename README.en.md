<p align="center">
  <img src="assets/model-routing-banner.png" alt="model-routing — subagents routed to the right model" width="560">
</p>

<p align="center"><a href="README.md">한국어</a> · <b>English</b></p>

# model-routing

A Claude Code and Codex CLI plugin that sends each subagent to the model and reasoning effort its task actually needs.

I kept catching my subagents doing easy lookups on the most expensive model, so I wrote down which model each kind of task
should get and packaged that table, plus the agents that follow it, as a plugin. I run it every day. Each plugin routes only to
its own vendor's models; the difficulty scale, delegation checklist and escalation order are shared in [`core/RULES.md`](core/RULES.md).

| Tier | Used for | Claude Code | Codex |
|---|---|---|---|
| T0 lookup | find files, symbols, config, log lines | `scout` haiku / low | `scout` terra / low |
| T1 read | facts from files, logs, pasted docs, one URL | `reader` haiku / high | `reader` terra / high |
| T2 scoped | mail/chat/drive facts; 2-5 file change or review with tests | `extractor`, `implementer`, `reviewer-lite` sonnet / medium | sol / medium |
| T3 strong | Hard: unknown cause, concurrency, cross-module, UI, no tests, performance | `implementer-hard`, `reviewer` opus / high | `implementer-hard`, `reviewer` sol / high |
| T4 strong-max | Architecture and Critical (production or hardware control, security, data loss, release) | same agents, opus / xhigh | `implementer-xhigh`, `reviewer-xhigh` sol / xhigh |
| T5 escalation | only after T4 failed twice on the same task | `architect` / `critical` fable | `astra-hard` / `architect` astra |

What it does:

- **Pick the model for the task** — lookups go to the cheapest model, scoped changes to the middle one, unknown causes and
  production paths to the strong one. Easy 1-2 file changes are not delegated; the main session just does them.
- **Delegation checklist** — before handing work off: goal, success criteria, non-goals, allowed files and a check command to run.
  Afterwards: read the diff and run the checks yourself. No check command, no delegation.
- **Step-by-step escalation** — a failed worker gets one fix round, then the task moves up one tier, and the most expensive model
  only comes in after two failures. `max` only when the user asks for it by name.
- **Benchmark refresh** — `scripts/refresh.py` re-pulls Intelligence Index, Terminal-Bench, hallucination rate, and cost and time per
  task from [Artificial Analysis](https://artificialanalysis.ai).
- **Real usage** — `scripts/usage.py` reads this machine's logs and shows which model and effort your subagents actually ran on, and
  how often.

A few things I paid attention to:

- Every number is from AA. Claude Opus xhigh costs 1.75x high per task ($6.05 vs $3.47) for +0.03 Terminal-Bench (0.596 vs 0.566),
  so xhigh is kept for Architecture and Critical work.
- On Codex, sol xhigh scores *lower* than sol high on Terminal-Bench (0.561 vs 0.586) for 16% more cost. Hard work runs on sol high,
  xhigh is only the first try for Architecture and Critical, and a stuck Hard task skips xhigh and goes straight to astra.
- Extraction and summaries go where hallucination is low: Haiku high 0.389, Codex terra high 0.370, versus 0.64-0.67 for Opus.
- "Critical" means the change itself reaches hardware or production. Inside a robot repo, local benchmarks, profiling, read-only
  measurement and UI styling still stay Hard. That line is there so a repo's name alone doesn't push everything up to the top tier.
- Codex usage is read from `state_<n>.sqlite`, not rollout files. Codex now keeps subagent records in that DB; reading only the
  files found 1 of 329 runs.

## Layout

| Path | What |
|---|---|
| `core/` | shared rules, the AA scraper `aa.py`, `sync.py` that copies it into each plugin |
| `claude/` | Claude Code plugin: skill, 12 agents, `routing/routing.json` |
| `codex/` | Codex plugin: skill, 11 role files + `install.sh`, `routing/gpt_rows.json` |

Branches `core`, `claude` and `codex` hold each part's history; `main` merges them.

## Claude Code

| Agent | Model | Effort | Use for |
|---|---|---|---|
| `scout` | haiku | low | find files, symbols, call sites, config values, log lines (read-only) |
| `classifier` | haiku | medium | classify, tag, route or extract fields from many short items |
| `reader` | haiku | high | facts or a summary from files, logs, pasted docs, one known URL |
| `extractor` | sonnet | medium | facts via mail, chat, drive or many web pages; repeated investigation (read-only) |
| `implementer` | sonnet | medium | Standard change: 2-5 files, clear spec, tests |
| `reviewer-lite` | sonnet | medium | Standard review, no edits |
| `writer` | sonnet | high | documents, slides, spreadsheets, reports |
| `implementer-hard` | opus | high (xhigh for Architecture / Critical) | Hard change: unknown cause, concurrency, cross-module, UI, no tests, performance |
| `reviewer` | opus | high (xhigh for Architecture / Critical) | Hard review, audit or bug hunt, no edits |
| `vision` | opus | medium | browser, computer use, screenshot- or image-heavy loops |
| `architect` | fable | medium | Architecture escalation, only after Opus xhigh failed twice |
| `critical` | fable | high | Critical escalation, only after Opus xhigh failed twice |
| main session | opus | medium | Easy 1-2 file changes, planning, final verification |

## Codex CLI

| Role | Model | Reasoning effort | Sandbox | Use for |
|---|---|---|---|---|
| `scout` | gpt-6.1-terra | low | read-only | find files, symbols, call sites, config |
| `reader` | gpt-6.1-terra | high | read-only | facts or a summary from text at hand |
| `extractor` | gpt-6.2-sol | medium | read-only | facts via mail, chat, drive or many web pages |
| `implementer` | gpt-6.2-sol | medium | workspace-write | Standard change: 2-5 files, clear spec, tests |
| `reviewer-lite` | gpt-6.2-sol | medium | read-only | Standard review, no edits |
| `implementer-hard` | gpt-6.2-sol | high | workspace-write | Hard change (first try) |
| `reviewer` | gpt-6.2-sol | high | read-only | Hard review (first try) |
| `implementer-xhigh` | gpt-6.2-sol | xhigh | workspace-write | Architecture or Critical change (first try) |
| `reviewer-xhigh` | gpt-6.2-sol | xhigh | read-only | Architecture or Critical review (first try) |
| `astra-hard` | gpt-6.2-astra | high | workspace-write | Hard escalation, only after sol high failed twice |
| `architect` | gpt-6.2-astra | xhigh | workspace-write | Architecture or Critical escalation, only after sol xhigh failed twice |
| main session | gpt-6.2-sol | medium | - | Easy 1-2 file changes, planning, final verification |

## Install

Claude Code:

```
/plugin marketplace add lsy041015/model-routing
/plugin install model-routing@model-routing
```

Agents are named `model-routing:<agent>`, e.g. `model-routing:scout`. Needs Claude Code v2.1.293 or later. A few things the plugin
can't set for you:

- Built-in `general-purpose` and `Plan` inherit your main model. Make them cheaper in `~/.claude/settings.json`:
  `{ "env": { "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet" } }`
- To run the built-in `Explore` on Haiku, copy [`claude/extras/Explore.md`](claude/extras/Explore.md) to `~/.claude/agents/Explore.md`.
- No Fable access? In `architect` and `critical`, change `model: fable` to `model: opus` and set `effort: xhigh`.
- Rules always on: add `Before any Agent call, follow the model-routing skill.` to `~/.claude/CLAUDE.md`.

Codex CLI:

```
codex plugin marketplace add lsy041015/model-routing
codex plugin add model-routing@model-routing
sh codex/install.sh        # from a clone: copies the role files into ~/.codex/agents
```

A Codex plugin can't register subagents, so `install.sh` copies `codex/agents/*.toml` into `$CODEX_HOME/agents` (existing files
are kept unless `--force`) and prints the `[agents]` block for `config.toml`; it never edits `config.toml`. Recommended main
session: `gpt-6.2-sol` at medium. Rules always on: add `Before spawning a subagent, follow the model-routing skill.` to
`~/.codex/AGENTS.md`.

## Measuring

```
python3 -I claude/scripts/usage.py 2026-11-01 [CUTOFF]   # ~/.claude/projects
python3 -I codex/scripts/usage.py 2026-11-01 [CUTOFF]    # ~/.codex/state_<n>.sqlite
python3 -I <plugin>/scripts/refresh.py --dry-run         # re-pull AA numbers
```

With `CUTOFF`, counts are split into before and after (say, a rule change). Claude counts output tokens; Codex counts the input +
output total Codex records.

## Rough edges

- AA numbers are API prices and public benchmarks, not your workload. For recurring work, run a few real tasks with an outcome check
  on two models and compare score against spend.
- `writer` and `vision` have no matching AA benchmark (document writing, computer use), so they aren't backed by numbers.
- `extractor` blocks connector write tools by their CLI names (`mcp__claude_ai_Gmail__send_message`, ...). Apps that name connectors
  by id are covered only by its instructions.
- AA has no API, only page data. If the page format changes, `refresh.py` stops with "no records found" rather than writing wrong
  numbers.

MIT licensed.
