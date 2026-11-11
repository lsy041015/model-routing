# Measure on your own work

Benchmarks pick a starting model. For a workload you will run often:

1. Pull a sample of real tasks. Write an outcome check for each (passing test,
   closed ticket, correct row count).
2. Run each candidate model at two or three effort levels, each in its own
   session so runs do not share a cache. Record the cost of each finished task
   from the response `usage` field.
3. Plot score against spend. Keep a multi-model setup only if it beats every
   single-model point.
4. Run the winner in shadow on a slice of real traffic before cutting over.

Quick check in Claude Code: run one backlog task on two models (`/model`) and
compare `/usage`.
