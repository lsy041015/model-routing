<p align="center">
  <img src="assets/model-routing-banner.png" alt="model-routing — Claude Code subagents routed to the right model" width="100%">
</p>

# model-routing

I kept catching my subagents doing easy lookups on the most expensive model, so I wrote down which model each kind of task should actually get. This Claude Code plugin is that table plus the agents that follow it.

| Task | Agent | Model / effort |
|---|---|---|
| Find files, symbols, config, log lines | `scout` | haiku / low |
| Classify, tag, route many short items | `classifier` | haiku / medium |
| Facts or summary from files, logs, pasted docs, a known URL | `reader` | haiku / high |
| Facts found via mail, chat, drive or many web pages; repeated investigation | `extractor` | sonnet / medium |
| Scoped bug fix or feature (2-5 files, tests) | `implementer` | sonnet / medium |
| Documents, slides, spreadsheets, reports | `writer` | sonnet / high |
| Standard code review | `reviewer-lite` | sonnet / medium |
| Hard debugging, concurrency, cross-module, UI, no tests | `implementer-hard` | opus / high |
| Hard review or audit | `reviewer` | opus / high |
| Browser, computer use, image-heavy loops | `vision` | opus / medium |
| Major refactor or migration, architecture, deep research | `implementer-hard` / `reviewer` with `effort: xhigh`; `architect` only after Opus xhigh fails twice | opus / xhigh, then fable / medium |
| Security, data loss, production or hardware control, release review | `implementer-hard` / `reviewer` with `effort: xhigh`; `critical` only after Opus xhigh fails twice | opus / xhigh, then fable / high |
| Easy 1-2 file changes | main session | Opus 5.5 / medium |

The skill keeps the table and a short delegation checklist in `SKILL.md` and only pulls in `references/` (escalation, costs, switching, measuring) when it needs them. The picks come from Artificial Analysis (2026-11-18) and claude.dev's model guide (2026-11-09), so they'll go stale; re-check `references/costs.md` against your own tasks now and then.

## Install

```
/plugin marketplace add lsy041015/model-routing
/plugin install model-routing@model-routing
```

Agents are named `model-routing:<agent>`, e.g. `model-routing:scout`. You'll need Claude Code v2.1.293 or later.

A few things the plugin can't set for you:

- Built-in `general-purpose` and `Plan` inherit your main model. Make them cheaper in `~/.claude/settings.json`:
  ```json
  { "env": { "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet" } }
  ```
- To run the built-in `Explore` on Haiku, copy [`extras/Explore.md`](extras/Explore.md) to `~/.claude/agents/Explore.md`.
- No Fable access? Change `model: fable` to `model: opus` and set `effort: xhigh` in `architect` and `critical`.
- If you want the rules always on, add `Before any Agent call, follow the model-routing skill.` to `~/.claude/CLAUDE.md`.

MIT licensed.
