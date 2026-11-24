#!/usr/bin/env python3
"""Copy core/aa.py into each plugin's scripts/ (plugins install separately, so each ships a copy).

Usage: python3 -I core/sync.py [--check]   (--check: exit 1 if any copy differs)
"""
import os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'core', 'aa.py')
PLUGINS = ('claude', 'codex')

src = open(SRC, 'rb').read()
bad = []
for p in PLUGINS:
    if not os.path.isdir(os.path.join(ROOT, p)):
        continue
    dst = os.path.join(ROOT, p, 'scripts', 'aa.py')
    same = os.path.exists(dst) and open(dst, 'rb').read() == src
    if '--check' in sys.argv:
        if not same:
            bad.append(dst)
    elif not same:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(SRC, dst)
        print('updated', os.path.relpath(dst, ROOT))
if bad:
    sys.exit('out of sync: ' + ', '.join(os.path.relpath(b, ROOT) for b in bad))
print('in sync')
