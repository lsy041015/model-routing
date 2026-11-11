# Escalation and briefs

## Brief template

```
Goal: <one sentence>
Success criteria: <observable outcomes>
Non-goals: <what not to touch or change>
Allowed files: <paths or globs>
Checks: <exact commands that fail when the change is wrong>
Mode: implement | review (no edits)
```

A brief without a runnable check is not ready. Giving the worker a way to verify
its own work (test, build, a script that calls the endpoint) is usually cheaper
and faster than raising effort.

## When a result misses a criterion

Go one step at a time; stop at the first step that works.

1. **Self-check.** Make sure the worker can run a check that fails on the wrong
   result. Send one fix round to the same agent (SendMessage), with the failing
   output.
2. **Effort +1.** Same model, one effort level up: take it over in the main
   session, or use the agent one level up on the same model
   (`implementer` sonnet/high is already high; go to step 3).
3. **Model +1, effort down.** Next model up, at a lower effort than the failed
   run: sonnet/high → opus/medium or `implementer-hard`; opus/high →
   `architect` fable/medium; fable/medium → `critical` fable/high.

Do not go past `high` on the same model: one more level past high can cost as
much as the next model, which usually does better.

## Batches with automatic checks

Run every item at the cheaper tier, then re-run only the failures one tier up.
Example (claude.dev, SWE-bench Pro subset): Opus 5.5 low with failures re-run at
high passed ~97% at ~$0.17/task; every task at high passed 95.3% at $0.29/task.

## Red flags in a worker report

- "Done" without the check command and its output.
- Files changed outside the allowed list.
- A check rewritten or skipped to pass.
- Haiku claiming a fix: Haiku never gets code edits; re-run on the right agent.
