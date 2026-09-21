#!/usr/bin/env python3
"""Render the Run and Bun trainer doc in the same style as the Emerald split docs.

Teams only: no EVs, no computed stats, no AI notes.
    python3 build_rnb_doc2.py   ->  trainers.html
"""
import html, io, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
EM = '/Users/gabrielhernandez/Downloads/emerald-hard-hack/design/data/'
e = html.escape

sp = json.load(open(EM + 'species.json'))
mv = json.load(open(EM + 'moves.json'))
rnb = json.load(open(os.path.join(HERE, 'rnb_trainers.json')))

TYPE = {
    'Normal': '#9A9A7A', 'Fire': '#D9602B', 'Water': '#4A7BE0', 'Electric': '#E9C02A',
    'Grass': '#5FA83A', 'Ice': '#7CCCCB', 'Fighting': '#B0332A', 'Poison': '#984095',
    'Ground': '#D4B25C', 'Flying': '#8C7FD8', 'Psychic': '#E8507D', 'Bug': '#95A625',
    'Rock': '#AA9139', 'Ghost': '#6A5794', 'Dragon': '#6A3CF0', 'Dark': '#6A5446',
    'Steel': '#9C9CB8', 'Fairy': '#D883A8',
}

def ink_for(hexcol):
    """Dark ink that sits on the type colour, same look as the split docs."""
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02x%02x%02x' % (int(r * .17), int(g * .17), int(b * .17))

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

# ---------------------------------------------------------------- lookups
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
ALIAS = {'darmanitangalar': 'darmanitangalarstandard',
         'enamorust': 'enamorustherian', 'zygarde10': 'zygarde10'}
lut.setdefault('zygarde10', lut.get('zygarde'))

CAT = {'Physical': 'Phys', 'Special': 'Spec', 'Status': 'Stat'}
mlut = {norm(m['name']): m for m in mv}

def types_of(name):
    s = lut.get(ALIAS.get(norm(name), norm(name)))
    return s['types'] if s else []

def slug(name):
    n = name.replace('%', '')
    parts = n.split('-')
    base = re.sub(r'[^a-z0-9]', '', parts[0].lower())
    if len(parts) == 1:
        return base
    form = re.sub(r'[^a-z0-9]', '', ''.join(parts[1:]).lower())
    return base + '-' + form if form else base

def move_of(name):
    m = mlut.get(norm(name))
    if m:
        return m['name'], m['type'], CAT.get(m['category'], 'Stat'), m['power']
    hp = re.match(r'hiddenpower(\w+)', norm(name))
    if hp:
        return name, hp.group(1).capitalize(), 'Spec', 60
    return name, 'Normal', 'Stat', 0

SPRITE = 'https://play.pokemonshowdown.com/sprites/gen5/%s.png'

# ---------------------------------------------------------------- structure
order = []
for t in rnb:
    if t['split'] not in order:
        order.append(t['split'])

splits = []
for name in order:
    rows = [t for t in rnb if t['split'] == name]
    areas = []
    for t in rows:
        a = t.get('area') or 'Pokémon League'
        if a not in areas:
            areas.append(a)
    splits.append({
        'name': name,
        'key': re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-'),
        'rows': rows,
        'areas': areas,
        'mons': sum(len(t['team']) for t in rows),
        'lo': min(m['level'] for t in rows for m in t['team']),
        'hi': max(m['level'] for t in rows for m in t['team']),
    })

TOTAL_T = len(rnb)
TOTAL_M = sum(len(t['team']) for t in rnb)
SPECIES = len({m['name'] for t in rnb for m in t['team']})

