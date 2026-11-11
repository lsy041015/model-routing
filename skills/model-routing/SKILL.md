---
name: model-routing
description: Pick the Claude model, effort level and subagent for a task before delegating it. Use before any Agent/subagent call, when deciding whether to delegate, when a delegated result failed and needs escalating, when switching the main session's model, or when the user asks which model or effort to use.
---

# Model routing

Find the task in the table, use its agent, then apply the difficulty overrides. Agents are this plugin's (`model-routing:<name>`). Load a reference file only when its trigger applies.

## 1. Pick by task

| Task | Agent | Model / effort | Why |
|---|---|---|---|
| Find files, symbols, call sites, config, log lines | `scout` | haiku / low | Wrong answers are cheap to spot; main makes the judgment calls. |
| Classify, tag, route or extract fields from many short items | `classifier` | haiku / medium | Lowest cost and latency; output is checkable. |
| Read mail, chat, docs or web; pull facts, cases, table rows | `extractor` | sonnet / medium | Repeated, well-defined reading; low hallucination. |
| Repeated agent tasks: investigation, triage, drafting replies | `extractor` | sonnet / medium | Well-defined repeat work rarely needs a bigger model. |
| Bug fix, feature from a spec, 2-5 files, tests exist | `implementer` | sonnet / high | Handles scoped work at half the Opus token price. |
| Documents, slides, spreadsheets, reports | `writer` | sonnet / high | Fast iteration, strong eye for layout. Complex financial model or large source pile: `architect`. |
| Standard code review, 2-5 files | `reviewer-lite` | sonnet / high | Scoped diffs; about half the cost of Opus high. |
| Debugging with unknown cause, concurrency, multi-process, cross-module, UI, no tests | `implementer-hard` | opus / high | Needs judgment and longer agentic loops. |
| Hard review or audit | `reviewer` | opus / high | Same signals as above, no edits. |
| Browser / computer use, screenshot- or image-heavy loops | `vision` | opus / medium | Long agentic loops over many images; Opus is built for these. |
| Major refactor or migration, architecture planning, leading many subagents | `architect` | fable / medium | Most capable model for large technical work; medium first. |
| Deep research, scientific or quantitative analysis | `architect` (brief says read-only) | fable / medium | Same; raise only per escalation. |
| Security, data-loss risk, production or hardware control, final release review | `critical` | fable / high | Highest intelligence at top Terminal-Bench; cost is secondary. |
| Easy: 1-2 files, mechanical, one obvious answer | main session | - | A brief and its check cost more than the task. |

Main session (not a subagent):
- Default and "not sure yet": **Opus 5.5 / medium**.
- Chat a person waits on: Sonnet 5.5 / low or medium (Haiku 5.5 for simple chat at volume).
- Long unattended runs, or Opus high still falls short: Fable 5.2 / medium.

## 2. Difficulty overrides (hardest signal wins)

- Any Critical signal (security, data loss, production/hardware control, release review) → `critical`, whatever the table said.
- A clear spec does not make work easy: migrations and performance optimization go to `implementer-hard`, or `architect` when large.
- Haiku agents only get work where a mistake is cheap to spot. Code edits and judgment calls never go to Haiku.

## 3. Before and after delegating

- Brief: goal, success criteria, non-goals, allowed files, and a runnable check. No check → not ready.
- After: read `git status` and the whole diff yourself; run the checks yourself; judge against the success criteria, not the worker's report.
- Result misses a criterion → follow `references/escalation.md`. Never jump to `max`.

## 4. Limits

- Past `high`, test the next model up at lower effort instead of raising effort.
- At most 3 agents at once; parallel edits in one repo → one git worktree each.
- Keep the main context lean: hand verbose reading to `scout`, keep main for decisions.

## References (load on demand)

- `references/escalation.md`: a result failed or looks weak; batch re-run strategy; brief template.
- `references/costs.md`: comparing cost or speed; prices, benchmark tables, cache and context costs.
- `references/switching.md`: changing the main session's model, mixing models, API compatibility when moving a request between models.
- `references/measure.md`: choosing between models for a recurring workload on your own data.
