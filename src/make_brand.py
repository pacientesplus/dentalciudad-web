#!/usr/bin/env python3
"""Kit de marca de Dental Ciudad a partir de los tres archivos que mandó Eduardo (25/10/2026):
isotipo (diente con la ciudad), logo vertical (isotipo + nombre) y logotipo (solo el nombre).

Genera en marca/:
  png/        isotipo, logotipo, logo vertical y horizontal, con fondo transparente, en varios tamaños; versión blanca
  svg/        logotipo e isotipo vectorizados (potrace), para la web y para imprenta
  web/        favicon.ico (16/32/48), favicon-96.png, favicon.svg, apple-touch-icon 180, icon-192, icon-512, og.jpg 1200x630
  redes/      Google (logo 720 y portada 1024x576), Instagram/Facebook 1080, WhatsApp 640
  paleta.png + LEEME.txt
Uso: python3 src/make_brand.py <isotipo.png> <logo-vertical.jpg> <logotipo.jpg>
"""
import os
import sys
import zipfile

import cv2
import numpy as np
import potrace
from PIL import Image, ImageDraw, ImageFont

SRC = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(SRC)
OUT = os.path.join(PROJ, "marca")

# Colores (medidos sobre el isotipo; los de texto se oscurecen hasta pasar el contraste AA de WCAG)
VERDE_LOGO = "#7DC41A"      # lima del logo: solo para el logo y detalles gráficos, nunca texto chico
VERDE_TEXTO = "#2E7D1F"     # mismo verde, oscuro: botones y enlaces (contraste > 4,5:1 sobre blanco)
GRIS_LOGO = "#5E5E5E"
CARBON = "#1B1B1B"          # el negro del logotipo, para títulos