# ---------------------------------------------------------------- render
def mon_card(m):
    ts = types_of(m['name'])
    pills = ''.join(
        '<span class="type" style="--tb:%s;--tf:%s">%s</span>' % (TYPE.get(t, '#9A9A7A'), ink_for(TYPE.get(t, '#9A9A7A')), t)
        for t in ts)
    moves = []
    for raw in m['moves']:
        nm, ty, cat, pw = move_of(raw)
        moves.append(
            '<li><span class="mdot" style="background:%s" title="%s"></span>'
            '<span class="mname">%s</span><span class="mmeta">%s %s</span></li>'
            % (TYPE.get(ty, '#9A9A7A'), e(ty), e(nm), cat, pw if pw else '&#8212;'))
    kv = ['<div><dt>Item</dt><dd>%s</dd></div>' % (e(m['item']) if m.get('item') else '<span class="none">&#8212;</span>'),
          '<div><dt>Ability</dt><dd>%s</dd></div>' % e(m.get('ability') or '—'),
          '<div><dt>Nature</dt><dd>%s</dd></div>' % e(m.get('nature') or '—')]
    return (
        '<article class="mon">'
        '<header class="mon-head">'
        '<img class="sprite" src="%s" alt="%s" width="96" height="96" loading="lazy">'
        '<div class="mon-id"><h4>%s</h4><p class="lv">Lv %d</p><p class="types">%s</p></div>'
        '</header>'
        '<dl class="kv">%s</dl>'
        '<ul class="moves">%s</ul>'
        '</article>'
    ) % (SPRITE % slug(m['name']), e(m['name']), e(m['name']), m['level'], pills,
         ''.join(kv), ''.join(moves))

def trainer_block(t, idx):
    lv = [m['level'] for m in t['team']]
    lo, hi = min(lv), max(lv)
    tid = re.sub(r'[^a-z0-9]+', '-', (t['split'] + '-' + t['name'] + '-' + str(idx)).lower()).strip('-')
    return (
        '<section class="fight" id="%s">'
        '<header class="fight-head">'
        '<h3>%s</h3>'
        '<div class="facts">'
        '<span class="fact">%s</span>'
        '<span class="fact"><b>%d</b> Pok&eacute;mon</span>'
        '<span class="fact">Lv <b>%s</b></span>'
        '</div></header>'
        '<div class="team">%s</div>'
        '</section>'
    ) % (tid, e(t['name']), e(t.get('area') or 'Pokémon League'), len(t['team']),
         str(lo) if lo == hi else '%d&#8211;%d' % (lo, hi),
         ''.join(mon_card(m) for m in t['team']))

ladder = ''.join(
    '<a class="rung" href="#%s"><b>%s</b><span>%d trainers</span><span>%d Pok&eacute;mon &#183; Lv %d&#8211;%d</span></a>'
    % (s['key'], e(s['name'].replace(' Split', '')), len(s['rows']), s['mons'], s['lo'], s['hi'])
    for s in splits)

body = []
for s in splits:
    body.append('<section class="split" id="%s">' % s['key'])
    body.append(
        '<div class="split-head"><h2>%s</h2>'
        '<p>%d trainers &#183; %d Pok&eacute;mon &#183; Lv %d&#8211;%d</p></div>'
        % (e(s['name']), len(s['rows']), s['mons'], s['lo'], s['hi']))
    area = None
    for i, t in enumerate(s['rows']):
        a = t.get('area') or 'Pokémon League'
        if a != area:
            area = a
            body.append('<h3 class="area">%s</h3>' % e(area))
        body.append(trainer_block(t, i))
    body.append('</section>')

doc = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Run and Bun &#8212; Trainer Sheet</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="rnb-site.css">
<style>
:root{
  --ground:#EEF2EF; --surface:#FFFFFF; --sunken:#E3E9E5; --ink:#15201B; --muted:#56645C; --faint:#7B8981;
  --rule:#D3DCD6; --accent:#0B7453; --accent-soft:#D8EEE5; --warn:#A3401E;
  --display:"Barlow Condensed","Arial Narrow",system-ui,sans-serif;
  --body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0E1412; --surface:#151D19; --sunken:#1B2520; --ink:#E3ECE7; --muted:#9AAAA1; --faint:#77867E;
    --rule:#28332D; --accent:#48C898; --accent-soft:#16372B; --warn:#F08A62;
  }
}
:root[data-theme="dark"], :root[data-theme="night"]{
  --ground:#0E1412; --surface:#151D19; --sunken:#1B2520; --ink:#E3ECE7; --muted:#9AAAA1; --faint:#77867E;
  --rule:#28332D; --accent:#48C898; --accent-soft:#16372B; --warn:#F08A62;
}
*{ box-sizing:border-box; }
body{ background:var(--ground); color:var(--ink); font:15px/1.5 var(--body); margin:0; }
.wrap{ max-width:1500px; margin:0 auto; padding:32px 24px 64px; }
h1,h2,h3,h4{ font-family:var(--display); letter-spacing:.01em; text-wrap:balance; margin:0; }

