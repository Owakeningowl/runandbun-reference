/* Run and Bun — shared cross-link bar + one theme choice across all pages */
(function () {
  var THEMES = ['light', 'dark', 'night'];
  var KEY = 'rnb-site-theme';
  var PAGES = [
    ['index.html',    'AI Reference'],
    ['trainers.html', 'Trainers'],
    ['dex.html',      'Dex'],
    ['calc.html',     'Calc']
  ];

  function apply(t) {
    if (THEMES.indexOf(t) < 0) t = 'dark';
    document.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem(KEY, t); } catch (e) {}
    var b = document.querySelectorAll('#rnb-bar .rnb-themes button');
    for (var i = 0; i < b.length; i++) b[i].classList.toggle('on', b[i].dataset.t === t);
  }

  var saved = 'dark';
  try { saved = localStorage.getItem(KEY) || 'dark'; } catch (e) {}
  document.documentElement.setAttribute('data-theme', saved);

  function build() {
    if (document.getElementById('rnb-bar')) return;
    var here = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    if (here === '') here = 'index.html';

    var bar = document.createElement('div');
    bar.id = 'rnb-bar';
    bar.innerHTML =
      '<a class="rnb-brand" href="index.html">RUN AND BUN</a>' +
      '<nav>' + PAGES.map(function (p) {
        return '<a href="' + p[0] + '"' + (p[0] === here ? ' class="rnb-current"' : '') +
               '>' + p[1] + '</a>';
      }).join('') + '</nav>' +
      '<div class="rnb-themes">' + THEMES.map(function (t) {
        return '<button type="button" data-t="' + t + '">' + t.toUpperCase() + '</button>';
      }).join('') + '</div>';

    document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-t]');
      if (b) apply(b.dataset.t);
    });

    /* the doc's own sticky sidebar/topbar need to clear this bar */
    function measure() {
      document.documentElement.style.setProperty('--rnb-bar-h', bar.offsetHeight + 'px');
    }
    measure();
    window.addEventListener('resize', measure);

    /* pages that are saved mirrors of remote sites get a marker class */
    if (here === 'dex.html' || here === 'calc.html') document.body.classList.add('rnb-mirror');

    apply(saved);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
