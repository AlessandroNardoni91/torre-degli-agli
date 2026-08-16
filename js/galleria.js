/* Visore a schermo intero per la galleria.
   Le miniature sono link alle foto grandi: senza JavaScript il link apre la foto. */
(function () {
  var tutti = Array.prototype.slice.call(document.querySelectorAll('.griglia a'));
  if (!tutti.length) return;
  var link = tutti;   // viene ristretto alla griglia toccata (una per lingua)

  var visore = document.createElement('div');
  visore.className = 'visore';
  visore.hidden = true;
  visore.setAttribute('role', 'dialog');
  visore.setAttribute('aria-modal', 'true');
  visore.innerHTML =
    '<button type="button" class="chiudi" aria-label="Close">×</button>' +
    '<button type="button" class="prec" aria-label="Previous">‹</button>' +
    '<img alt="">' +
    '<button type="button" class="succ" aria-label="Next">›</button>' +
    '<div class="contatore"></div>';
  document.body.appendChild(visore);

  var img = visore.querySelector('img');
  var contatore = visore.querySelector('.contatore');
  var corrente = 0;

  function mostra(i) {
    corrente = (i + link.length) % link.length;
    img.src = link[corrente].getAttribute('href');
    img.alt = link[corrente].querySelector('img').alt;
    contatore.textContent = (corrente + 1) + ' / ' + link.length;
    visore.hidden = false;
    document.body.style.overflow = 'hidden';
    // precarica la successiva
    var pre = new Image(); pre.src = link[(corrente + 1) % link.length].getAttribute('href');
  }
  function chiudi() {
    visore.hidden = true;
    document.body.style.overflow = '';
  }

  tutti.forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      link = Array.prototype.slice.call(a.closest('.griglia').querySelectorAll('a'));
      mostra(link.indexOf(a));
    });
  });
  visore.querySelector('.chiudi').addEventListener('click', chiudi);
  visore.querySelector('.prec').addEventListener('click', function () { mostra(corrente - 1); });
  visore.querySelector('.succ').addEventListener('click', function () { mostra(corrente + 1); });
  visore.addEventListener('click', function (e) { if (e.target === visore) chiudi(); });
  document.addEventListener('keydown', function (e) {
    if (visore.hidden) return;
    if (e.key === 'Escape') chiudi();
    if (e.key === 'ArrowLeft') mostra(corrente - 1);
    if (e.key === 'ArrowRight') mostra(corrente + 1);
  });

  // scorrimento col dito
  var x0 = null;
  visore.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  visore.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (dx > 40) mostra(corrente - 1);
    else if (dx < -40) mostra(corrente + 1);
  });
})();
