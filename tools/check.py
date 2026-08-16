"""Controllo del sito (sola lettura, non è un build).
Uso: python tools/check.py   (dalla cartella del repo)

Per ogni pagina HTML verifica:
  - 4 <section lang="en|it|es|fr"> (index.html è esente: è la scelta lingua)
  - stesso numero di h2 / img / a per lingua (parità delle traduzioni)
  - data-title-en/it/es presenti
  - <meta name="robots" content="noindex, nofollow">
  - link e immagini relativi che esistono davvero (case-sensitive, come su GitHub Pages)
  - nessun link assoluto al vecchio/nuovo dominio del sito
  - peso della pagina come la vede un telefono in inglese: HTML + css + js + immagini della sezione EN (senza le varianti pc)
  - testi vietati: indirizzo esatto, cellulari, "6º piano"
"""
import os, re, sys
from html.parser import HTMLParser

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINGUE = ('en', 'it', 'es', 'fr')
VIETATI = [r'Torre degli Agli,? 8\b', r'sixth floor', r'6th floor', r'sesto piano', r'6º piano', r'sexto piso',
           r'\+39 3(?!20 406 5709)\d\d \d{3} \d{4}']  # cellulari, tranne il numero dei medici (320 406 5709)

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sez = None; self.sezioni = {}; self.link = []; self.img = []; self.img_en = []; self.meta = {}; self.attr_html = {}
        self.titolo = ''; self.in_titolo = False; self.profondita = 0; self.prof_sez = None
    def handle_starttag(self, t, a):
        a = dict(a); self.profondita += 1
        if t == 'html': self.attr_html = a
        if t == 'meta' and a.get('name'): self.meta[a['name']] = a.get('content', '')
        if t == 'title': self.in_titolo = True
        if t == 'section' and a.get('lang') in LINGUE:
            self.sez = a['lang']; self.prof_sez = self.profondita
            self.sezioni[self.sez] = {'h2': 0, 'img': 0, 'a': 0}
        if self.sez and t in ('h2', 'img', 'a'):
            self.sezioni[self.sez][t] += 1
        if t == 'a' and a.get('href'): self.link.append(a['href'])
        if t == 'img' and a.get('src'):
            self.img.append(a['src'])
            if self.sez in (None, 'en'): self.img_en.append(a['src'])
        if t == 'source' and a.get('srcset'): self.img.append(a['srcset'])
        if t == 'link' and a.get('href'): self.link.append(a['href'])
        if t == 'script' and a.get('src'): self.link.append(a['src'])
        if t in ('meta', 'img', 'source', 'link', 'br', 'input'): self.profondita -= 1
    def handle_endtag(self, t):
        if t == 'title': self.in_titolo = False
        if t == 'section' and self.prof_sez == self.profondita: self.sez = None; self.prof_sez = None
        self.profondita -= 1
    def handle_data(self, d):
        if self.in_titolo: self.titolo += d

def peso(path):
    try: return os.path.getsize(path)
    except OSError: return 0

def esiste_case(path):
    """True se il file esiste con esattamente questo maiuscolo/minuscolo."""
    if not os.path.exists(path): return False
    d, f = os.path.split(path)
    return f in os.listdir(d or '.')

def main():
    pagine = []
    for cartella, sub, files in os.walk(RADICE):
        sub[:] = [s for s in sub if s not in ('.git', 'tools', 'node_modules')]
        for f in files:
            if f.endswith('.html'): pagine.append(os.path.join(cartella, f))
    errori = 0
    print(f"{'pagina':32} {'lang':4} {'h2':>3} {'img':>3} {'a':>3}  {'peso':>8}")
    for pg in sorted(pagine):
        rel = os.path.relpath(pg, RADICE).replace(os.sep, '/')
        src = open(pg, encoding='utf-8').read()
        p = P(); p.feed(src)
        probl = []
        if p.meta.get('robots', '').replace(' ', '') != 'noindex,nofollow': probl.append('manca noindex')
        if rel != 'index.html':
            if set(p.sezioni) != set(LINGUE): probl.append(f'sezioni lingua: {sorted(p.sezioni)}')
            else:
                for k in ('h2', 'img', 'a'):
                    v = {l: p.sezioni[l][k] for l in LINGUE}
                    if len(set(v.values())) > 1: probl.append(f'parità {k}: {v}')
            for l in LINGUE:
                if not p.attr_html.get('data-title-' + l): probl.append(f'manca data-title-{l}')
            if 'class="no-js"' not in src: probl.append('manca class="no-js" su <html>')
            if 'js/lang.js' not in src: probl.append('manca lang.js')
        for v in VIETATI:
            m = re.search(v, src)
            if m: probl.append(f'testo vietato: "{m.group(0)}"')
        # link e risorse
        base = os.path.dirname(pg); tot = peso(pg)
        for h in p.link + p.img:
            if h.startswith(('http://', 'https://')):
                if 'github.io' in h: probl.append(f'link assoluto al sito: {h}')
                continue
            if h.startswith(('#', 'mailto:', 'tel:')): continue
            h0 = h.split('#')[0].split('?')[0]
            if not h0: continue
            dest = os.path.normpath(os.path.join(base, h0))
            if not esiste_case(dest): probl.append(f'manca: {h}')
            elif h in p.img_en or h.endswith(('.css', '.js')): tot += peso(dest)
        for l in LINGUE:
            s = p.sezioni.get(l, {'h2': '-', 'img': '-', 'a': '-'})
            print(f"{rel if l == 'en' else '':32} {l:4} {s['h2']:>3} {s['img']:>3} {s['a']:>3}  {tot/1024:>7.0f}K" if l == 'en' else f"{'':32} {l:4} {s['h2']:>3} {s['img']:>3} {s['a']:>3}")
        for e in probl: print('   !!', e); errori += 1
    # file immagine non usati
    usati = set()
    for pg in pagine:
        p = P(); p.feed(open(pg, encoding='utf-8').read())
        for h in p.img + p.link:
            if not h.startswith(('http', '#', 'mailto', 'tel')):
                usati.add(os.path.normpath(os.path.join(os.path.dirname(pg), h.split('#')[0].split('?')[0])))
    css = open(os.path.join(RADICE, 'css', 'site.css'), encoding='utf-8').read()
    for u in re.findall(r'url\("([^"]+)"\)', css):
        usati.add(os.path.normpath(os.path.join(RADICE, 'css', u)))
    for cartella, sub, files in os.walk(os.path.join(RADICE, 'images')):
        for f in files:
            pth = os.path.join(cartella, f)
            if pth not in usati: print('   !! immagine non usata:', os.path.relpath(pth, RADICE)); errori += 1
    print(f"\n{len(pagine)} pagine, {errori} problemi")
    sys.exit(1 if errori else 0)

if __name__ == '__main__':
    main()
