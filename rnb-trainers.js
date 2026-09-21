(function () {
  var SEC = window.RNB_DATA.sections;
  var state = { q: '', sec: '', full: false };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function types(a) {
    return (a || []).map(function (t) {
      return '<span class="type t-' + t + '">' + t + '</span>';
    }).join('');
  }
  function splitName(n) {
    var i = n.indexOf('-');
    return i > 0 ? [n.slice(0, i), n.slice(i + 1).replace(/-/g, ' ')] : [n, ''];
  }

  var ROOT = 'https://play.pokemonshowdown.com/sprites/gen5/';
  function setSprite(img, slug) {
    var base = (slug || '').split('-')[0];
    var tried = false;
    img.onerror = function () {
      if (!tried && base && base !== slug) { tried = true; img.src = ROOT + base + '.png'; }
      else { img.onerror = null; img.style.visibility = 'hidden'; }
    };
    img.src = ROOT + (slug || 'x') + '.png';
  }

  /* search index */
  SEC.forEach(function (sc) {
    sc.trainers.forEach(function (t) {
      var bits = [t.n, t.a];
      t.team.forEach(function (m) {
        bits.push(m.n, m.i, m.ab, m.na);
        m.mv.forEach(function (x) { bits.push(x.n); });
      });
      t._hay = bits.join(' ').toLowerCase();
    });
  });

  function monCard(m) {
    var parts = splitName(m.n);
    var h = ['<div class="mon">'];
    h.push('<div class="top"><img alt="' + esc(m.n) + '" data-slug="' + esc(m.g) + '">');
    h.push('<div class="id"><div class="nm">' + esc(parts[0]) +
           (parts[1] ? '<span class="form">' + esc(parts[1]) + '</span>' : '') + '</div>' +
           '<div class="lv">Lv ' + m.lv + '</div>' +
           '<div class="types">' + types(m.ty) + '</div></div></div>');

    h.push('<div class="kv">');
    if (m.i) h.push('<div><span>Item</span> <b>' + esc(m.i) + '</b></div>');
    if (m.ab) h.push('<div><span>Abil</span> <b>' + esc(m.ab) + '</b></div>');
    if (m.na) h.push('<div><span>Nat</span> <b>' + esc(m.na) + '</b></div>');
    h.push('</div>');

    h.push('<div class="moves">' + m.mv.map(function (x) {
      return '<div class="mv"><span class="cat ' + x.c + '">' + x.c + '</span>' +
             '<span class="type t-' + x.t + '" style="width:50px;text-align:center">' +
             x.t.slice(0, 3) + '</span>' +
             '<span class="nmv">' + esc(x.n) + '</span></div>';
    }).join('') + '</div>');
    h.push('</div>');
    return h.join('');
  }

  function trainerCard(t) {
    var h = ['<article class="tcard" id="t-' + esc(t.k) + '">'];
    h.push('<header><h3>' + esc(t.n) + '</h3><div class="meta">');
    if (t.a) h.push('<span class="chip">' + esc(t.a) + '</span>');
    h.push('<span class="chip">' + t.team.length + ' mon' + (t.team.length === 1 ? '' : 's') + '</span>');
    var lv = t.team.map(function (m) { return m.lv; });
    var lo = Math.min.apply(null, lv), hi = Math.max.apply(null, lv);
    h.push('<span class="chip">Lv ' + (lo === hi ? lo : lo + '–' + hi) + '</span>');
    h.push('</div></header>');
    h.push('<div class="party">' + t.team.map(monCard).join('') + '</div>');
    h.push('</article>');
    return h.join('');
  }

  function matches(t) {
    if (state.full && t.team.length < 6) return false;
    if (state.q && t._hay.indexOf(state.q) < 0) return false;
    return true;
  }

  function render() {
    var list = document.getElementById('list');
    var nav = document.getElementById('nav-list');
    var html = [], navHtml = [], shown = 0, mons = 0;

    SEC.forEach(function (sc) {
      if (state.sec && sc.k !== state.sec) return;
      var hits = sc.trainers.filter(matches);
      if (!hits.length) return;
      shown += hits.length;
      hits.forEach(function (t) { mons += t.team.length; });

      html.push('<section class="section-head" id="s-' + sc.k + '"><h2>' + esc(sc.n) + '</h2>' +
                '<p>' + esc(sc.sub) + '</p></section>');
      navHtml.push('<li><a href="#s-' + sc.k + '">' + esc(sc.n) + '</a></li>');

      var area = null;
      hits.forEach(function (t) {
        if (t.a && t.a !== area) {
          area = t.a;
          html.push('<div class="area-head">' + esc(area) + '</div>');
        }
        html.push(trainerCard(t));
      });
    });

    list.innerHTML = html.length ? html.join('')
      : '<div class="empty">Nothing matches that search.</div>';
    nav.innerHTML = navHtml.join('');
    document.getElementById('count').textContent = shown + ' trainers · ' + mons + ' Pokémon';

    var imgs = list.querySelectorAll('img[data-slug]');
    for (var i = 0; i < imgs.length; i++) setSprite(imgs[i], imgs[i].dataset.slug);
    spy();
  }

  var spyTargets = [];
  function spy() {
    spyTargets = [].slice.call(document.querySelectorAll('.section-head'));
    onScroll();
  }
  function onScroll() {
    if (!spyTargets.length) return;
    var best = null;
    for (var i = 0; i < spyTargets.length; i++) {
      if (spyTargets[i].getBoundingClientRect().top <= 150) best = spyTargets[i];
      else break;
    }
    var links = document.querySelectorAll('#nav-list a');
    for (var j = 0; j < links.length; j++) links[j].classList.remove('active');
    if (best) {
      var a = document.querySelector('#nav-list a[href="#' + best.id + '"]');
      if (a) a.classList.add('active');
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  var sel = document.getElementById('sec');
  sel.innerHTML = '<option value="">All splits</option>' +
    SEC.map(function (s) { return '<option value="' + s.k + '">' + esc(s.n) + '</option>'; }).join('');
  sel.addEventListener('change', function (e) { state.sec = e.target.value; render(); });

  var t;
  document.getElementById('q').addEventListener('input', function (e) {
    clearTimeout(t);
    var v = e.target.value.trim().toLowerCase();
    t = setTimeout(function () { state.q = v; render(); }, 140);
  });
  document.getElementById('fullOnly').addEventListener('click', function (e) {
    state.full = !state.full; e.target.classList.toggle('on', state.full); render();
  });

  render();
})();
