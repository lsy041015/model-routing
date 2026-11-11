# Costs and benchmarks

## List prices (Claude API, per million tokens)

| Model | Input / output | Cache read | API default effort | Fast mode |
|---|---|---|---|---|
| Haiku 5.5 | $0.10 / $0.50 (prompt ≤100K); $0.50 / $2.50 above | $0.01 (≤100K), $0.05 above | medium | no |
| Sonnet 5.5 | $2 / $10 | $0.10 | high (medium in Claude Code) | no |
| Opus 5.5 | $4 / $20 | $0.20 | medium | yes |
| Fable 5.2 | $8 / $40 | $0.20 | high (medium in Claude Code) | yes |

All four: 1M-token context, 128K max output. `/effort` shows your current level.

## Artificial Analysis, 2026-11-11 (per index task)

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
