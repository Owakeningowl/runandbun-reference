#!/usr/bin/env python3
"""Build rnb-data.js for the Run and Bun trainer sheet."""
import json, re, io, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
EM = '/Users/gabrielhernandez/Downloads/emerald-hard-hack/design/data/'

sp = json.load(open(EM + 'species.json'))
mv = json.load(open(EM + 'moves.json'))
rnb = json.load(open(os.path.join(HERE, 'rnb_trainers.json')))

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

# ---- species lookup (types only; RnB may retune stats, so we don't show them)
shortest = {}
for s in sp:
    n = s['name']
    if n not in shortest or len(s['const']) < len(shortest[n]):
        shortest[n] = s['const']

lut = {}
for s in sp:
    base = shortest[s['name']]
    c = s['const']
    suf = '' if c == base else (c[len(base) + 1:] if c.startswith(base + '_') else '')
    lut.setdefault(norm(s['name']) + norm(suf), s)
    lut.setdefault(norm(c.replace('SPECIES_', '')), s)

SPECIES_ALIAS = {
    'darmanitangalar': 'darmanitangalarstandard',
    'enamorust': 'enamorustherian',
    'zygarde10': 'zygarde10',
}
lut.setdefault('zygarde10', lut.get('zygarde10percent') or lut.get('zygarde'))

CAT = {'Physical': 'P', 'Special': 'S', 'Status': 'T'}
mlut = {norm(m['name']): m for m in mv}

def species_types(name):
    k = SPECIES_ALIAS.get(norm(name), norm(name))
    s = lut.get(k)
    return s['types'] if s else []

def sprite_slug(name):
    """Showdown gen5 slug: base is alphanumerics only, form keeps one dash."""
    n = name.replace('%', '')
    parts = n.split('-')
    base = re.sub(r'[^a-z0-9]', '', parts[0].lower())
    if len(parts) == 1:
        return base
    form = re.sub(r'[^a-z0-9]', '', ''.join(parts[1:]).lower())
    FIX = {'galar': 'galar', 'alola': 'alola', 'hisui': 'hisui', 'paldea': 'paldea'}
    return base + '-' + form if form else base

def move_info(name):
    k = norm(name)
    m = mlut.get(k)
    if m:
        return {'n': name, 't': m['type'], 'c': CAT.get(m['category'], 'T')}
    hp = re.match(r'hiddenpower(\w+)', k)
    if hp:
        t = hp.group(1).capitalize()
        return {'n': name, 't': t.capitalize(), 'c': 'S'}
    return {'n': name, 't': 'Normal', 'c': 'T'}

# ---- assemble, preserving the file's split order
order = []
for t in rnb:
    if t['split'] not in order:
        order.append(t['split'])

sections = []
for split in order:
    rows = [t for t in rnb if t['split'] == split]
    areas = []
    for t in rows:
        a = t.get('area') or ''
        if a and a not in areas:
            areas.append(a)
    trainers = []
    for i, t in enumerate(rows):
        team = []
        for m in t['team']:
            team.append({
                'n': m['name'],
                'g': sprite_slug(m['name']),
                'lv': m['level'],
                'i': m.get('item') or '',
                'ab': m.get('ability') or '',
                'na': m.get('nature') or '',
                'ty': species_types(m['name']),
                'mv': [move_info(x) for x in m['moves']],
            })
        trainers.append({
            'k': re.sub(r'[^a-z0-9]+', '-', (split + '-' + t['name'] + '-' + str(i)).lower()).strip('-'),
            'n': t['name'],
            'a': t.get('area') or '',
            'team': team,
        })
    sections.append({
        'k': re.sub(r'[^a-z0-9]+', '-', split.lower()).strip('-'),
        'n': split,
        'sub': '%d trainers · %d Pokémon%s' % (
            len(rows), sum(len(t['team']) for t in rows),
            (' · ' + ', '.join(areas[:4]) + (' …' if len(areas) > 4 else '')) if areas else ''),
        'trainers': trainers,
    })

out = {'sections': sections}
txt = 'window.RNB_DATA=' + json.dumps(out, separators=(',', ':'), ensure_ascii=False) + ';\n'
io.open(os.path.join(HERE, 'rnb-data.js'), 'w', encoding='utf-8').write(txt)

notypes = {m['n'] for s in sections for t in s['trainers'] for m in t['team'] if not m['ty']}
print('sections     : %d' % len(sections))
print('trainers     : %d' % sum(len(s['trainers']) for s in sections))
print('pokemon      : %d' % sum(len(t['team']) for s in sections for t in s['trainers']))
print('no types for : %s' % (sorted(notypes) or 'none'))
print('rnb-data.js  : %.0f KB' % (len(txt) / 1024))
