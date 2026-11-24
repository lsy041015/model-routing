#!/usr/bin/env python3
"""Count Codex subagent runs by role, model and effort.

Usage: python3 -I codex/scripts/usage.py SINCE_ISO [CUTOFF_ISO] [--home DIR]
  --home  Codex home (default $CODEX_HOME or ~/.codex)
Reads the newest state_<n>.sqlite: every thread that is the child of a
thread_spawn_edges row is one spawned subagent, with its agent_role, model,
reasoning_effort and tokens_used (input + output, as Codex records it).
Codex before the state DB kept this only in rollout files; those are read as a
fallback when no state DB exists.
"""
import collections, datetime, glob, json, os, re, sqlite3, sys

args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--home']
if not args:
    sys.exit(__doc__)
SINCE, CUT = args[0], (args[1] if len(args) > 1 else None)
HOME = sys.argv[sys.argv.index('--home') + 1] if '--home' in sys.argv else \
    os.environ.get('CODEX_HOME', os.path.expanduser('~/.codex'))


def iso(epoch):
    return datetime.datetime.fromtimestamp(int(epoch), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def from_db(path):
    db = sqlite3.connect('file:%s?mode=ro' % path, uri=True)
    rows = db.execute(
        'select t.created_at, t.agent_role, t.model, t.reasoning_effort, t.tokens_used '
        'from threads t join thread_spawn_edges e on e.child_thread_id = t.id')
    return [(iso(c), r or '?', m or '?', e or '?', tok or 0) for c, r, m, e, tok in rows]


def from_rollouts(root):
    out = []
    for f in glob.glob(os.path.join(root, '**', 'rollout-*.jsonl'), recursive=True):
        start = role = model = effort = None
        tokens = 0
        for i, line in enumerate(open(f, errors='ignore')):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            p = d.get('payload') or {}
            if i == 0:
                src = p.get('source') if isinstance(p.get('source'), dict) else {}
                spawn = (src.get('subagent') or {}).get('thread_spawn') if isinstance(src.get('subagent'), dict) else None
                if not spawn:
                    break
                start, role = p.get('timestamp') or d.get('timestamp'), spawn.get('agent_role')
            elif d.get('type') == 'turn_context' and model is None:
                model, effort = p.get('model'), p.get('effort')
            elif d.get('type') == 'event_msg' and p.get('type') == 'token_count':
                tokens = ((p.get('info') or {}).get('total_token_usage') or {}).get('total_tokens', tokens)
        if start:
            out.append((start, role or '?', model or '?', effort or '?', tokens))
    return out


dbs = sorted(glob.glob(os.path.join(HOME, 'state_*.sqlite')),
             key=lambda p: int(re.search(r'state_(\d+)', p).group(1)))
records = from_db(dbs[-1]) if dbs else from_rollouts(os.path.join(HOME, 'sessions'))
runs, tok = collections.Counter(), collections.Counter()
for start, role, model, effort, tokens in records:
    if start < SINCE:
        continue
    key = ('' if not CUT else ('after' if start >= CUT else 'before'), role, model, effort)
    runs[key] += 1
    tok[key] += tokens

print('source:', os.path.basename(dbs[-1]) if dbs else 'rollout files')
if not runs:
    print('no subagent runs since', SINCE)
total = sum(tok.values()) or 1
for side in sorted({k[0] for k in runs}):
    keys = [k for k in runs if k[0] == side]
    print(f"== {side or 'all'} since {SINCE}: {sum(runs[k] for k in keys)} runs, {sum(tok[k] for k in keys)} tokens")
    for k in sorted(keys, key=lambda k: -tok[k]):
        print(f'  {runs[k]:4} runs {tok[k]:>11} tok {100 * tok[k] / total:5.1f}%  {k[1]}  {k[2]}  {k[3]}')
