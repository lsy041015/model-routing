# model-routing

A Claude Code plugin that sends each subagent task to the right Claude model and effort level, based on what the task is and how hard it is.

| Type | Easy | Standard | Hard | Critical |
|---|---|---|---|---|
| Lookup (read-only) | `scout` haiku/low | `scout` haiku/low | review row | - |
| Fact extraction | `extractor` sonnet/medium | `extractor` sonnet/medium | `extractor` + main | - |
| Code change | main session | `implementer` sonnet/high | `implementer-hard` opus/high | `critical` fable/high |
| Review (no edits) | main session | `reviewer-lite` sonnet/high | `reviewer` opus/high | `critical` fable/high |

The `model-routing` skill holds the difficulty rules, the brief and verification checklist, the escalation order and the evidence (Artificial Analysis 2026-11-11, claude.dev "Which Claude model should you build with?" 2026-11-09).

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
- Access to Fable for the `critical` agent. Without it, change `model: fable` to `model: opus` and `effort: high` to `effort: xhigh` in `agents/critical.md`.

## Adjusting

Prices and benchmarks move. Re-check the table in `skills/model-routing/SKILL.md` against your own tasks: pick real tasks with an outcome check, run each candidate at two or three effort levels in separate sessions, and compare score against spend.

## License

MIT
