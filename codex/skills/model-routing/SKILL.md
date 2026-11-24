---
name: model-routing
description: Pick the Codex subagent role, model and reasoning effort before delegating, when a delegated result failed and needs escalating, or when the user asks which model or effort to use.
---

# Model routing (Codex)

Main session: `gpt-6.2-sol` medium (`model` / `model_reasoning_effort` in config.toml). Spawn workers with `agent_type` set to a role from `agents.toml` and `fork_turns="none"`; reuse one worker for related tasks and fixes. No nested subagents. User model choices override this skill.

## Subagent routing

Pick the row by task type and the column by the hardest signal present. Roles: `agents/*.toml` in this plugin, installed by `install.sh` and registered under `[agents]` in config.toml. Evidence: `routing/gpt_rows.json` (Artificial Analysis; refresh: `python3 -I scripts/refresh.py`).

Difficulty, hardest signal wins:
- Easy: 1-2 files, mechanical (rename, config, boilerplate, docs), or one obvious answer.
- Standard: 2-5 files, clear spec, tests or a checker exist. Migrations and performance work are Hard or higher.
- Hard: unknown root cause, distributed or multi-process systems (services, message buses, simulators), concurrency, crosses modules or more than 5 files, no tests, UI or visual output, performance optimization, a reversible migration of 5 files or fewer.
- Architecture: architecture decisions, major refactors, migrations that change schemas or data or span modules; also a Hard task still failing after one fix round.
- Critical: production or hardware control paths (deploys, payments, device or robot control), security, data-loss risk, final release review. Overrides every other signal.

| Type | Easy | Standard | Hard | Architecture | Critical |
|---|---|---|---|---|---|
| Read-only lookup: files, symbols, call sites, config, logs | `scout` terra/low | `scout` terra/low (thin: rerun on `reader`) | needs a correctness judgment: review row | - | - |
| Facts from text at hand (files, logs, pasted docs, one URL) | `reader` terra/high | `reader` terra/high | `reader` gathers, main synthesizes | - | - |
| Facts via mail, Slack, Drive or many web pages | `extractor` sol/medium | `extractor` sol/medium | `extractor` gathers, main synthesizes | - | - |
| Code change: feature, fix, refactor, tests, UI | main session sol/medium | `implementer` sol/high | `implementer-hard` sol/xhigh | `implementer-hard` sol/xhigh | `implementer-hard` sol/xhigh |
| Review, bug hunt or audit, no edits | main session sol/medium | `reviewer-lite` sol/high | `reviewer` sol/xhigh | `reviewer` sol/xhigh | `reviewer` sol/xhigh |

Astra only after sol xhigh failed twice on the same task (two fix rounds still missing the criteria): Hard -> `astra-hard` astra/high; Architecture or Critical -> `architect` astra/xhigh. Both implement or review per the brief (user rule 2026-11-20).

Models: terra = `gpt-6.1-terra`, sol = `gpt-6.2-sol`, astra = `gpt-6.2-astra`. Why (AA Intelligence Index / Terminal-Bench / cost per task):
- terra low: $0.07, 78 s, hallucination 0.42. Cheapest usable lookup; `gpt-6-luna` is cheaper but Terminal-Bench 0-0.13 and hallucination 0.79-0.85.
- terra high: hallucination 0.37, lowest of all variants, $0.26. Text extraction only.
- sol medium: AutomationBench 0.70 at $0.41, best tool-workflow value.
- sol high: 54.9 / 0.586 / $0.56. sol xhigh: 55.7 / 0.561 / $0.65, first try for Hard and up (user rule), about a quarter of astra's cost.
- astra high: 60.1 / 0.601 / $2.07. astra xhigh: 61.6 / 0.641 / $2.52, the top Terminal-Bench score. Escalation only.
- Never `max` or `ultra` unless the user names it: astra max = xhigh on Terminal-Bench (0.641) for +59% cost and +85% time; ultra has no AA data.
- Dominated, never route to: `gpt-6.1-sol`, `gpt-6-sol`, `gpt-6-astra` (beaten by the 6.2 versions on every axis), all `gpt-5.6-*` (5.6-luna xhigh Terminal-Bench 0.035), `gpt-6-luna` high and up.

Delegating a code change:
- Before: settle goal, success criteria, non-goals, allowed files, and runnable check commands; put all in the brief. No runnable check, no delegation.
- After: read `git status` and the whole diff yourself; any file outside the allowed list is a finding. Run the checks yourself and compare against the criteria, not the worker's report.
- Escalate one step at a time: 1. one fix round to the same worker (make sure it can run the check); 2. one column up: `implementer`/`reviewer-lite` (sol high) -> `implementer-hard`/`reviewer` (sol xhigh); 3. sol xhigh failed twice -> `astra-hard` (Hard) or `architect` (Architecture/Critical); 4. astra failed twice: stop and report to the user.
- Small models only get work where a mistake is cheap to spot. Code edits and judgment calls stay on main or implementer/reviewer roles.
- At most 3 agents at once (`agents.max_threads = 3`). Parallel writers in one repo each get their own worktree.


Critical means the change itself alters what reaches the hardware or production (command, stop or safety paths, deployed config). Local benchmarks, profiling, read-only measurement and UI styling inside such a repository stay Hard.
