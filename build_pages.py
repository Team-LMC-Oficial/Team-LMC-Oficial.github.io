#!/usr/bin/env python3
"""Genera una pagina real por seccion (/equipo/index.html, etc.) y 404.html
a partir de index.html. Cada pagina lleva su propio titulo y descripcion
(Discord, X, WhatsApp, etc. leen esas etiquetas sin ejecutar JavaScript).
Uso: python3 build_pages.py   (ejecutalo despues de editar index.html)
Las descripciones se editan en index.html, en el objeto DD."""
import json, re, pathlib, html

root = pathlib.Path(__file__).parent
src = (root / 'index.html').read_text(encoding='utf-8')
DD = json.loads(re.search(r'/\*DD-START\*/const DD=(.*?);/\*DD-END\*/', src, re.S).group(1))
SITE = 'https://team-lmc-oficial.github.io'
e = lambda v: html.escape(v, quote=True)

def page(n):
    d = DD[n]; url = SITE + ('/' if n == 'inicio' else '/%s/' % n)
    h = src
    subs = [
      (r'<title>.*?</title>', '<title>%s</title>' % e(d['t'])),
      (r'(<meta name="description" content=").*?(">)', r'\g<1>%s\g<2>' % e(d['d'])),
      (r'(<link rel="canonical" href=").*?(">)', r'\g<1>%s\g<2>' % url),
      (r'(<meta property="og:url" content=").*?(">)', r'\g<1>%s\g<2>' % url),
      (r'(<meta property="og:title" content=").*?(">)', r'\g<1>%s\g<2>' % e(d['t'])),
      (r'(<meta property="og:description" content=").*?(">)', r'\g<1>%s\g<2>' % e(d['d'])),
      (r'(<meta name="twitter:title" content=").*?(">)', r'\g<1>%s\g<2>' % e(d['t'])),
      (r'(<meta name="twitter:description" content=").*?(">)', r'\g<1>%s\g<2>' % e(d['d'])),
    ]
    for pat, rep in subs:
        h, k = re.subn(pat, lambda m, rep=rep: m.expand(rep), h, count=1, flags=re.S)
        assert k == 1, pat
    return h

for n in DD:
    if n == 'inicio': continue
    out = root / n / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page(n), encoding='utf-8')

# 404: misma app (con <base href="/">), cualquier ruta desconocida muestra el inicio y limpia la URL
h404 = page('inicio').replace('<base href="/">', '<base href="/">\n<meta name="robots" content="noindex">')
(root / '404.html').write_text(h404, encoding='utf-8')
print('listo:', ', '.join(n for n in DD if n != 'inicio'), '+ 404.html')
