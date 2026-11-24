# Model routing rules (provider-neutral)

Each plugin (`claude/`, `codex/`, `agy/`) maps these rules to its own models. Only the
model names differ; the difficulty scale, delegation checklist and escalation order are
the same everywhere.

## Tiers

| Tier | Meaning | Claude | Codex | agy |
|---|---|---|---|---|
| T0 lookup | cheapest; output easy to check | haiku / low | terra / low | flash |
| T1 read | cheap, low hallucination; text already at hand | haiku / high | terra / high | flash |
| T2 scoped | tool loops and clear-spec work | sonnet / medium | sol / medium | flash (extraction); pro (code, review) |
| T3 strong | hard work, judgment | opus / high | sol / high | pro |
| T4 strong-max | architecture and critical work | opus / xhigh | sol / xhigh | pro |
| T5 escalation | only after T4 failed twice | fable / medium-high | astra / high-xhigh | report to the user |

agy subagents accept only two model tiers (`flash`, `pro`): `flash` for T0-T1 and extraction, `pro` for every code change or review; for T4 run the agy main session on a stronger model (Neon high -> Carbon).

Codex: sol xhigh scores lower than sol high on Terminal-Bench (AA 2026-11-24), so a failing T3 Codex task skips T4 and escalates straight to astra (T5).

## Difficulty (hardest signal wins)

- **Easy**: 1-2 files, mechanical (rename, config, boilerplate, docs), or one obvious answer. Stays in the main session.
- **Standard**: 2-5 files, clear spec, tests or a checker exist. A clear spec alone is not Standard: migrations and performance work go Hard or higher.
- **Hard**: any of unknown root cause, distributed or multi-process systems, concurrency, crosses modules or more than 5 files, no tests, UI or visual output, performance optimization, a reversible migration of 5 files or fewer.
- **Architecture**: architecture decisions, major refactors, migrations that change schemas or data or span several modules; also a Hard task still failing after one fix round.
- **Critical**: production or hardware control paths (deploys, payments, device or robot control), security, data-loss risk, final release review. Overrides every other signal.
  Critical means the change itself alters what reaches the hardware or production (command, stop or safety paths, deployed config). Working inside such a repository is not enough: local benchmarks, profiling, read-only measurement and UI styling there stay Hard.

## Task type x difficulty

| Type | Easy | Standard | Hard | Architecture | Critical |
|---|---|---|---|---|---|
| Read-only lookup: files, symbols, call sites, config, logs | T0 | T0 (thin result: rerun one tier up) | needs a judgment: review row | - | - |
| Facts from text at hand (files, logs, pasted docs, a known URL) | T1 | T1 | T1 gathers, main synthesizes | - | - |
| Facts via mail, chat, drive or many web pages | T2 | T2 | T2 gathers, main synthesizes | - | - |
| Code change: feature, fix, refactor, tests, UI | main | T2 | T3 | T4 | T4 |
| Review, bug hunt or audit, no edits | main | T2 | T3 | T4 | T4 |

Small models only get work where a mistake is cheap to spot. Code edits, judgment calls and
account-tool loops never go to T0/T1.

## Delegating a code change

- **Before**: settle goal, success criteria, non-goals, allowed files, and runnable check commands; put all of them in the brief. No runnable check, no delegation.
- **After**: read `git status` and the whole diff yourself; a file outside the allowed list is a finding. Run the checks yourself and judge against the criteria, not the worker's report.
- **Escalate one step at a time**:
  1. one fix round to the same worker (make sure it can run the check);
  2. one tier up (T2 -> T3 -> T4);
  3. only after T4 failed twice on the same task: T5;
  4. T5 failed too: stop and report to the user.
- **Batch with automatic checks**: run everything at the low tier, re-run only the failures one tier up.

## Limits

- Never use `max` (or any effort above the table) unless the user names it: on AA it costs far more for the same Terminal-Bench score.
- At most 3 subagents at once; parallel writers in one repository each get their own worktree.
- Keep the main context lean: hand verbose reading (logs, large files, search sweeps) to T0/T1 and keep the main session for decisions.
- Benchmarks (Artificial Analysis) are a proxy. Measure on your own tasks before trusting a tier for a recurring workload (each plugin ships a `usage.py`).
