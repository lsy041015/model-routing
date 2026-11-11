# model-routing

A Claude Code plugin that sends each subagent task to the right Claude model and effort level, based on what the task is and how hard it is.

| Task | Agent | Model / effort |
|---|---|---|
| Find files, symbols, config, log lines | `scout` | haiku / low |
| Classify, tag, route many short items | `classifier` | haiku / medium |
| Facts from mail, chat, docs, web; repeated investigation | `extractor` | sonnet / medium |
| Scoped bug fix or feature (2-5 files, tests) | `implementer` | sonnet / high |
| Documents, slides, spreadsheets, reports | `writer` | sonnet / high |
| Standard code review | `reviewer-lite` | sonnet / high |
| Hard debugging, concurrency, cross-module, UI, no tests | `implementer-hard` | opus / high |
| Hard review or audit | `reviewer` | opus / high |
| Browser, computer use, image-heavy loops | `vision` | opus / medium |
| Major refactor or migration, architecture, deep research | `architect` | fable / medium |
| Security, data loss, production or hardware control, release review | `critical` | fable / high |
| Easy 1-2 file changes | main session | Opus 5.5 / medium |

The `model-routing` skill keeps this table, the difficulty overrides and the delegation checklist in `SKILL.md`, and loads detail only when needed from `references/` (escalation, costs, switching models, measuring). Evidence: Artificial Analysis 2026-11-11 and claude.dev "Which Claude model should you build with?" (2026-11-09).

## Install

```
/plugin marketplace add lsy041015/model-routing
/plugin install model-routing@model-routing
```

Plugin agents are named `model-routing:<agent>`, for example `model-routing:scout`.

## Recommended manual setup

A plugin cannot change these for you.

1. **Cheaper default for built-in subagents.** `general-purpose` and `Plan` have no model of their own and otherwise inherit your main session's model. In `~/.claude/settings.json`:
   ```json
   { "env": { "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet" } }
   ```
2. **Cheap built-in Explore.** The built-in `Explore` agent runs on your session's model. To run it on Haiku, copy [`extras/Explore.md`](extras/Explore.md) to `~/.claude/agents/Explore.md`.
3. **Main session.** Opus 5.5 at medium effort is the recommended default (`/model`, `/effort`).
4. **Always apply the rules (optional).** The skill loads when Claude is about to delegate. To keep the rules in context all the time, add one line to `~/.claude/CLAUDE.md`: `Before any Agent call, follow the model-routing skill.`

## Requirements

- Claude Code v2.1.293 or later (the `haiku` alias resolves to Haiku 5.5 on the Anthropic API; on Bedrock, Vertex and Foundry it may still resolve to Haiku 4.5).
- Access to Fable for the `architect` and `critical` agents. Without it, change `model: fable` to `model: opus` in both, and set `effort: high` in `architect.md` and `effort: xhigh` in `critical.md`.

## Adjusting

Prices and benchmarks move. Re-check `skills/model-routing/references/costs.md` against your own tasks: pick real tasks with an outcome check, run each candidate at two or three effort levels in separate sessions, and compare score against spend.

## License

MIT
