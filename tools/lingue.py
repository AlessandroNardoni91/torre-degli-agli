"""Confronto fra le lingue (sola lettura).
Uso: python tools/lingue.py   (dalla cartella del repo)

Per ogni pagina verifica che le quattro lingue offrano le STESSE cose:
  - le stesse sezioni lingua presenti (en, it, es, fr) e il titolo scheda per ognuna
  - gli stessi link (stessi file di destinazione, nello stesso ordine)
  - le stesse immagini, gli stessi titoli h1/h2, lo stesso numero di paragrafi/elenchi
  - nessuna sezione lasciata identica a un'altra lingua (traduzione dimenticata)
E poi, sull'intero sito:
  - ogni pagina raggiungibile dai menu esiste in tutte le lingue
  - nessuna pagina esiste solo in una lingua
"""
import os, re, sys
from collections import OrderedDict

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINGUE = ('en', 'it', 'es', 'fr')
NOMI = {'en': 'inglese', 'it': 'italiano', 'es': 'spagnolo', 'fr': 'francese'}


def pagine():
    for cartella, _, files in os.walk(RADICE):
        if os.path.basename(cartella) in ('.git', 'tools', 'manuali', 'fonts', 'images'):
            continue
        for f in sorted(files):
            if f.endswith('.html'):
                rel = os.path.relpath(os.path.join(cartella, f), RADICE).replace('\\', '/')
                if rel != 'index.html':          # l'ingresso è la scelta lingua, non ha sezioni
                    yield rel


def sezioni(testo):
    """Le quattro sezioni lingua, senza i commenti HTML."""
    testo = re.sub(r'<!--.*?-->', '', testo, flags=re.S)
    out = OrderedDict()
    for m in re.finditer(r'<section lang="(\w+)">(.*?)</section>', testo, re.S):
        out[m.group(1)] = m.group(2)
    return out


def dati(html):
    """Cosa deve coincidere fra le lingue.
    Le note "lo schema è in italiano" esistono solo in alcune lingue: contate a parte."""
    note = re.findall(r'<p class="nota">(.*?)</p>', html, re.S)
    senza_note = re.sub(r'<p class="nota">.*?</p>', '', html, flags=re.S)
    return {
        'link': re.findall(r'<a [^>]*href="([^"]+)"', html),
        'immagini': re.findall(r'<img [^>]*src="([^"]+)"', html) + re.findall(r'srcset="([^"]+)"', html),
        'h1': len(re.findall(r'<h1[\s>]', html)),
        'h2': len(re.findall(r'<h2[\s>]', html)),
        'paragrafi': len(re.findall(r'<p[\s>]', senza_note)),
        'voci elenco': len(re.findall(r'<li[\s>]', html)),
        'elenchi': len(re.findall(r'<[uo]l[\s>]', html)),
        'figure': len(re.findall(r'<figure[\s>]', html)),
        'note': len(note),
    }


