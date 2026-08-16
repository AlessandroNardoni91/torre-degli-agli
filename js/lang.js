/* Torre degli Agli — scelta della lingua.
   Ogni pagina contiene tre <section lang="en|it|es">. Questo script ne lascia
   visibile una sola. Ordine di scelta: ?lang=xx nell'indirizzo → lingua
   memorizzata sul telefono → lingua del browser → inglese.
   Senza JavaScript non succede nulla: si vedono tutte e tre le lingue. */
(function () {
  var LINGUE = ['en', 'it', 'es'];
  var html = document.documentElement;
  html.classList.remove('no-js');

  function daUrl() {
    var m = /[?&]lang=(en|it|es)\b/.exec(location.search);
    return m ? m[1] : null;
  }
  function daMemoria() {
    try { var v = localStorage.getItem('lingua'); return LINGUE.indexOf(v) >= 0 ? v : null; } catch (e) { return null; }
  }
  function daBrowser() {
    var l = (navigator.language || 'en').slice(0, 2).toLowerCase();
    return LINGUE.indexOf(l) >= 0 ? l : 'en';
  }

  function applica(lingua) {
    html.setAttribute('lang', lingua);
    try { localStorage.setItem('lingua', lingua); } catch (e) {}

    document.querySelectorAll('section[lang]').forEach(function (s) {
      s.hidden = s.getAttribute('lang') !== lingua;
    });
    var titolo = html.getAttribute('data-title-' + lingua);
    if (titolo) document.title = titolo + ' · Torre degli Agli';

    document.querySelectorAll('.lingue button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-lang') === lingua ? 'true' : 'false');
    });
    // bandierina e sigla della lingua corrente sul selettore chiuso
    var att = document.querySelector('.lingue button[data-lang="' + lingua + '"] img');
    var img = document.querySelector('.lingue summary img');
    var sigla = document.querySelector('.lingue summary .sigla');
    if (att && img) img.src = att.src;
    if (sigla) sigla.textContent = lingua.toUpperCase();
  }

  var tendina = document.querySelector('details.lingue');
  document.querySelectorAll('.lingue button').forEach(function (b) {
    b.addEventListener('click', function () {
      applica(b.getAttribute('data-lang'));
      if (tendina) tendina.open = false;
    });
  });
  // la tendina si chiude toccando fuori o con Esc
  document.addEventListener('click', function (e) {
    if (tendina && tendina.open && !tendina.contains(e.target)) tendina.open = false;
  });
  document.addEventListener('keydown', function (e) {
    if (tendina && e.key === 'Escape') tendina.open = false;
  });

  applica(daUrl() || daMemoria() || daBrowser());
})();