.masthead{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,520px); gap:32px;
  align-items:end; padding-bottom:24px; border-bottom:2px solid var(--ink); }
.eyebrow{ font:500 12px var(--mono); letter-spacing:.14em; text-transform:uppercase; color:var(--accent); margin:0 0 10px; }
.masthead h1{ font-size:clamp(40px,6vw,68px); line-height:.95; text-transform:uppercase; }
.masthead .lede{ color:var(--muted); max-width:62ch; margin:12px 0 0; }
.rules{ margin:0; padding:0; list-style:none; display:grid; gap:6px; font-size:13px; color:var(--muted); }
.rules li{ padding-left:14px; position:relative; }
.rules li::before{ content:""; position:absolute; left:0; top:.65em; width:6px; height:6px; background:var(--accent); }
.rules b{ color:var(--ink); font-weight:600; }

.ladder{ display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:6px; margin:24px 0 8px; }
.rung{ display:grid; gap:2px; padding:10px 10px 8px; background:var(--surface);
  border:1px solid var(--rule); border-top:4px solid var(--accent); text-decoration:none; color:inherit; }
.rung:hover{ background:var(--accent-soft); }
.rung b{ font:700 15px/1.15 var(--display); text-transform:uppercase; }
.rung span{ font-size:11.5px; color:var(--faint); }

.toolbar{ position:sticky; top:0; z-index:30; display:flex; gap:10px; flex-wrap:wrap; align-items:center;
  margin:22px 0 6px; padding:10px 12px; background:var(--surface); border:1px solid var(--rule); }
.toolbar input{ flex:1 1 260px; padding:7px 10px; font:14px var(--body); color:var(--ink);
  background:var(--ground); border:1px solid var(--rule); }
.toolbar input:focus{ outline:2px solid var(--accent); outline-offset:-2px; }
.toolbar .hits{ font:500 12px var(--mono); color:var(--faint); }

.split{ margin-top:44px; }
.split-head{ border-bottom:2px solid var(--ink); padding-bottom:8px; margin-bottom:6px; }
.split-head h2{ font-size:clamp(26px,3.4vw,40px); text-transform:uppercase; line-height:1; }
.split-head p{ margin:6px 0 0; font:500 12px var(--mono); color:var(--faint); letter-spacing:.06em; }
h3.area{ font-size:15px; text-transform:uppercase; letter-spacing:.12em; color:var(--accent);
  margin:26px 0 10px; padding-bottom:5px; border-bottom:1px solid var(--rule); }

.fight{ background:var(--sunken); padding:12px 14px 14px; margin:0 0 10px; }
.fight-head{ display:flex; gap:12px; align-items:baseline; flex-wrap:wrap; margin-bottom:10px; }
.fight-head h3{ font-size:21px; text-transform:uppercase; }
.facts{ display:flex; gap:8px; flex-wrap:wrap; margin-left:auto; }
.fact{ font-size:12.5px; padding:3px 9px; background:var(--surface); color:var(--muted); }
.fact b{ font-family:var(--mono); font-weight:500; color:var(--ink); }

.team{ display:grid; grid-template-columns:repeat(auto-fill,minmax(216px,1fr)); gap:8px; }
.mon{ background:var(--surface); border:1px solid var(--rule); padding:10px 11px 11px;
  display:grid; gap:8px; align-content:start; }
.mon-head{ display:flex; gap:8px; align-items:center; }
.sprite{ width:72px; height:72px; image-rendering:pixelated; flex:0 0 72px; }
.mon-id{ min-width:0; }
.mon-id h4{ font-size:18px; line-height:1.1; text-transform:uppercase; word-break:break-word; }
.lv{ margin:2px 0 0; font:500 11.5px var(--mono); color:var(--faint); }
.types{ margin:5px 0 0; display:flex; gap:3px; flex-wrap:wrap; }
.type{ font:600 10.5px/1 var(--body); letter-spacing:.04em; text-transform:uppercase;
  padding:3px 6px; border-radius:2px; background:var(--tb); color:var(--tf); }

