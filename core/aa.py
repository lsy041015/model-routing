"""Shared Artificial Analysis (AA) scraper for the model-routing plugins.

Edit only core/aa.py; `python3 core/sync.py` copies it into each plugin's scripts/.
AA has no public API: the data sits in an escaped RSC payload in each model page,
so a page-format change shows up as "no records found", never as wrong numbers.
"""
import json, re, urllib.request

BASE = 'https://artificialanalysis.ai/models/'
EFFORT = {None: 0, 'minimal': 0, 'low': 1, 'medium': 2, 'high': 3, 'xhigh': 4, 'max': 5}


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    s = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'ignore')
    return s.replace('\\"', '"')


def fetch(track, prefix):
    """Records for every variant of the release slugs in `track` (all starting with `prefix`).

    A page embeds full metrics only for base releases and its own variant, and AA
    redirects some variant pages to the base page, so every base and variant page is read.
    """
    alt = '|'.join(map(re.escape, track))
    pages, slugs = {}, set(track)
    for slug in track:
        try:
            pages[slug] = get(BASE + slug)
        except OSError as e:
            print('skip', slug, e)
            continue
        slugs |= set(re.findall(r'"slug":"(%s[a-z0-9.-]+)","name":"[^"]*","releaseSlug":"(?:%s)"'
                                % (re.escape(prefix), alt), pages[slug]))
    for slug in sorted(slugs - set(pages)):
        try:
            pages[slug] = get(BASE + slug)
        except OSError as e:
            print('skip', slug, e)
    dec, recs = json.JSONDecoder(), {}
    for s in pages.values():
        for m in re.finditer(r'\{"id":"[0-9a-f-]{36}","slug":"%s' % re.escape(prefix), s):
            try:
                o, _ = dec.raw_decode(s, m.start())
            except ValueError:
                continue
            if (o.get('release') or {}).get('slug') in track and 'intelligenceIndex' in o:
                if len(o) > len(recs.get(o['slug'], {})):
                    recs[o['slug']] = o
    return recs


def headline(x):
    """First nested 'headline' speed block."""
    if isinstance(x, dict):
        h = x.get('headline')
        if isinstance(h, dict) and 'outputSpeed' in h:
            return h
        x = x.values()
    if isinstance(x, (list, type({}.values()))):
        for v in x:
            h = headline(v)
            if h:
                return h
    return None


def row(o):
    g = o.get
    r = lambda x, n=3: None if x is None else round(x, n)
    cost = (g('intelligenceIndexCostPerTask') or {}).get('cost') or {}
    ts = g('timescaleData') or {}
    hl = headline(o) or {}
    return {
        'model': o['release']['slug'], 'effort': (g('effort') or {}).get('slug'),
        'intelligence': r(g('intelligenceIndex'), 1),
        'terminal_bench': r(g('terminalBench40')), 'scicode': r(g('scicode')),
        'long_context': r(g('lcr')), 'automation': r(g('automationBenchPartialScore')),
        'gdpval': r(g('gdpvalNormalized')), 'hle': r(g('hle')), 'critpt': r(g('critpt')),
        'hallucination': r(g('omniscienceHallucinationRate')),
        'price_in': g('price1mInputTokens'), 'price_out': g('price1mOutputTokens'),
        'cost_per_task': r(cost.get('total')),
        'sec_per_task': r(g('intelligenceIndexTimePerTask'), 0),
        'out_tokens_per_task': r((g('intelligenceIndexOutputTokensPerTask') or {}).get('output'), 0),
        'tok_per_sec': r(ts.get('medianOutputSpeed') or hl.get('outputSpeed'), 0),
        'ttft_sec': r(ts.get('medianTimeToFirstChunk') or hl.get('timeToFirstToken'), 1),
    }


def mark_dominated(rows):
    """B dominates A: no worse on cost, time, terminal_bench, intelligence; better on one."""
    keys = ('cost_per_task', 'sec_per_task', 'terminal_bench', 'intelligence')
    full = {k: v for k, v in rows.items() if all(v[x] is not None for x in keys)}
    for a, ra in full.items():
        ka = tuple(ra[x] for x in keys)
        ra['dominated_by'] = sorted(
            b for b, rb in full.items() if b != a
            and rb['cost_per_task'] <= ra['cost_per_task'] and rb['sec_per_task'] <= ra['sec_per_task']
            and rb['terminal_bench'] >= ra['terminal_bench'] and rb['intelligence'] >= ra['intelligence']
            and tuple(rb[x] for x in keys) != ka)


def refresh(db_path, track, prefix, argv):
    """Fetch, print a table, and write the "models" key of db_path (other keys kept).

    --dry-run prints only; refuses to drop known variants unless --force.
    """
    import datetime, os, sys
    recs = fetch(track, prefix)
    if not recs:
        sys.exit('no records found; AA page format changed, %s left untouched' % db_path)
    rows = {k: row(o) for k, o in recs.items()}
    mark_dominated(rows)
    rows = dict(sorted(rows.items(), key=lambda kv: (kv[1]['model'], EFFORT.get(kv[1]['effort'], 9))))
    print(f"{'variant':30} II    TB    $/task s/task hallu dominated_by")
    for k, v in rows.items():
        print(f"{k:30} {v['intelligence']!s:5} {v['terminal_bench']!s:5} {v['cost_per_task']!s:6} "
              f"{v['sec_per_task']!s:6} {v['hallucination']!s:5} {','.join(v.get('dominated_by') or [])}")
    db = json.load(open(db_path)) if os.path.exists(db_path) else {}
    lost = sorted(set(db.get('models', {})) - set(rows))
    if lost:
        print('missing vs db:', ', '.join(lost))
    if '--dry-run' in argv:
        return rows
    if lost and '--force' not in argv:
        sys.exit('%s left untouched; pass --force to drop the missing variants' % db_path)
    db.setdefault('source', {}).update(url=BASE + track[0], fetched=datetime.date.today().isoformat())
    db['models'] = rows
    with open(db_path, 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'wrote {len(rows)} variants to {db_path}')
    return rows
