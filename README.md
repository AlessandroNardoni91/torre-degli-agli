# Torre degli Agli — guida per gli ospiti

Sito statico (HTML/CSS/JS puri, niente build né framework) che l'ospite apre dal QR in casa.
Online su GitHub Pages: <https://alessandronardoni91.github.io/torre-degli-agli/>
Il sito è `noindex,nofollow`: lo trova solo chi ha il link/QR.

## Struttura

```
index.html                 ingresso: benvenuto + scelta lingua → home.html?lang=xx
home.html                  menu delle sezioni
arrivo.html check-in.html regole.html trasporti.html galleria.html manuali.html
consigli/                  index, ristoranti, dintorni
elettrodomestici/          index + una pagina per apparecchio
css/site.css               unico foglio di stile (colori, font, dimensioni)
js/lang.js                 scelta lingua; js/galleria.js visore foto
fonts/                     Nunito e Dancing Script (self-hosted)
images/                    foto, screenshot, mappe, schemi, bandiere
manuali/                   PDF dei manuali
tools/check.py             controllo automatico (sola lettura)
```

## Le lingue

Ogni pagina è **un solo file** con quattro blocchi:

```html
<section lang="en"> … </section>
<section lang="it"> … </section>
<section lang="es"> … </section>
<section lang="fr"> … </section>
```

`js/lang.js` mostra solo la lingua scelta (`?lang=` → memoria del browser → lingua del telefono → inglese) e la ricorda da una pagina all'altra. Senza JavaScript si vedono tutte e quattro.
Titolo della scheda per lingua: attributi `data-title-en/it/es/fr` sul tag `<html>`.

## Come si modifica

- **Correggere una frase**: aprire il file HTML, cercare la frase, correggerla **nelle quattro sezioni** (o solo in quella lingua se è una traduzione).
- **Nuova pagina**: copiare una pagina simile, cambiare titolo (`data-title-*`, `<h1>`), contenuto delle quattro sezioni e aggiungere il pulsante nel menu (`home.html` o `elettrodomestici/index.html`).
- **Immagini**: solo file già ridimensionati (foto ≤1600 px, screenshot ≤720 px), nomi ASCII minuscoli. Le coppie telefono/PC vanno in `<picture>`.
- **Confronto fra le lingue**: `python tools/lingue.py` → verifica che le quattro lingue offrano le stesse pagine, gli stessi link, le stesse immagini e gli stessi titoli, e segnala le differenze volute.
- **Prima di pubblicare**: `python tools/check.py` dalla cartella del repo → deve dire `0 problemi` (controlla parità fra le lingue, link e immagini esistenti, `noindex`, testi vietati come indirizzo esatto e cellulari, pesi).
- Anteprima locale: `python -m http.server 8765` nella cartella e aprire <http://localhost:8765/>.

Ogni push su `main` va online da solo in un paio di minuti (GitHub Pages).

## QR

Il QR in casa punta ancora al vecchio sito (`torredegliagli.github.io/knowledge-base`), che rimbalzerà qui con un redirect.
Per ristampare il QR con l'indirizzo nuovo, generarlo per l'URL **`https://alessandronardoni91.github.io/torre-degli-agli/`** (l'ingresso: la lingua la sceglie l'ospite).

## Privacy

Non pubblicare: indirizzo esatto (via e numero civico), piano, numeri di cellulare. `tools/check.py` li intercetta.
