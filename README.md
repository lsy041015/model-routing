<p align="center">
  <img src="assets/model-routing-banner.png" alt="model-routing — subagents routed to the right model" width="560">
</p>

# model-routing

I kept catching my subagents doing easy lookups on the most expensive model, so I wrote down which model each kind of task should actually get. This repository is that table, packaged as a plugin for three coding agents: **Claude Code**, **Codex CLI** and **agy** (Antigravity CLI). Each plugin routes only to its own vendor's models; the difficulty scale, delegation checklist and escalation order are shared ([`core/RULES.md`](core/RULES.md)).

| Tier | Used for | Claude Code | Codex | agy |
|---|---|---|---|---|
| T0 lookup | find files, symbols, config, log lines | `scout` haiku / low | `scout` terra / low | `scout` flash |
| T1 read | facts from files, logs, pasted docs, one URL | `reader` haiku / high | `reader` terra / high | `reader` flash |
| T2 scoped | mail/chat/drive facts; 2-5 file change or review with tests | `extractor`, `implementer`, `reviewer-lite` sonnet / medium | sol / medium-high | flash |
| T3 strong | Hard: unknown cause, concurrency, cross-module, UI, no tests, performance | `implementer-hard`, `reviewer` opus / high | sol / xhigh | `implementer-hard`, `reviewer` pro |
| T4 strong-max | Architecture and Critical (production or hardware control, security, data loss, release) | same agents, opus / xhigh | sol / xhigh | pro |
| T5 escalation | only after T4 failed twice on the same task | `architect` / `critical` fable | `astra-hard` / `architect` astra | report to the user |

Easy 1-2 file changes stay in the main session. "Critical" means the change itself alters what reaches the hardware or production; local benchmarks, profiling, read-only measurement and UI styling stay Hard.

The picks come from [Artificial Analysis](https://artificialanalysis.ai) (Intelligence Index, Terminal-Bench, cost and time per task) and each vendor's model guide. They go stale: every plugin ships `scripts/refresh.py` to re-pull the numbers and `scripts/usage.py` to count what your subagents actually ran on.

## Layout

| Path | What |
|---|---|
| `core/` | shared rules, the AA scraper `aa.py`, `sync.py` that copies it into each plugin |
| `claude/` | Claude Code plugin: skill, 12 agents, `routing/routing.json` |
| `codex/` | Codex plugin: skill, 9 role files + `install.sh`, `routing/gpt_rows.json` |
| `agy/` | agy plugin: always-on rules, 7 agents, `routing/gemini_rows.json` |

Branches `core`, `claude`, `codex` and `agy` hold each part's history; `main` merges them.

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

```
/plugin marketplace add lsy041015/model-routing
/plugin install model-routing@model-routing
```

Agents are named `model-routing:<agent>`, e.g. `model-routing:scout`. Needs Claude Code v2.1.293 or later. The plugin can't set these for you:

- Built-in `general-purpose` and `Plan` inherit your main model. Make them cheaper in `~/.claude/settings.json`: `{ "env": { "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet" } }`
- To run the built-in `Explore` on Haiku, copy [`claude/extras/Explore.md`](claude/extras/Explore.md) to `~/.claude/agents/Explore.md`.
- No Fable access? Change `model: fable` to `model: opus` and set `effort: xhigh` in `architect` and `critical`.
- Rules always on: add `Before any Agent call, follow the model-routing skill.` to `~/.claude/CLAUDE.md`.
- `extractor` denies connector write tools by their CLI names (`mcp__claude_ai_Gmail__send_message`, ...). Apps that name connectors by id are covered only by its instructions.

## Codex CLI

| Role | Model | Reasoning effort | Sandbox | Use for |
|---|---|---|---|---|
| `scout` | gpt-6.1-terra | low | read-only | find files, symbols, call sites, config |
| `reader` | gpt-6.1-terra | high | read-only | facts or a summary from text at hand |
| `extractor` | gpt-6.2-sol | medium | read-only | facts via mail, chat, drive or many web pages |
| `implementer` | gpt-6.2-sol | high | workspace-write | Standard change: 2-5 files, clear spec, tests |
| `reviewer-lite` | gpt-6.2-sol | high | read-only | Standard review, no edits |
| `implementer-hard` | gpt-6.2-sol | xhigh | workspace-write | Hard, Architecture or Critical change (first try) |
| `reviewer` | gpt-6.2-sol | xhigh | read-only | Hard, Architecture or Critical review (first try) |
| `astra-hard` | gpt-6.2-astra | high | workspace-write | Hard escalation, only after sol xhigh failed twice |
| `architect` | gpt-6.2-astra | xhigh | workspace-write | Architecture or Critical escalation, only after sol xhigh failed twice |
| main session | gpt-6.2-sol | medium | - | Easy 1-2 file changes, planning, final verification |

```
codex plugin marketplace add lsy041015/model-routing
codex plugin add model-routing@model-routing
sh codex/install.sh        # from a clone: copies the role files into ~/.codex/agents
```

A Codex plugin can't register subagents, so `install.sh` copies `codex/agents/*.toml` into `$CODEX_HOME/agents` (existing files are kept unless `--force`) and prints the `[agents]` block for `config.toml`; it never edits `config.toml`. Recommended main session: `gpt-6.2-sol` at medium. Rules always on: add `Before spawning a subagent, follow the model-routing skill.` to `~/.codex/AGENTS.md`.

## agy (Antigravity CLI)

| Agent | Tier | Tools | Use for |
|---|---|---|---|
| `scout` | flash | read_file | find files, symbols, call sites, config, log lines |
| `reader` | flash | read_file, search_web | facts or a summary from text at hand |
| `extractor` | flash | read_file, search_web (+ your read-only MCP tools) | facts via mail, chat, drive or many web pages |
| `implementer` | flash | read_file, edit_file, write_file, run_command, manage_task | Standard change: 2-5 files, clear spec, tests |
| `reviewer-lite` | flash | read_file, run_command | Standard review, no edits |
| `implementer-hard` | pro | read_file, edit_file, write_file, run_command, manage_task | Hard, Architecture or Critical change |
| `reviewer` | pro | read_file, run_command | Hard, Architecture or Critical review, no edits |
| main session | your choice (`agy --model`, `--effort`) | - | Easy changes; strongest model at high effort for Architecture / Critical |

```
agy plugin install https://github.com/lsy041015/model-routing/tree/main/agy
```

The rules in `agy/rules/AGENTS.md` are always on while the plugin is enabled. agy subagents accept only a model tier (`model: flash` or `model: pro`; a full model id makes the loader skip the agent), so the table collapses to two tiers. For Architecture and Critical work, run the main session itself on the strongest model (`agy --model ... --effort high`). `extractor` only has read and web tools; add your read-only mail/chat MCP tools to its `tools:` list.

## Measuring

```
python3 -I claude/scripts/usage.py 2026-11-01 [CUTOFF]   # ~/.claude/projects
python3 -I codex/scripts/usage.py 2026-11-01 [CUTOFF]    # ~/.codex/sessions
python3 -I agy/scripts/usage.py 2026-11-01 [--all]       # ~/.gemini/antigravity-cli
python3 -I <plugin>/scripts/refresh.py --dry-run         # re-pull AA numbers
```

AA numbers are API prices and public benchmarks, not your workload. Before trusting a tier for recurring work, run a few real tasks with an outcome check on two models and compare score against spend.

MIT licensed.