def ensure(*parts):
    p = os.path.join(OUT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def key_white(img_rgb, tol=14):
    """Fondo blanco → transparente. Quita solo el blanco conectado al borde y suaviza el contorno."""
    h, w = img_rgb.shape[:2]
    near_white = (img_rgb.min(axis=2) >= 255 - tol * 2).astype(np.uint8)
    # inundar desde los bordes
    mask = np.zeros((h + 2, w + 2), np.uint8)
    flood = near_white.copy()
    bg = np.zeros_like(flood)
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for sx, sy in seeds:
        if flood[sy, sx]:
            m = np.zeros((h + 2, w + 2), np.uint8)
            cv2.floodFill(flood.copy(), m, (sx, sy), 2)
            bg |= m[1:-1, 1:-1]
    alpha = np.where(bg == 1, 0, 255).astype(np.uint8)
    # borde: píxeles de fondo pegados a la figura reciben alfa según lo que se alejan del blanco
    ring = cv2.dilate((alpha > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) - (alpha > 0).astype(np.uint8)
    whiteness = img_rgb.min(axis=2).astype(np.int32)
    soft = np.clip((255 - whiteness) * 255 // max(1, tol * 2), 0, 255).astype(np.uint8)
    alpha = np.where(ring == 1, soft, alpha)
    rgba = np.dstack([img_rgb, alpha])
    # des-blanquear los píxeles semitransparentes para que no quede halo claro
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    rgb = rgba[..., :3].astype(np.float32)
    rgb = np.where(a > 0, np.clip((rgb - 255 * (1 - a)) / np.maximum(a, 1e-3), 0, 255), rgb)
    rgba[..., :3] = rgb.astype(np.uint8)
    return rgba


def crop_alpha(rgba, pad_ratio=0.06):
    ys, xs = np.where(rgba[..., 3] > 8)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    pad = int(max(y1 - y0, x1 - x0) * pad_ratio)
    h, w = rgba.shape[:2]
    return rgba[max(0, y0 - pad):min(h, y1 + pad + 1), max(0, x0 - pad):min(w, x1 + pad + 1)]


def to_pil(rgba):
    return Image.fromarray(rgba, "RGBA")


def fit(img, box_w, box_h):
    im = img.copy()
    im.thumbnail((box_w, box_h), Image.LANCZOS)
    return im


def canvas(w, h, color=(255, 255, 255, 255)):
    return Image.new("RGBA", (w, h), color)


def paste_center(bg, fg, dy=0):
    x = (bg.width - fg.width) // 2
    y = (bg.height - fg.height) // 2 + dy
    bg.alpha_composite(fg, (x, y))
    return bg


def trace_mask(mask, scale):
    """mask: bool array → lista de paths SVG (coordenadas ya escaladas)."""
    bmp = potrace.Bitmap(~mask.astype(bool))  # potracer traza los ceros como figura
    path = bmp.trace(turdsize=6, alphamax=0.8, opticurve=True, opttolerance=0.2)
    d = []
    for curve in path:
        s = curve.start_point
        d.append(f"M{s.x * scale:.2f},{s.y * scale:.2f}")
        for seg in curve:
            e = seg.end_point
            if seg.is_corner:
                c = seg.c
                d.append(f"L{c.x * scale:.2f},{c.y * scale:.2f}L{e.x * scale:.2f},{e.y * scale:.2f}")
            else:
                c1, c2 = seg.c1, seg.c2
                d.append(f"C{c1.x * scale:.2f},{c1.y * scale:.2f} {c2.x * scale:.2f},{c2.y * scale:.2f} {e.x * scale:.2f},{e.y * scale:.2f}")
        d.append("Z")
    return "".join(d)


def svg_doc(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'{("<defs>" + defs + "</defs>") if defs else ""}{body}</svg>')


def classify(rgba):
    """Separa el isotipo en verde, gris/negro y transparente."""
    rgb = rgba[..., :3].astype(np.int32)
    a = rgba[..., 3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    opaque = a > 128
    green = opaque & (g > r + 25) & (g > b + 40)
    grey = opaque & ~green
    return green, grey


def contrast(hex1, hex2):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    l1, l2 = lum(hex1), lum(hex2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def main(iso_path, vert_path, word_path):
    iso = key_white(np.array(Image.open(iso_path).convert("RGB")))
    vert = key_white(np.array(Image.open(vert_path).convert("RGB")))
    word = key_white(np.array(Image.open(word_path).convert("RGB")))
    iso, vert, word = crop_alpha(iso, 0.04), crop_alpha(vert, 0.05), crop_alpha(word, 0.08)
    ISO, VERT, WORD = to_pil(iso), to_pil(vert), to_pil(word)

    # ---- PNG transparentes
    for size in (2048, 1024, 512):
        fit(ISO, size, size).save(ensure("png", f"isotipo-{size}.png"), optimize=True)
    VERT.save(ensure("png", "logo-vertical.png"), optimize=True)
    WORD.save(ensure("png", "logotipo-dentalciudad.png"), optimize=True)
    # logotipo blanco (lo negro pasa a blanco, el verde queda)
    wb = word.copy()
    dark = (wb[..., :3].max(axis=2) < 110) & (wb[..., 3] > 0)
    wb[dark, :3] = 255
    to_pil(wb).save(ensure("png", "logotipo-dentalciudad-blanco.png"), optimize=True)
    # logo horizontal: isotipo + logotipo
    iso_h = fit(ISO, 10000, 420)
    word_h = fit(WORD, 10000, 230)
    gap = 36
    H = canvas(iso_h.width + gap + word_h.width + 40, 460, (0, 0, 0, 0))
    H.alpha_composite(iso_h, (20, (H.height - iso_h.height) // 2))
    H.alpha_composite(word_h, (20 + iso_h.width + gap, (H.height - word_h.height) // 2 + 10))
    H.save(ensure("png", "logo-horizontal.png"), optimize=True)
    Hw = H.copy()
    arr = np.array(Hw)
    d2 = (arr[..., :3].max(axis=2) < 110) & (arr[..., 3] > 0)
    arr[d2, :3] = 255
    to_pil(arr).save(ensure("png", "logo-horizontal-blanco.png"), optimize=True)

    # ---- SVG (vectorizados)
    # logotipo: negro y verde por separado
    # se traza a 4x para que las curvas salgan fieles (la fuente mide solo ~200 px de alto)
    big = np.array(WORD.resize((WORD.width * 4, WORD.height * 4), Image.LANCZOS))
    wa = big[..., 3] > 128
    wrgb = big[..., :3].astype(np.int32)
    # cada píxel va al color de marca más cercano (así los bordes del JPG no quedan como contorno oscuro)
    # cada letra (componente conexo) entera va al color que domina adentro: así los bordes del JPG no dejan contorno
    sat_green = wrgb[..., 1] - np.maximum(wrgb[..., 0], wrgb[..., 2])
    n, labels = cv2.connectedComponents(wa.astype(np.uint8), connectivity=8)
    wgreen = np.zeros_like(wa)
    for k in range(1, n):
        comp = labels == k
        if (sat_green[comp] > 20).mean() > 0.5:
            wgreen |= comp
    wblack = wa & ~wgreen
    scale = 0.25
    body = (f'<path fill="{CARBON}" d="{trace_mask(wblack, scale)}"/>'
            f'<path fill="{VERDE_LOGO}" d="{trace_mask(wgreen, scale)}"/>')
    with open(ensure("svg", "logotipo-dentalciudad.svg"), "w") as f:
        f.write(svg_doc(word.shape[1], word.shape[0], body))
    body_w = body.replace(f'fill="{CARBON}"', 'fill="#FFFFFF"')
    with open(ensure("svg", "logotipo-dentalciudad-blanco.svg"), "w") as f:
        f.write(svg_doc(word.shape[1], word.shape[0], body_w))
    # isotipo: verde con degradé y gris con degradé
    g, gr = classify(iso)
    h, w = iso.shape[:2]
    defs = ('<linearGradient id="v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A6DC1E"/><stop offset="1" stop-color="#5FB80E"/></linearGradient>'
            '<linearGradient id="n" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8A8A8A"/><stop offset="1" stop-color="#111111"/></linearGradient>')
    body = f'<path fill="url(#v)" d="{trace_mask(g, 1.0)}"/><path fill="url(#n)" d="{trace_mask(gr, 1.0)}"/>'
    iso_svg = svg_doc(w, h, body, defs)
    with open(ensure("svg", "isotipo.svg"), "w") as f:
        f.write(iso_svg)

    # ---- Web: favicons e íconos
    def square_icon(size, pad_ratio=0.08, bg=None):
        c = canvas(size, size, bg or (0, 0, 0, 0))
        inner = int(size * (1 - 2 * pad_ratio))
        return paste_center(c, fit(ISO, inner, inner))
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    base = square_icon(256, 0.04)
    base.save(ensure("web", "favicon.ico"), sizes=ico_sizes)
    square_icon(96, 0.04).save(ensure("web", "favicon-96.png"), optimize=True)
    square_icon(180, 0.12, (255, 255, 255, 255)).convert("RGB").save(ensure("web", "apple-touch-icon.png"), optimize=True)
    square_icon(192, 0.08).save(ensure("web", "icon-192.png"), optimize=True)
    square_icon(512, 0.08).save(ensure("web", "icon-512.png"), optimize=True)
    square_icon(512, 0.2, (255, 255, 255, 255)).save(ensure("web", "icon-512-maskable.png"), optimize=True)
    with open(ensure("web", "favicon.svg"), "w") as f:
        f.write(iso_svg)
    # Open Graph 1200x630: logo horizontal sobre blanco con una línea verde
    og = canvas(1200, 630)
    paste_center(og, fit(H, 900, 300), -20)
    dr = ImageDraw.Draw(og)
    dr.rectangle([0, 600, 1200, 630], fill=VERDE_LOGO)
    og.convert("RGB").save(ensure("web", "og.jpg"), quality=90, optimize=True)

    # ---- Redes
    square_icon(720, 0.14, (255, 255, 255, 255)).convert("RGB").save(ensure("redes", "google-perfil-logo-720.png"), optimize=True)
    cover = canvas(1024, 576)
    paste_center(cover, fit(H, 800, 260))
    cover.convert("RGB").save(ensure("redes", "google-portada-1024x576.jpg"), quality=90)
    square_icon(1080, 0.16, (255, 255, 255, 255)).convert("RGB").save(ensure("redes", "instagram-facebook-perfil-1080.png"), optimize=True)
    square_icon(640, 0.16, (255, 255, 255, 255)).convert("RGB").save(ensure("redes", "whatsapp-perfil-640.png"), optimize=True)

    # ---- Paleta
    pal = canvas(1200, 300)
    dr = ImageDraw.Draw(pal)
    cols = [(VERDE_LOGO, "Verde logo (solo logo y detalles)"), (VERDE_TEXTO, "Verde texto y botones"),
            (GRIS_LOGO, "Gris logo"), (CARBON, "Carbón (títulos)")]
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    for i, (hx, name) in enumerate(cols):
        x = i * 300
        dr.rectangle([x, 0, x + 300, 200], fill=hx)
        dr.text((x + 14, 214), hx, fill="#111", font=font)
        dr.text((x + 14, 244), name, fill="#444", font=font)
        dr.text((x + 14, 272), f"sobre blanco {contrast(hx, '#FFFFFF'):.1f}:1", fill="#444", font=font)
    pal.convert("RGB").save(ensure("paleta.png"), optimize=True)

    with open(ensure("LEEME.txt"), "w", encoding="utf-8") as f:
        f.write(f"""KIT DE MARCA DENTAL CIUDAD (generado {__import__('datetime').date.today().isoformat()})

Colores
  Verde logo     {VERDE_LOGO}  solo para el logo y detalles gráficos (sobre blanco da {contrast(VERDE_LOGO, '#FFFFFF'):.1f}:1, no alcanza para texto)
  Verde texto    {VERDE_TEXTO}  botones, enlaces y texto en verde (sobre blanco {contrast(VERDE_TEXTO, '#FFFFFF'):.1f}:1, pasa WCAG AA)
  Gris logo      {GRIS_LOGO}
  Carbón         {CARBON}  títulos y texto (el negro del logotipo)

Carpetas
  png/    isotipo-2048/1024/512 · logotipo-dentalciudad (+ blanco) · logo-vertical · logo-horizontal (+ blanco). Fondo transparente.
  svg/    logotipo e isotipo vectorizados: para la web y para imprimir a cualquier tamaño.
  web/    favicon.ico (16/32/48) · favicon-96.png · favicon.svg · apple-touch-icon.png (180) · icon-192 · icon-512 · icon-512-maskable · og.jpg (1200x630, para compartir enlaces)
  redes/  google-perfil-logo-720 (logo de la ficha de Google) · google-portada-1024x576 · instagram-facebook-perfil-1080 · whatsapp-perfil-640

Qué va dónde
  Ficha de Google: logo = redes/google-perfil-logo-720.png · portada = redes/google-portada-1024x576.jpg
  Instagram / Facebook: redes/instagram-facebook-perfil-1080.png
  WhatsApp Business: redes/whatsapp-perfil-640.png
  Web: todo lo de web/ (la web nueva ya lo usa)
  Imprenta, cartelería, recetarios: svg/
""")

    # ---- ZIP para descargar
    zpath = os.path.join(PROJ, "DentalCiudad-kit-de-marca.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            for fn in files:
                p = os.path.join(root, fn)
                z.write(p, os.path.relpath(p, PROJ))
    print("listo:", OUT, "zip:", zpath)


if __name__ == "__main__":
    main(*sys.argv[1:4])
