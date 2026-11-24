#!/usr/bin/env python3
"""Count Codex subagent runs by role, model and effort from local rollouts.

Usage: python3 -I codex/scripts/usage.py SINCE_ISO [CUTOFF_ISO] [--root DIR]
  --root  sessions folder (default $CODEX_HOME/sessions or ~/.codex/sessions)
A subagent rollout starts with session_meta whose source is
{"subagent": {"thread_spawn": {"agent_role": ...}}}; model and effort come from its
first turn_context, output tokens from its last token_count event.
"""
import collections, glob, json, os, sys

args = [a for a in sys.argv[1:] if not a.startswith('--')]
if not args:
    sys.exit(__doc__)
SINCE, CUT = args[0], (args[1] if len(args) > 1 else None)
home = os.environ.get('CODEX_HOME', os.path.expanduser('~/.codex'))
ROOT = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else os.path.join(home, 'sessions')


def read(path):
    """(start, role, model, effort, output tokens) or None if not a spawned subagent."""
    start = role = model = effort = None
    tokens = 0
    for i, line in enumerate(open(path, errors='ignore')):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        p = d.get('payload') or {}
        if i == 0:
            spawn = ((p.get('source') or {}) if isinstance(p.get('source'), dict) else {}).get('subagent') or {}
            spawn = spawn.get('thread_spawn') if isinstance(spawn, dict) else None
            if not spawn:
                return None
            start, role = p.get('timestamp') or d.get('timestamp'), spawn.get('agent_role') or '?'
        elif d.get('type') == 'turn_context' and model is None:
            model, effort = p.get('model'), p.get('effort') or p.get('reasoning_effort')
        elif d.get('type') == 'event_msg' and p.get('type') == 'token_count':
            tokens = ((p.get('info') or {}).get('total_token_usage') or {}).get('output_tokens', tokens)
    return start, role, model or '?', effort or '?', tokens


runs, out = collections.Counter(), collections.Counter()
for f in glob.glob(os.path.join(ROOT, '**', 'rollout-*.jsonl'), recursive=True):
    r = read(f)
    if not r or not r[0] or r[0] < SINCE:
        continue
    side = '' if not CUT else ('after' if r[0] >= CUT else 'before')
    key = (side,) + r[1:4]
    runs[key] += 1
    out[key] += r[4]

if not runs:
    print('no subagent runs since', SINCE)
total = sum(out.values()) or 1
for side in sorted({k[0] for k in runs}):
    keys = [k for k in runs if k[0] == side]
    print(f"== {side or 'all'} since {SINCE}: {sum(runs[k] for k in keys)} runs, {sum(out[k] for k in keys)} output tokens")
    for k in sorted(keys, key=lambda k: -out[k]):
        print(f'  {runs[k]:4} runs {out[k]:>10} tok {100 * out[k] / total:5.1f}%  {k[1]}  {k[2]}  {k[3]}')
