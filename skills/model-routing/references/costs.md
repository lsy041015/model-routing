# Costs and benchmarks

## List prices (Claude API, per million tokens)

| Model | Input / output | Cache read | API default effort | Fast mode |
|---|---|---|---|---|
| Haiku 5.5 | $0.10 / $0.50 (prompt ≤100K); $0.50 / $2.50 above | $0.01 (≤100K), $0.05 above | medium | no |
| Sonnet 5.5 | $2 / $10 | $0.10 | high (medium in Claude Code) | no |
| Opus 5.5 | $4 / $20 | $0.20 | medium | yes |
| Fable 5.2 | $8 / $40 | $0.20 | high (medium in Claude Code) | yes |

All four: 1M-token context, 128K max output. `/effort` shows your current level.

## Artificial Analysis, 2026-11-18 (per index task)

| Variant | Intelligence | Terminal-Bench | Tool workflows | $ / task | s / task | Output tok/s | First token (s) |
|---|---|---|---|---|---|---|---|
| haiku-5.5 low | 18.6 | 0.126 | 0.229 | 0.044 | 132 | 213 | 5.3 |
| haiku-5.5 medium | 24.6 | 0.152 | 0.286 | 0.092 | 238 | 224 | 9.7 |
| haiku-5.5 max | 36.5 | 0.328 | 0.354 | 0.41 | 880 | 257 | 187 |
| sonnet-5.5 medium | 30.8 | 0.298 | 0.549 | 0.78 | 236 | 131 | 5.0 |
| sonnet-5.5 high | 41.5 | 0.439 | 0.594 | 1.64 | 406 | 144 | 9.4 |
| sonnet-5.5 xhigh | 49.9 | 0.571 | 0.655 | 4.09 | 854 | 143 | 27.3 |
| opus-5.5 medium | 48.2 | 0.525 | 0.612 | 2.45 | 407 | 108 | 12.5 |
| opus-5.5 high | 51.8 | 0.566 | 0.632 | 3.47 | 556 | 108 | 21.3 |
| opus-5.5 xhigh | 57.4 | 0.596 | 0.650 | 6.05 | 945 | 109 | 65.9 |
| opus-5.5 max | 59.1 | 0.596 | 0.695 | 10.04 | 1475 | 117 | 354 |
| fable-5.2 low | 53.9 | 0.545 | 0.680 | 3.10 | 324 | 111 | 7.4 |
| fable-5.2 medium | 56.4 | 0.551 | 0.688 | 3.80 | 406 | 106 | 9.5 |
| fable-5.2 high | 61.8 | 0.596 | 0.714 | 9.08 | 878 | 111 | 24.1 |

Tool workflows = AutomationBench. Output speed is Haiku ~2x Opus/Fable, but time
per task is driven by tokens spent, not speed.

Reading the table:
- Opus max vs xhigh: +1.7 intelligence, same Terminal-Bench, +66% cost, +56%
  time. Opus max is dominated by Fable 5.2 high.
- Opus high vs Sonnet xhigh: same Terminal-Bench (0.566 vs 0.571), −15% cost,
  −35% time. Hard work goes to Opus high, not Sonnet xhigh.
- Haiku max is no Sonnet substitute: half the cost of Sonnet medium, but tool
  workflows 0.354 vs 0.549 and 3.7x the time; below Sonnet high on
  Terminal-Bench (0.328 vs 0.439).
- Fable low vs Opus high: −11% cost, −42% time, higher intelligence and tool
  workflows, but Terminal-Bench 0.545 vs 0.566. Worth an A/B on your own hard
  tasks (`measure.md`) before switching.

Fable 5.1 is dominated at every effort by Fable 5.2 or Opus 5.5; do not use it.

## From claude.dev, "Which Claude model should you build with?" (2026-11-09)

- SWE-bench Pro, Opus 5.5 relative to high: medium −2.5 points at ~70% cost; low
  −8 points at ~1/3 cost; xhigh +1.4 points at 2.5x cost.
- FrontierCode 2.0: Fable 5.2 high 45.3% vs Opus 5.5 max 45.5%, at about half
  the cost per task.
- Terminal-Bench 3.0: Fable 5.1 max 58.0% vs Opus 5.5 high 58.9% with half the
  tokens.
- Opus 5.5 lead + up to 25 Sonnet 5.5 workers over ~22M tokens of code: about
  one third cheaper than Opus alone, same score. Only for work larger than one
  context window.

## Context and cache

- Every turn resends the context; on long runs most input bills as cache reads.
- Opus 5.5 cache read: ~$0.03 per turn at 150K context, ~$0.004 at 20K.
- Fable and Opus cache reads cost the same, so on cache-heavy runs the gap is
  only uncached input and output (Fable 2x).
- Haiku over 100K prompt costs 5x; on long prompts compare Haiku and Sonnet by
  cost per finished task, not list price.
- The hardest few tasks carry most of the spend (one 20-problem benchmark: 2
  problems = 43%). Price the hard tail, not the average.
