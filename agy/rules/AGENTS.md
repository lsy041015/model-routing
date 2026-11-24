# Model routing (agy)

Before delegating to a subagent, pick the row by task type and the column by the hardest
signal present. agy subagents choose only a model tier, `flash` or `pro`; the main
session's model and effort are yours (`agy --model ... --effort ...`).

Difficulty, hardest signal wins:
- Easy: 1-2 files, mechanical (rename, config, boilerplate, docs), or one obvious answer.
- Standard: 2-5 files, clear spec, tests or a checker exist. Migrations and performance work are Hard or higher.
- Hard: unknown root cause, distributed or multi-process systems, concurrency, crosses modules or more than 5 files, no tests, UI or visual output, performance optimization, a reversible migration of 5 files or fewer.
- Architecture: architecture decisions, major refactors, migrations that change schemas or data or span modules; also a Hard task still failing after one fix round.
- Critical: production or hardware control paths (deploys, payments, device or robot control), security, data-loss risk, final release review. Overrides every other signal. Critical means the change itself alters what reaches the hardware or production; local benchmarks, profiling, read-only measurement and UI styling stay Hard.

| Type | Easy | Standard | Hard | Architecture | Critical |
|---|---|---|---|---|---|
| Read-only lookup: files, symbols, call sites, config, logs | `scout` flash | `scout` flash | needs a judgment: review row | - | - |
| Facts from text at hand (files, logs, pasted docs, one URL) | `reader` flash | `reader` flash | `reader` gathers, main synthesizes | - | - |
| Facts via mail, chat, drive or many web pages | `extractor` flash | `extractor` flash | `extractor` gathers, main synthesizes | - | - |
| Code change: feature, fix, refactor, tests, UI | main session | `implementer` flash | `implementer-hard` pro | `implementer-hard` pro | `implementer-hard` pro |
| Review, bug hunt or audit, no edits | main session | `reviewer-lite` flash | `reviewer` pro | `reviewer` pro | `reviewer` pro |

For Architecture and Critical work, run the main session itself on the strongest model at
high effort, since the subagent tier stops at `pro`.

Delegating a code change:
- Before: settle goal, success criteria, non-goals, allowed files and runnable check commands; put all of them in the brief. No runnable check, no delegation.
- After: read `git status` and the whole diff yourself; a file outside the allowed list is a finding. Run the checks yourself and judge against the criteria, not the worker's report.
- Escalate one step at a time: one fix round to the same worker; then flash -> pro; `pro` failed twice on the same task: stop and report to the user.
- Small-tier (`flash`) workers only get work where a mistake is cheap to spot.
- At most 3 subagents at once; parallel writers in one repository each get their own worktree.
- Never use `max` effort unless the user names it.

Evidence for the main-session choice: `routing/gemini_rows.json` in this plugin
(Artificial Analysis; refresh with `python3 -I scripts/refresh.py`).
