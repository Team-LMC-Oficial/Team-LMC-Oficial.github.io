#!/usr/bin/env python3
"""Genera las imagenes de vista previa (Discord, X, WhatsApp...) de cada seccion de Team LMC.
Usa el logo de assets/avatars/banernew.png sobre un fondo rojo/negro, el nombre de la seccion en grande
y la direccion debajo. Medida 1200x630. Salida: assets/og/<seccion>.png (inicio.png, equipo.png, ...)
Los nombres salen del campo "n" del objeto DD en index.html.
Uso (desde la carpeta del sitio): python3 tools/make_og.py   y luego   python3 build_pages.py
Necesita Pillow:  pip install pillow"""
import json, re, pathlib
import pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1200, 630
RED = (179, 38, 45)
def font(size, weight=800, here=None):
    here = pathlib.Path(here or __file__).resolve().parent
    for p, var in ((here / 'BricolageGrotesque.ttf', True), (pathlib.Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'), False)):
        try:
            f = ImageFont.truetype(str(p), size)
            if var:
                vals = []
                for a in f.get_variation_axes():
                    n = a['name'].decode() if isinstance(a['name'], bytes) else a['name']
                    vals.append(weight if 'eight' in n else (min(max(size / 4, a['minimum']), a['maximum']) if 'ptical' in n else a['default']))
                f.set_variation_by_axes(vals)
            return f
        except Exception:
            continue
    return ImageFont.load_default()
def tw(d, text, f, tracking):
    return sum(d.textlength(c, font=f) for c in text) + tracking * (len(text) - 1)
def spaced(d, cx, cy, text, f, fill, tracking=0):
    x = cx - tw(d, text, f, tracking) / 2
    for c in text:
        d.text((x, cy), c, font=f, fill=fill, anchor='lm')
        x += d.textlength(c, font=f) + tracking
def fit(d, text, maxw, start, minsize, tracking, weight=800, here=None):
    s = start
    while True:
        f = font(s, weight, here)
        if tw(d, text, f, tracking) <= maxw or s <= minsize: return f, s
        s -= 4

root = pathlib.Path(__file__).resolve().parent.parent
SITE = 'team-lmc-oficial.github.io'
src = (root / 'index.html').read_text(encoding='utf-8')
DD = json.loads(re.search(r'/\*DD-START\*/const DD=(.*?);/\*DD-END\*/', src, re.S).group(1))
GREY = (176, 168, 170)

banner = Image.open(root / 'assets' / 'avatars' / 'banernew.png').convert('RGB')
k = banner.width / 1500
# fondo: el rojo oscuro del banner, difuminado, con rayas diagonales suaves como las de la web
bg = banner.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(48))
bg = Image.blend(bg, Image.new('RGB', (W, H), (0, 0, 0)), 0.38).convert('RGBA')
st = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
for x in range(-H, W + H, 120):
    sd.polygon([(x, H), (x + 60, H), (x + 60 + H * 0.7, 0), (x + H * 0.7, 0)], fill=(255, 255, 255, 9))
bg = Image.alpha_composite(bg, st)
# logo "TEAM LMC" recortado del banner con bordes suaves
lg = banner.crop((round(228 * k), round(58 * k), round(562 * k), round(362 * k)))
lh = 410; lg = lg.resize((round(lg.width * lh / lg.height), lh), Image.LANCZOS).convert('RGBA')
m = Image.new('L', lg.size, 0); ImageDraw.Draw(m).rectangle((26, 26, lg.width - 26, lg.height - 26), fill=255)
lg.putalpha(m.filter(ImageFilter.GaussianBlur(16)))
LX, LY = 36, (H - lh) // 2
bg.alpha_composite(lg, (LX, LY))
DIV = LX + lg.width + 26
CX = DIV + (W - DIV) // 2

out = root / 'assets' / 'og'
out.mkdir(parents=True, exist_ok=True)
for slug, d0 in DD.items():
    name = d0.get('n') or slug.replace('-', ' ').upper()
    im = bg.copy(); dr = ImageDraw.Draw(im)
    f, s = fit(dr, name, W - DIV - 90, 100, 46, 5)
    addr = SITE if slug == 'inicio' else f'{SITE}/{slug}/'
    fa = font(26, 500)
    while tw(dr, addr, fa, 1) > W - DIV - 70: fa = font(fa.size - 2, 500)
    items = [('rule', 3), ('gap', 34), ('txt', s), ('gap', 30), ('addr', 28)]
    total = sum(h for _, h in items); y = (H - total) // 2
    for kind, h in items:
        if kind == 'rule': dr.rectangle((CX - 28, y, CX + 28, y + 2), fill=(255, 48, 56))
        elif kind == 'txt': spaced(dr, CX, y + h // 2, name, f, (255, 255, 255), 5)
        elif kind == 'addr': spaced(dr, CX, y + h // 2, addr, fa, GREY, 1)
        y += h
    dr.rectangle((DIV, 120, DIV + 1, H - 120), fill=(255, 48, 56))      # divisor vertical rojo
    im.convert('RGB').save(out / f'{slug}.png', optimize=True)
    print('og:', slug, '->', name)