def testo_puro(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()


problemi = []
info = []
righe = []
destinazioni = {l: set() for l in LINGUE}

for rel in sorted(pagine()):
    percorso = os.path.join(RADICE, rel.replace('/', os.sep))
    testo = open(percorso, encoding='utf-8').read()
    sez = sezioni(testo)
    mancanti = [l for l in LINGUE if l not in sez]
    if mancanti:
        problemi.append(f'{rel}: manca la sezione in {", ".join(NOMI[l] for l in mancanti)}')
        continue
    for l in LINGUE:
        if not re.search(r'data-title-%s="[^"]+"' % l, testo):
            problemi.append(f'{rel}: manca il titolo della scheda in {NOMI[l]}')

    d = {l: dati(sez[l]) for l in LINGUE}
    for chiave in d['it']:
        valori = {l: d[l][chiave] for l in LINGUE}
        if len({str(v) for v in valori.values()}) == 1:
            continue
        if chiave == 'link':
            # devono essere tanti quanti e puntare agli stessi siti; una versione tradotta
            # dello stesso sito (es. /english-menu/) è una differenza voluta, non un errore
            if len({len(v) for v in valori.values()}) > 1:
                problemi.append(f'{rel}: numero di link diverso -> ' +
                                ', '.join(f'{NOMI[l]}: {len(valori[l])}' for l in LINGUE))
            else:
                for i in range(len(valori['it'])):
                    url = {l: valori[l][i] for l in LINGUE}
                    if len(set(url.values())) == 1:
                        continue
                    host = {u.split('/')[2] if u.startswith('http') else u for u in url.values()}
                    if len(host) > 1:
                        problemi.append(f'{rel}: il link n.{i+1} porta a siti diversi -> ' +
                                        ', '.join(f'{NOMI[l]}: {url[l]}' for l in LINGUE))
                    else:
                        info.append(f'{rel}: link n.{i+1} allo stesso sito ma a pagine diverse -> ' +
                                    ', '.join(f'{NOMI[l]}: {url[l]}' for l in LINGUE))
        elif chiave == 'immagini':
            # EN e IT/ES/FR usano schemi in lingue diverse: conta solo il numero
            if len({len(v) for v in valori.values()}) > 1:
                problemi.append(f'{rel}: numero di immagini diverso -> ' +
                                ', '.join(f'{NOMI[l]}: {len(valori[l])}' for l in LINGUE))
        elif chiave == 'note':
            con = [l for l in LINGUE if valori[l]]
            info.append(f'{rel}: riga di avvertenza in più (di solito "lo schema è in italiano") '
                        f'presente in {", ".join(NOMI[l] for l in con)}')
        else:
            problemi.append(f'{rel}: {chiave} in numero diverso -> ' +
                            ', '.join(f'{NOMI[l]}: {valori[l]}' for l in LINGUE))

    for l in LINGUE:
        for altra in LINGUE:
            if l < altra and testo_puro(sez[l]) == testo_puro(sez[altra]) and len(testo_puro(sez[l])) > 60:
                problemi.append(f'{rel}: {NOMI[l]} e {NOMI[altra]} hanno lo stesso testo (traduzione dimenticata?)')

    for l in LINGUE:
        for href in d[l]['link']:
            if href.startswith(('http', 'tel:', 'mailto:', '#')):
                continue
            base = os.path.normpath(os.path.join(os.path.dirname(rel), href.split('#')[0].split('?')[0]))
            destinazioni[l].add(base.replace('\\', '/'))

    righe.append((rel, [len(testo_puro(sez[l]).split()) for l in LINGUE], len(d['it']['link'])))

# pagine raggiungibili: devono essere le stesse in tutte le lingue
solo_in_alcune = set()
for l in LINGUE:
    solo_in_alcune |= destinazioni[l]
for d_ in sorted(solo_in_alcune):
    lingue_con = [l for l in LINGUE if d_ in destinazioni[l]]
    if len(lingue_con) != len(LINGUE):
        problemi.append(f'la pagina "{d_}" è raggiungibile solo in {", ".join(NOMI[l] for l in lingue_con)}')
    if d_.endswith('.html') and not os.path.exists(os.path.join(RADICE, d_.replace('/', os.sep))):
        problemi.append(f'link a una pagina che non esiste: {d_}')

print(f'{"pagina":34}{"parole (en/it/es/fr)":26}link')
for rel, parole, nlink in righe:
    print(f'{rel:34}{"/".join(str(p) for p in parole):26}{nlink}')

print()
if info:
    print('differenze volute (controllate a mano):')
    for i in info:
        print('  ·', i)
    print()
if problemi:
    print(f'{len(problemi)} problemi:')
    for p in problemi:
        print('  !!', p)
else:
    print(f'{len(righe)} pagine: le quattro lingue offrono le stesse pagine e gli stessi contenuti.')
sys.exit(1 if problemi else 0)
