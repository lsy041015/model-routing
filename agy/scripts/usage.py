#!/usr/bin/env python3
"""Count agy (Antigravity CLI) subagent conversations by agent and model.

Usage: python3 -I agy/scripts/usage.py SINCE_ISO [--all] [--root DIR]
  --all   also count top-level conversations (useful to check the parser)
  --root  data folder (default ~/.gemini/antigravity-cli)
Subagents are rows of conversation_summaries.db with a parent_conversation_id.
The model is the first model-like id in the conversation's gen_metadata blob
(protobuf, read as bytes): best effort, '?' when absent. agy stores no token counts
in a readable form, so this reports runs only.
"""
import collections, os, re, sqlite3, sys

args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--root']
if not args:
    sys.exit(__doc__)
SINCE = args[0]
ROOT = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else os.path.expanduser('~/.gemini/antigravity-cli')
MODEL = re.compile(rb'(?:gemini|claude|gpt)-[a-z0-9.-]+')


def ro(path):
    return sqlite3.connect('file:%s?mode=ro' % path, uri=True)


def model_of(cid):
    path = os.path.join(ROOT, 'conversations', cid + '.db')
    if not os.path.exists(path):
        return '?'
    try:
        for (blob,) in ro(path).execute('select data from gen_metadata order by idx limit 5'):
            for hit in MODEL.finditer(blob or b''):
                # protobuf string: the byte before it is its length
                start = hit.start()
                n = blob[start - 1] if start else 0
                text = blob[start:start + n]
                if n and MODEL.fullmatch(text):
                    return text.decode()
    except sqlite3.Error:
        pass
    return '?'


where = '' if '--all' in sys.argv else "and coalesce(parent_conversation_id, '') != ''"
rows = ro(os.path.join(ROOT, 'conversation_summaries.db')).execute(
    "select conversation_id, coalesce(agent_name, ''), last_modified_time from conversation_summaries "
    "where last_modified_time >= ? " + where, (SINCE,)).fetchall()
runs = collections.Counter((agent or 'main', model_of(cid)) for cid, agent, _ in rows)
print(f"== {'conversations' if '--all' in sys.argv else 'subagent runs'} since {SINCE}: {sum(runs.values())}")
for (agent, model), n in runs.most_common():
    print(f'  {n:4}  {agent}  {model}')