.kv{ margin:0; display:grid; gap:2px; font-size:12.5px; }
.kv div{ display:grid; grid-template-columns:62px minmax(0,1fr); gap:8px; }
.kv dt{ color:var(--faint); }
.kv dd{ margin:0; color:var(--ink); }
.kv .none{ color:var(--faint); }

.moves{ margin:0; padding:0; list-style:none; display:grid; gap:3px; font-size:12.5px; }
.moves li{ display:flex; align-items:center; gap:6px; }
.mdot{ width:8px; height:8px; border-radius:50%; flex:0 0 8px; }
.mname{ flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.mmeta{ font:500 11px var(--mono); color:var(--faint); white-space:nowrap; }

.warn{ color:var(--warn); font-size:12px; }
.hidden{ display:none !important; }
.noresults{ padding:40px 0; text-align:center; color:var(--faint); }

@media (max-width:900px){
  .masthead{ grid-template-columns:1fr; }
  .wrap{ padding:20px 14px 48px; }
}
</style>
</head>
<body>
<div class="wrap">

  <header class="masthead">
    <div>
      <p class="eyebrow">Run and Bun &#183; Trainer Sheet</p>
      <h1>Every Trainer<br>In The Run</h1>
      <p class="lede">All __T__ trainers and __M__ Pok&eacute;mon, in play order, split by badge and then by
      route. Each card is the set as the game runs it: species, level, held item, ability, nature and moves.</p>
    </div>
    <ul class="rules">
      <li><b>__S__ distinct species</b> across the run, from Route 102 to the Pok&eacute;mon League.</li>
      <li><b>Teams only.</b> No EVs, no computed stats, no AI commentary &#8212; just what each trainer brings.</li>
      <li><b>Move power</b> is the standard value for that move; Run and Bun retunes a few.</li>
      <li><b>Data</b> from <code>rnb_trainers.json</code>; rebuild with <code>build_rnb_doc2.py</code>.</li>
    </ul>
  </header>

  <nav class="ladder">__LADDER__</nav>

  <div class="toolbar">
    <input id="q" type="search" placeholder="Filter by trainer, species, item, ability or move&hellip;" autocomplete="off">
    <span class="hits" id="hits"></span>
  </div>

  __BODY__

  <p class="noresults hidden" id="noresults">Nothing matches that filter.</p>
</div>

<script src="rnb-site.js" defer></script>
<script>
(function(){
  var fights = [].slice.call(document.querySelectorAll('.fight'));
  fights.forEach(function(f){ f.dataset.hay = f.textContent.toLowerCase().replace(/\\s+/g,' '); });
  var q = document.getElementById('q'), hits = document.getElementById('hits'),
      none = document.getElementById('noresults'), t;
  function run(){
    var v = q.value.trim().toLowerCase(), n = 0;
    fights.forEach(function(f){
      var on = !v || f.dataset.hay.indexOf(v) !== -1;
      f.classList.toggle('hidden', !on); if(on) n++;
    });
    document.querySelectorAll('.split').forEach(function(s){
      var any = s.querySelector('.fight:not(.hidden)');
      s.classList.toggle('hidden', !any);
      s.querySelectorAll('h3.area').forEach(function(a){
        var sib = a.nextElementSibling, vis = false;
        while(sib && sib.classList.contains('fight')){ if(!sib.classList.contains('hidden')) vis = true; sib = sib.nextElementSibling; }
        a.classList.toggle('hidden', !vis);
      });
    });
    none.classList.toggle('hidden', n > 0);
    hits.textContent = n + ' of ' + fights.length + ' trainers';
  }
  q.addEventListener('input', function(){ clearTimeout(t); t = setTimeout(run, 130); });
  run();
})();
</script>
</body>
</html>
'''
doc = (doc.replace('__LADDER__', ladder)
          .replace('__BODY__', '\n'.join(body))
          .replace('__T__', str(TOTAL_T))
          .replace('__M__', '{:,}'.format(TOTAL_M))
          .replace('__S__', str(SPECIES)))

io.open(os.path.join(HERE, 'trainers.html'), 'w', encoding='utf-8').write(doc)
print('splits   : %d' % len(splits))
print('trainers : %d' % TOTAL_T)
print('pokemon  : %d' % TOTAL_M)
print('species  : %d' % SPECIES)
print('output   : trainers.html  (%.0f KB)' % (len(doc) / 1024))
