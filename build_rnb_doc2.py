#!/usr/bin/env python3
"""Run and Bun trainer doc, in the Emerald split-doc layout (split-doc.css verbatim).

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
CSS = io.open(os.path.join(HERE, 'split-doc.css'), encoding='utf-8').read()

TYPE = {
    'Normal': '#9A9A7A', 'Fire': '#D9602B', 'Water': '#4A7BE0', 'Electric': '#E9C02A',
    'Grass': '#5FA83A', 'Ice': '#7CCCCB', 'Fighting': '#B0332A', 'Poison': '#984095',
    'Ground': '#D4B25C', 'Flying': '#8C7FD8', 'Psychic': '#E8507D', 'Bug': '#95A625',
    'Rock': '#AA9139', 'Ghost': '#6A5794', 'Dragon': '#6A3CF0', 'Dark': '#6A5446',
    'Steel': '#9C9CB8', 'Fairy': '#D883A8',
}

def ink_for(c):
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02x%02x%02x' % (int(r * .17), int(g * .17), int(b * .17))

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

shortest = {}
for s in sp:
    n = s['name']
    if n not in shortest or len(s['const']) < len(shortest[n]):
        shortest[n] = s['const']
lut = {}
for s in sp:
    base, c = shortest[s['name']], s['const']
    suf = '' if c == base else (c[len(base) + 1:] if c.startswith(base + '_') else '')
    lut.setdefault(norm(s['name']) + norm(suf), s)
    lut.setdefault(norm(c.replace('SPECIES_', '')), s)
ALIAS = {'darmanitangalar': 'darmanitangalarstandard', 'enamorust': 'enamorustherian'}
lut.setdefault('zygarde10', lut.get('zygarde'))

CAT = {'Physical': 'Phys', 'Special': 'Spec', 'Status': 'Stat'}
mlut = {norm(m['name']): m for m in mv}
SPRITE = 'https://play.pokemonshowdown.com/sprites/gen5/%s.png'

def types_of(n):
    s = lut.get(ALIAS.get(norm(n), norm(n)))
    return s['types'] if s else []

def slug(name):
    parts = name.replace('%', '').split('-')
    base = re.sub(r'[^a-z0-9]', '', parts[0].lower())
    if len(parts) == 1:
        return base
    form = re.sub(r'[^a-z0-9]', '', ''.join(parts[1:]).lower())
    return base + '-' + form if form else base

def move_of(name):
    m = mlut.get(norm(name))
    if m:
        return m['name'], m['type'], CAT.get(m['category'], 'Stat'), m['power'], m['priority']
    hp = re.match(r'hiddenpower(\w+)', norm(name))
    if hp:
        return name, hp.group(1).capitalize(), 'Spec', 60, 0
    return name, 'Normal', 'Stat', 0, 0

# ------------------------------------------------------------------ structure
order = []
for t in rnb:
    if t['split'] not in order:
        order.append(t['split'])

def tid(split, name, i):
    return re.sub(r'[^a-z0-9]+', '-', ('%s-%s-%d' % (split, name, i)).lower()).strip('-')

splits = []
for name in order:
    rows = [t for t in rnb if t['split'] == name]
    for i, t in enumerate(rows):
        t['_id'] = tid(name, t['name'], i)
        t['_n'] = i + 1
    legs = []
    for t in rows:
        a = t.get('area') or 'Pokémon League'
        if not legs or legs[-1][0] != a:
            legs.append((a, []))
        legs[-1][1].append(t)
    splits.append({
        'name': name,
        'key': re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-'),
        'rows': rows, 'legs': legs,
        'mons': sum(len(t['team']) for t in rows),
        'lo': min(m['level'] for t in rows for m in t['team']),
        'hi': max(m['level'] for t in rows for m in t['team']),
    })

TOTAL_T, TOTAL_M = len(rnb), sum(len(t['team']) for t in rnb)
SPECIES = len({m['name'] for t in rnb for m in t['team']})

def team_colour(t):
    ts = types_of(t['team'][0]['name'])
    return TYPE.get(ts[0], '#0B7453') if ts else '#0B7453'

# ------------------------------------------------------------------ render
def mon_card(m):
    ts = types_of(m['name'])
    pills = ''.join('<span class="type" style="--tb:%s;--tf:%s">%s</span>'
                    % (TYPE.get(t, '#9A9A7A'), ink_for(TYPE.get(t, '#9A9A7A')), t) for t in ts)
    moves = []
    for raw in m['moves']:
        nm, ty, cat, pw, pri = move_of(raw)
        prio = '<span class="prio">+%d</span>' % pri if pri > 0 else ''
        moves.append('<li><span class="mdot" style="background:%s" title="%s"></span>'
                     '<span class="mname">%s%s</span><span class="mmeta">%s %s</span></li>'
                     % (TYPE.get(ty, '#9A9A7A'), e(ty), e(nm), prio, cat,
                        pw if pw else '&#8212;'))
    return (
        '<article class="mon">\n'
        '  <header class="mon-head">\n'
        '    <img class="sprite" src="%s" alt="%s sprite" width="120" height="120" loading="lazy">\n'
        '    <div class="mon-id">\n      <h4>%s</h4>\n      <p class="lv">Lv %d</p>\n'
        '      <p class="types">%s</p>\n    </div>\n  </header>\n'
        '  <dl class="kv">'
        '<div><dt>Item</dt><dd>%s</dd></div>'
        '<div><dt>Ability</dt><dd>%s</dd></div>'
        '<div><dt>Nature</dt><dd>%s</dd></div></dl>\n'
        '  <ul class="moves">%s</ul>\n'
        '</article>'
    ) % (SPRITE % slug(m['name']), e(m['name']), e(m['name']), m['level'], pills,
         e(m['item']) if m.get('item') else '&#8212;',
         e(m.get('ability') or '—'), e(m.get('nature') or '—'), ''.join(moves))

def fight(t, split):
    lv = [m['level'] for m in t['team']]
    lo, hi = min(lv), max(lv)
    lead = t['team'][0]
    return (
        '<section class="gym" id="%s" style="--gym:%s">\n'
        '  <header class="gym-head">\n'
        '    <img class="leader" src="%s" alt="" width="112" height="112" loading="lazy">\n'
        '    <div class="gym-title">\n'
        '      <p class="eyebrow">Fight %d &#183; %s &#183; %s</p>\n'
        '      <h2>%s</h2>\n'
        '      <div class="facts">'
        '<span class="fact"><b>%d</b> Pok&#233;mon</span>'
        '<span class="fact"><b>Lv %s</b> team</span>'
        '<span class="fact format-singles"><b>%s</b></span>'
        '</div>\n    </div>\n  </header>\n'
        '  <div class="team">\n%s\n  </div>\n'
        '</section>'
    ) % (t['_id'], team_colour(t), SPRITE % slug(lead['name']), t['_n'],
         e(t.get('area') or 'Pokémon League'), e(split['name'].replace(' Split', '')),
         e(t['name']), len(t['team']),
         str(lo) if lo == hi else '%d&#8211;%d' % (lo, hi),
         'Doubles' if '[Double]' in t['name'] else 'Singles',
         '\n'.join(mon_card(m) for m in t['team']))

tabs, pages = [], []
for s in splits:
    tabs.append('<button type="button" class="split-tab" data-k="%s"><b>%s</b>'
                '<span>%d fights &#183; Lv %d&#8211;%d</span></button>'
                % (s['key'], e(s['name'].replace(' Split', '')), len(s['rows']), s['lo'], s['hi']))

    legs = ''.join(
        '<div class="leg"><div class="leg-name">%s<small>%d fights</small></div>'
        '<div class="leg-stops">%s</div></div>'
        % (e(a), len(group),
           ''.join('<a class="stop" href="#%s" style="--gym:%s"><img src="%s" alt="" loading="lazy">'
                   '<div><b>%s</b><span>%d &#183; %d mons</span></div></a>'
                   % (x['_id'], team_colour(x), SPRITE % slug(x['team'][0]['name']),
                      e(x['name']), x['_n'], len(x['team']))
                   for x in group))
        for a, group in s['legs'])

    inner = []
    for a, group in s['legs']:
        inner.append('<h3 class="area-rule">%s</h3>' % e(a))
        for x in group:
            inner.append(fight(x, s))

    pages.append(
        '<section class="split-page" id="sp-%s" data-k="%s" hidden>\n'
        '  <h2 class="split-rule"><small>%s</small>%d trainers &#183; %d Pok&#233;mon &#183; Lv %d&#8211;%d</h2>\n'
        '  <nav class="route" aria-label="Fights in order">%s</nav>\n'
        '  <div class="toolbar"><input class="q" type="search" '
        'placeholder="Filter this split by trainer, species, item, ability or move&hellip;" autocomplete="off">'
        '<span class="hits"></span></div>\n'
        '%s\n  <p class="noresults" hidden>Nothing in this split matches that filter.</p>\n'
        '</section>'
        % (s['key'], s['key'], e(s['name']), len(s['rows']), s['mons'], s['lo'], s['hi'],
           legs, '\n'.join(inner)))

EXTRA = '''


/* --- one split at a time --- */
.split-tabs{ display:grid; grid-template-columns:repeat(auto-fit,minmax(142px,1fr)); gap:4px;
  margin:24px 0 0; }
.split-tab{ display:grid; gap:2px; text-align:left; padding:10px 11px 9px; cursor:pointer;
  background:var(--surface); border:1px solid var(--rule); border-top:4px solid var(--rule);
  color:var(--muted); font-family:var(--body); }
.split-tab:hover{ background:var(--sunken); color:var(--ink); }
.split-tab b{ font:700 16px/1.15 var(--display); text-transform:uppercase; color:var(--ink); }
.split-tab span{ font:500 11px var(--mono); color:var(--faint); }
.split-tab[aria-selected="true"]{ border-top-color:var(--accent); background:var(--accent-soft); }
.split-tab[aria-selected="true"] b{ color:var(--accent); }
.split-page[hidden]{ display:none; }
.split-page .split-rule{ margin-top:30px; }

/* --- shared cross-link bar, painted in this doc's own tokens --- */
:root[data-theme="night"]{
  --ground:#0E1412; --surface:#151D19; --sunken:#1B2520; --ink:#E3ECE7; --muted:#9AAAA1;
  --faint:#77867E; --rule:#28332D; --accent:#48C898; --accent-soft:#16372B; --warn:#F08A62;
}
#rnb-bar{ position:sticky; top:0; z-index:400; display:flex; align-items:center; gap:14px;
  flex-wrap:wrap; padding:9px 16px; background:var(--surface); border-bottom:1px solid var(--rule);
  font-family:var(--body); }
#rnb-bar .rnb-brand{ font:700 15px/1 var(--display); letter-spacing:.06em; text-transform:uppercase;
  color:var(--accent); text-decoration:none; white-space:nowrap; }
#rnb-bar nav{ display:flex; gap:3px; flex-wrap:wrap; }
#rnb-bar nav a{ padding:5px 10px; font-size:13px; color:var(--muted); text-decoration:none;
  border:1px solid transparent; white-space:nowrap; }
#rnb-bar nav a:hover{ background:var(--sunken); color:var(--ink); }
#rnb-bar nav a.rnb-current{ color:var(--accent); background:var(--accent-soft); border-color:var(--accent); font-weight:600; }
#rnb-bar .rnb-themes{ display:flex; gap:4px; margin-left:auto; }
#rnb-bar .rnb-themes button{ padding:5px 8px; font:500 10px var(--mono); letter-spacing:.08em;
  border:1px solid var(--rule); background:var(--ground); color:var(--faint); cursor:pointer; }
#rnb-bar .rnb-themes button:hover{ color:var(--ink); }
#rnb-bar .rnb-themes button.on{ background:var(--accent); border-color:var(--accent); color:var(--surface); }
.toolbar{ top:44px !important; }

/* --- Run and Bun: teams shown larger than the split docs --- */
.team{ grid-template-columns:repeat(auto-fit,minmax(310px,1fr)) !important; }
.sprite{ width:120px; height:120px; }
.mon{ padding:18px 18px 16px; gap:12px; }
.mon-id h4{ font-size:28px; }
.lv{ font-size:14px; }
.type{ font-size:12px; padding:4px 8px; }
.kv{ font-size:14.5px; }
.moves{ font-size:14.5px; padding:10px 0; }
.mname{ font-size:14.5px; }
.mmeta{ font-size:12.5px; }
.gym-head h2{ font-size:clamp(28px,3.2vw,40px); }

.split-rule{ font-size:clamp(26px,3.4vw,40px); text-transform:uppercase; line-height:1;
  margin:52px 0 4px; padding-bottom:10px; border-bottom:2px solid var(--ink); }
.split-rule small{ display:block; font:500 12px var(--mono); letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin-bottom:6px; }
.area-rule{ font-size:16px; text-transform:uppercase; letter-spacing:.12em; color:var(--accent);
  margin:30px 0 10px; padding-bottom:6px; border-bottom:1px solid var(--rule); }

.toolbar{ position:sticky; top:0; z-index:30; display:flex; gap:10px; flex-wrap:wrap;
  align-items:center; margin:22px 0 0; padding:10px 12px;
  background:var(--surface); border:1px solid var(--rule); }
.toolbar input{ flex:1 1 280px; padding:8px 11px; font:15px var(--body); color:var(--ink);
  background:var(--ground); border:1px solid var(--rule); }
.toolbar input:focus{ outline:2px solid var(--accent); outline-offset:-2px; }
.toolbar .hits{ font:500 12px var(--mono); color:var(--faint); }
.hidden{ display:none !important; }
.noresults{ padding:40px 0; text-align:center; color:var(--faint); }
'''

doc = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Run and Bun &#8212; Trainer Sheet</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
__CSS__
__EXTRA__
</style>
</head>
<body>
<div id="rnb-bar">
  <a class="rnb-brand" href="index.html">Run and Bun</a>
  <nav>
    <a href="index.html">AI Reference</a>
    <a href="trainers.html" class="rnb-current">Trainers</a>
    <a href="dex.html">Dex</a>
    <a href="calc.html">Calc</a>
  </nav>
  <div class="rnb-themes">
    <button type="button" data-t="light">LIGHT</button>
    <button type="button" data-t="dark">DARK</button>
    <button type="button" data-t="night">NIGHT</button>
  </div>
</div>
<div class="wrap">
  <header class="masthead">
    <div>
      <h1><small>Run and Bun &#183; Trainer Sheet</small>Every Trainer In The Run</h1>
      <p class="lede">All __T__ trainers and __M__ Pok&#233;mon, in play order, split by badge and then by route.
      Each card is the set as the game runs it: species, level, types, held item, ability, nature and moves.</p>
      <p class="dex">Roster: <b>__S__</b> distinct species across the run, from Route 102 to the Pok&#233;mon League.</p>
    </div>
    <ul class="rules">
      <li><b>Teams only.</b> No EVs, no computed stats, no AI commentary &#8212; just what each trainer brings.</li>
      <li><b>Ten badge splits</b>, each broken down by route in the order you meet them.</li>
      <li><b>Move power</b> is the standard value for that move; Run and Bun retunes a few.</li>
      <li><b>Rebuild</b> from <code>rnb_trainers.json</code> with <code>build_rnb_doc2.py</code>.</li>
    </ul>
  </header>

  <nav class="split-tabs" aria-label="Badge splits">__TABS__</nav>

__PAGES__
</div>
<script>
(function(){
  var K='rnb-site-theme', T=['light','dark','night'], saved='dark';
  try{ saved=localStorage.getItem(K)||'dark'; }catch(e){}
  function apply(v){ if(T.indexOf(v)<0)v='dark';
    document.documentElement.setAttribute('data-theme',v);
    try{ localStorage.setItem(K,v); }catch(e){}
    [].forEach.call(document.querySelectorAll('#rnb-bar .rnb-themes button'),function(b){
      b.classList.toggle('on', b.dataset.t===v); });
  }
  document.getElementById('rnb-bar').addEventListener('click',function(e){
    var b=e.target.closest('button[data-t]'); if(b) apply(b.dataset.t); });
  apply(saved);
})();
(function(){
  var pages=[].slice.call(document.querySelectorAll('.split-page')),
      tabs=[].slice.call(document.querySelectorAll('.split-tab')),
      KEY='rnb-split';

  pages.forEach(function(p){
    [].forEach.call(p.querySelectorAll('.gym'),function(f){
      f.dataset.hay=f.textContent.toLowerCase().replace(/\s+/g,' ');
    });
  });

  function filter(page){
    var q=page.querySelector('.q'), hits=page.querySelector('.hits'),
        none=page.querySelector('.noresults'),
        fights=[].slice.call(page.querySelectorAll('.gym')),
        v=q.value.trim().toLowerCase(), n=0;
    fights.forEach(function(f){
      var on=!v||f.dataset.hay.indexOf(v)!==-1;
      f.hidden=!on; if(on)n++;
    });
    [].forEach.call(page.querySelectorAll('.area-rule'),function(a){
      var s=a.nextElementSibling,vis=false;
      while(s&&s.classList.contains('gym')){ if(!s.hidden)vis=true; s=s.nextElementSibling; }
      a.hidden=!vis;
    });
    none.hidden=n>0;
    hits.textContent=n+' of '+fights.length+' trainers';
  }

  function show(k,scroll){
    var hit=false;
    pages.forEach(function(p){ var on=p.dataset.k===k; p.hidden=!on; if(on)hit=true; });
    tabs.forEach(function(b){ b.setAttribute('aria-selected',String(b.dataset.k===k)); });
    if(!hit) return false;
    try{ localStorage.setItem(KEY,k); }catch(e){}
    if(scroll) window.scrollTo(0,0);
    return true;
  }

  tabs.forEach(function(b){
    b.addEventListener('click',function(){ show(b.dataset.k,true); });
  });
  pages.forEach(function(p){
    var q=p.querySelector('.q'),t;
    q.addEventListener('input',function(){ clearTimeout(t); t=setTimeout(function(){ filter(p); },130); });
    filter(p);
  });

  /* a deep link to a fight opens the split that holds it */
  function fromHash(){
    var h=location.hash.slice(1); if(!h) return false;
    var el=document.getElementById(h); if(!el) return false;
    var page=el.closest('.split-page'); if(!page) return false;
    show(page.dataset.k,false);
    if(el!==page) setTimeout(function(){ el.scrollIntoView(); },0);
    return true;
  }
  window.addEventListener('hashchange',fromHash);

  var saved=null; try{ saved=localStorage.getItem(KEY); }catch(e){}
  if(!fromHash() && !(saved&&show(saved,false))) show(pages[0].dataset.k,false);
})();
</script>
</body>
</html>
'''
doc = (doc.replace('__CSS__', CSS).replace('__EXTRA__', EXTRA)
          .replace('__TABS__', ''.join(tabs)).replace('__PAGES__', '\n'.join(pages))
          .replace('__T__', str(TOTAL_T)).replace('__M__', '{:,}'.format(TOTAL_M))
          .replace('__S__', str(SPECIES)))
io.open(os.path.join(HERE, 'trainers.html'), 'w', encoding='utf-8').write(doc)
print('trainers %d · pokemon %d · species %d · %.0f KB'
      % (TOTAL_T, TOTAL_M, SPECIES, len(doc) / 1024))
