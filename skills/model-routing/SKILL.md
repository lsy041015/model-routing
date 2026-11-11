---
name: model-routing
description: Pick the Claude model, effort level and subagent for a task before delegating it. Use before any Agent/subagent call, when deciding whether to delegate, when a delegated result failed and needs escalating, or when the user asks which model or effort to use.
---

# Model routing

Pick the row by task type and the column by the hardest signal present. Agent names below are this plugin's agents (`model-routing:<name>`).

## Difficulty (hardest signal wins)

- **Easy**: 1-2 files, mechanical (rename, config, boilerplate, docs), or one obvious answer.
- **Standard**: 2-5 files, clear spec, tests or a checker exist. A clear spec alone is not Standard: migrations and performance work go Hard.
- **Hard**: any of unknown root cause, concurrency, distributed or multi-process systems, crosses modules or more than 5 files, no tests, UI or visual output, migration, performance optimization.
- **Critical**: security, data-loss risk, production or hardware control paths, architecture, major refactor or migration, final release review. Overrides every other signal.

## Routing table

| Type | Easy | Standard | Hard | Critical |
|---|---|---|---|---|
| Read-only lookup: files, symbols, call sites, config, logs | `scout` haiku/low | `scout` haiku/low (thin result: rerun with `model: "sonnet"`) | needs a correctness judgment: review row | - |
| Facts from mail, chat, docs or the web | `extractor` sonnet/medium | `extractor` sonnet/medium | `extractor` gathers, main synthesizes | - |
| Code change: feature, fix, refactor, tests, UI | main session | `implementer` sonnet/high | `implementer-hard` opus/high | `critical` fable/high |
| Review, bug hunt or audit, no edits | main session | `reviewer-lite` sonnet/high | `reviewer` opus/high | `critical` fable/high (brief says review) |

Small models get only work where a mistake is cheap to spot (find files, run tests, read logs). Code edits and judgment calls stay on the main session or an implementer/reviewer. Easy changes stay in the main session: writing and checking a brief costs more than the task.

## Brief and verification

- Before delegating a code change, settle and put in the brief: goal, success criteria, non-goals, allowed files, and the check commands. A brief without a runnable check is not ready: self-verification beats more effort.
- After: read `git status` and the whole diff yourself. Any file outside the allowed list is a finding. Run the checks yourself and compare against the success criteria, not against the worker's report.

## Escalation (one step at a time)

1. Make sure the worker can verify its own work (test, build, a script that calls the endpoint); send one fix round to the same agent.
2. Raise effort one level (take it over in the main session, or use an agent one effort up on the same model).
3. Move one column up (the next model), at a lower effort than the failed run, not a higher one.

For batches with automatic checks: run everything at the lower tier, then re-run only the failures one tier up.

## Limits

- No `max` effort unless the user names it. Past `high`, test the next model up at a lower effort instead of raising effort: one more level past high can cost as much as a bigger model.
- Haiku: keep prompts under 100K tokens (the price is 5x above that). Never for code changes, multi-step tool workflows, visual output, or work judged only by its own report.
- Keep the main context lean: every turn resends it, so the bigger the main model, the more it costs. Hand verbose reading (logs, large files, search sweeps) to `scout` and keep the main session for decisions.
- Switching the main session's model drops its prompt cache, and moving down drops its thinking: switch only at a natural break, after `/compact` or in a fresh session with a short written plan.
- Run at most 3 agents at once. When parallel agents edit the same repo, give each its own git worktree. A lead plus many cheap workers pays off only when the work exceeds one context window; for one chain of dependent steps, use one agent.

## Evidence

Claude API list prices per million tokens (input/output): Haiku 5.5 $0.10/$0.50 (≤100K prompt), Sonnet 5.5 $2/$10, Opus 5.5 $4/$20, Fable 5.2 $8/$40.

Artificial Analysis, 2026-11-11, per index task:

| Variant | Intelligence | Terminal-Bench | $ / task | s / task |
|---|---|---|---|---|
| haiku-5.5 low | 18.6 | 0.126 | 0.044 | 129 |
| sonnet-5.5 medium | 30.8 | 0.298 | 0.78 | 221 |
| sonnet-5.5 high | 41.5 | 0.439 | 1.64 | 414 |
| opus-5.5 medium | 48.2 | 0.525 | 2.45 | 424 |
| opus-5.5 high | 51.8 | 0.566 | 3.47 | 573 |
| opus-5.5 xhigh | 57.4 | 0.596 | 6.05 | 953 |
| fable-5.2 medium | 56.4 | 0.551 | 3.80 | 475 |
| fable-5.2 high | 61.8 | 0.596 | 9.08 | 1049 |

From "Which Claude model should you build with?" (claude.dev, 2026-11-09): Opus 5.5 xhigh costs 2.5x high for +1.4 points on SWE-bench Pro; on FrontierCode 2.0 Fable 5.2 high matched Opus 5.5 max at about half the cost per task; Opus low with failures re-run at high passed ~97% at $0.17/task vs 95.3% at $0.29 all-high.

Benchmarks are a starting point. Measure on your own tasks: pick real tasks with an outcome check, run candidates at two or three efforts in separate sessions, and compare score against spend.
