#!/usr/bin/env python3
"""Count Claude Code subagent runs by agent, model and effort from local transcripts.

Usage: python3 -I claude/scripts/usage.py SINCE_ISO [CUTOFF_ISO] [--root DIR]
  SINCE   only runs that started at or after this time (e.g. 2026-11-18)
  CUTOFF  optional: split the counts into before/after (e.g. a rule change)
  --root  transcripts folder (default ~/.claude/projects)
Each run is counted by its own start time, so long sessions spanning SINCE are included.
"""
import collections, glob, json, os, sys

args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--root']
if not args:
    sys.exit(__doc__)
SINCE, CUT = args[0], (args[1] if len(args) > 1 else None)
ROOT = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else os.path.expanduser('~/.claude/projects')


def read(path):
    """(start timestamp, model, effort, output tokens) of one subagent transcript."""
    first, model, best, effort = None, None, {}, '?'
    for line in open(path, errors='ignore'):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        first = first or d.get('timestamp')
        if d.get('type') == 'assistant':
            m = d.get('message') or {}
            model = model or m.get('model')
            out = (m.get('usage') or {}).get('output_tokens', 0)
            best[m.get('id')] = max(best.get(m.get('id'), 0), out)
        if effort == '?' and '"effort":"' in line:  # effort sits in a nested field
            i = line.find('"effort":"') + 10
            effort = line[i:line.find('"', i)]
    return first, model, effort, sum(best.values())


runs, out = collections.Counter(), collections.Counter()
for s in glob.glob(os.path.join(ROOT, '*', '*', 'subagents', '*.jsonl')):
    t0, model, effort, tokens = read(s)
    if not t0 or t0 < SINCE:
        continue
    meta = s[:-6] + '.meta.json'
    agent = (json.load(open(meta)).get('agentType') or '?') if os.path.exists(meta) else '?'
    side = '' if not CUT else ('after' if t0 >= CUT else 'before')
    key = (side, agent, model or '?', effort)
    runs[key] += 1
    out[key] += tokens

total = sum(out.values()) or 1
for side in sorted({k[0] for k in runs}):
    keys = [k for k in runs if k[0] == side]
    part = sum(out[k] for k in keys)
    print(f"== {side or 'all'} since {SINCE}{' cutoff ' + CUT if CUT else ''}: "
          f"{sum(runs[k] for k in keys)} runs, {part} output tokens")
    for k in sorted(keys, key=lambda k: -out[k]):
        print(f'  {runs[k]:4} runs {out[k]:>10} tok {100 * out[k] / total:5.1f}%  {k[1]}  {k[2]}  {k[3]}')
