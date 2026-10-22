#!/usr/bin/env python3
"""Genera la web de Dental Ciudad en public/.

Una sola web (dentalciudad.ar) con una página por sede y una por tratamiento.
Lo que se edita: textos y datos en este archivo, estilos en site.css, comportamiento en site.js.
public/ se genera con `python3 src/build.py` y no se edita a mano.
"""
import hashlib
import html
import json
import os
import shutil
from datetime import date

SRC = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(SRC)
OUT = os.path.join(PROJ, "public")
SITE = "https://dentalciudad.ar"
BRAND = "Dental Ciudad"
TODAY = date.today().isoformat()
CONSULTA = "$20.000"

esc = lambda s: html.escape(str(s), quote=True)

# ---------------------------------------------------------------- datos
SEDES = {
    "microcentro": {
        "nombre": "Microcentro",
        "calle": "Av. Córdoba 679, piso 3, oficina C",
        "cp": "C1054",
        "ref": "a pasos de Galerías Pacífico",
        "llegada": "Anunciate con el portero: vas a Odontología, piso 3, oficina C.",
        "wa": "5491124577716",
        "tel_label": "11 2457-7716",
        "tel": "+541124577716",
        "maps": "https://www.google.com/maps/search/?api=1&query=Dental%20Ciudad%20Av.%20C%C3%B3rdoba%20679%20CABA",
        "geo": (-34.5993, -58.3756),
        "horario": "",  # FALTA: horario de la sede (lo pasa Eduardo)
    },
    "once": {
        "nombre": "Once",
        "calle": "Av. Rivadavia 3033, planta baja 6",
        "cp": "C1203",
        "ref": "frente a Plaza Miserere",
        "llegada": "Tocá el timbre de la planta baja 6 y te abrimos.",
        "wa": "5491161460061",
        "tel_label": "11 6146-0061",
        "tel": "+541161460061",
        "maps": "https://www.google.com/maps/search/?api=1&query=Dental%20Ciudad%20Av.%20Rivadavia%203033%20CABA",
        "geo": (-34.6097, -58.4067),
        "horario": "",  # FALTA
    },
}

# Opciones del formulario. "valor" es interno: solo lo ve Google para saber qué consulta vale más.
MOTIVOS = [
    ("consulta", "Consulta", 3),
    ("implantes", "Implantes", 10),
    ("protesis", "Prótesis", 8),
    ("carillas", "Carillas", 8),
    ("ortodoncia", "Ortodoncia", 6),
    ("conducto", "Conducto", 4),
    ("arreglo", "Arreglo", 2),
    ("urgencia", "Dolor o urgencia", 3),
    ("limpieza", "Limpieza o control", 1),
]
PAGOS = [("particular", "Particular (efectivo, transferencia o tarjeta)"), ("obra", "Con obra social o prepaga")]
CUANDO = [("hoy", "Hoy", 1.0), ("semana", "Esta semana", 0.9), ("mes", "Este mes", 0.6)]

# Páginas de tratamiento: un anuncio de Google por tratamiento manda a su página.
TRATAMIENTOS = [
    {
        "slug": "implantes", "motivo": "implantes",
        "title": "Implantes dentales en Microcentro y Once",
        "h1": "Implantes dentales",
        "lead": "Para volver a morder con confianza donde hoy falta un diente.",
        "desc": "Implantes dentales en CABA, sedes Microcentro y Once. Atención particular. Consulta con el especialista en implantes.",
        "body": [
            "Un implante es una raíz nueva: un tornillo chico de titanio que se coloca en el hueso y sobre el que va el diente. "
            "Funciona como el taco que ponés en la pared para que el cuadro no se caiga: el diente queda firme y no depende de los dientes de al lado.",
            "Sirve cuando falta uno o varios dientes, y también para sostener una prótesis que hoy se mueve.",
            "En la consulta el especialista revisa el hueso con imágenes, te dice si sos candidato y te arma el plan con tiempos y valor.",
        ],
    },
    {
        "slug": "protesis", "motivo": "protesis",
        "title": "Prótesis dentales: flexibles, removibles y fijas",
        "h1": "Prótesis dentales",
        "lead": "Flexibles, removibles (las de ganchos) o completas, hechas a tu medida.",
        "desc": "Prótesis dentales flexibles, removibles y completas en CABA, sedes Microcentro y Once. Atención particular.",
        "body": [
            "La prótesis reemplaza los dientes que faltan. La flexible es liviana y se adapta a la encía, sin ganchos de metal a la vista; "
            "la removible de ganchos (la que mucha gente llama arañita) se apoya en los dientes que tenés; la completa reemplaza toda la arcada.",
            "Tomamos las medidas con escáner 3D, sin la pasta de impresión de siempre, para que encaje mejor desde la primera prueba.",
            "En la consulta te muestran qué tipo te conviene según los dientes que tenés y el doctor te da el valor.",
        ],
    },
    {
        "slug": "carillas", "motivo": "carillas",
        "title": "Carillas y diseño de sonrisa",
        "h1": "Carillas y diseño de sonrisa",
        "lead": "Para la sonrisa que hoy tapás con la mano en las fotos.",
        "desc": "Carillas de cerámica, zirconio y resina en CABA, sedes Microcentro y Once. Diseño de sonrisa. Atención particular.",
        "body": [
            "Una carilla es una lámina finita que se pega en la cara de adelante del diente. Cambia color, forma y largo. "
            "La de cerámica es como una taza de loza: no se mancha con el café ni con el mate.",
            "Hay de cerámica, de zirconio y de resina. La elección depende de cómo están tus dientes y de cuánto querés que dure.",
            "Antes de empezar se hace el diseño digital para que veas cómo te va a quedar. El valor final lo da el doctor en la consulta.",
        ],
    },
    {
        "slug": "ortodoncia", "motivo": "ortodoncia",
        "title": "Ortodoncia: brackets y alineadores invisibles",
        "h1": "Ortodoncia",
        "lead": "Brackets o alineadores invisibles para ordenar los dientes.",
        "desc": "Ortodoncia con brackets y alineadores invisibles en CABA, sedes Microcentro y Once. Atención particular.",
        "body": [
            "La ortodoncia mueve los dientes de a poco hasta su lugar. Con brackets es una guía pegada a los dientes; "
            "con alineadores son placas transparentes que te sacás para comer.",
            "Sirve para dientes torcidos, separados o montados, y para cuando la mordida no cierra bien.",
            "En la consulta la ortodoncista revisa tu mordida, te explica las opciones y los tiempos, y te da el valor.",
        ],
    },
    {
        "slug": "conducto", "motivo": "conducto",
        "title": "Tratamiento de conducto (endodoncia)",
        "h1": "Tratamiento de conducto",
        "lead": "Para salvar el diente en vez de sacarlo.",
        "desc": "Tratamiento de conducto (endodoncia) en CABA, sedes Microcentro y Once. Atención particular.",
        "body": [
            "Cuando la caries llega al nervio, el diente duele con el frío, con el calor o solo. El conducto limpia el interior del diente y lo sella, "
            "como cuando se cambia un caño tapado sin tirar la pared.",
            "Se hace con anestesia y con radiografías en el momento, para ver el trabajo mientras se hace.",
            "En la consulta te dicen si el diente se puede salvar y el doctor te da el valor.",
        ],
    },
    {
        "slug": "urgencias", "motivo": "urgencia",
        "title": "Urgencias dentales: dolor de muela",
        "h1": "Dolor de muela o urgencia",
        "lead": "Si te duele, escribinos y te buscamos un turno lo antes posible.",
        "desc": "Atención de urgencias dentales y dolor de muela en CABA, sedes Microcentro y Once. Atención particular.",
        "body": [
            "Muela que late, encía hinchada, un diente partido o una corona que se salió: escribinos con una foto si podés.",
            "Primero se calma el dolor y se ve qué lo causa. Después se arma el tratamiento.",
            "Atendemos de manera particular. La consulta tiene un costo de " + CONSULTA + ".",
        ],
    },
]

FAQ = [
    ("¿Cuánto cuesta la consulta?", "La consulta tiene un costo de " + CONSULTA + ". Por WhatsApp te damos valores aproximados de tu tratamiento; el valor final te lo da el doctor personalmente en la consulta, después de revisarte."),
    ("¿Trabajan con obra social o prepaga?", "Por ahora atendemos de manera particular. Se puede pagar en efectivo, por transferencia o con tarjeta."),
    ("¿Quién me atiende?", "Cada área tiene su especialista: implantes y cirugía, prótesis, estética, ortodoncia y conductos."),
    ("¿Quién responde el WhatsApp?", "Una persona de la recepción de la sede que elijas."),
]

# ---------------------------------------------------------------- utilidades
def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def hashed(name):
    with open(os.path.join(SRC, name), "rb") as f:
        data = f.read()
    h = hashlib.md5(data).hexdigest()[:8]
    base, ext = os.path.splitext(name)
    rel = f"assets/{base}.{h}{ext}"
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, rel), "wb") as f:
        f.write(data)
    return "/" + rel


def ld_json():
    org_id = SITE + "/#org"
    graph = [{
        "@type": "Organization", "@id": org_id, "name": BRAND, "url": SITE + "/",
        "email": "dentalciudad1@gmail.com",
    }]
    for slug, s in SEDES.items():
        node = {
            "@type": "Dentist", "@id": f"{SITE}/{slug}/#sede", "name": f"{BRAND} {s['nombre']}",
            "url": f"{SITE}/{slug}/", "telephone": s["tel"], "parentOrganization": {"@id": org_id},
            "priceRange": "$$", "currenciesAccepted": "ARS", "paymentAccepted": "Efectivo, transferencia, tarjeta",
            "address": {"@type": "PostalAddress", "streetAddress": s["calle"], "addressLocality": "Ciudad Autónoma de Buenos Aires",
                        "postalCode": s["cp"], "addressRegion": "CABA", "addressCountry": "AR"},
            "geo": {"@type": "GeoCoordinates", "latitude": s["geo"][0], "longitude": s["geo"][1]},
        }
        graph.append(node)
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def head(title, desc, path, assets, noindex=False):
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="format-detection" content="telephone=no, address=no">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
{robots}
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:locale" content="es_AR">
<meta name="theme-color" content="#0E4D64">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{assets['css']}">
{ld_json() if not noindex else ''}
</head>
"""


def topbar():
    return f"""<header class="top wrap">
<a class="mark" href="/">{BRAND}</a>
<nav class="topnav" aria-label="Sedes"><a href="/microcentro/">Microcentro</a><a href="/once/">Once</a></nav>
</header>"""


def chips(name, items, checked=None, required=True):
    out = []
    for i, it in enumerate(items):
        key, label = it[0], it[1]
        chk = " checked" if checked == key else ""
        out.append(f'<label class="chip"><input type="radio" name="{name}" value="{esc(key)}"{chk}><span>{esc(label)}</span></label>')
    return "".join(out)


def form(motivo=None, sede=None):
    return f"""<section class="card" id="turno" aria-labelledby="h-form">
<h2 id="h-form">Pedí tu consulta</h2>
<p class="sub">Cuatro toques y se abre el WhatsApp de la sede con tu mensaje listo.</p>
<form class="form" id="lead-form" novalidate>
<fieldset aria-describedby="err-motivo"><legend>¿Qué querés resolver?</legend><div class="chips">{chips("motivo", MOTIVOS, motivo)}</div><p class="error" id="err-motivo" hidden>Elegí qué querés resolver.</p></fieldset>
<fieldset aria-describedby="err-pago"><legend>¿Cómo pensás pagar?</legend><div class="chips">{chips("pago", PAGOS)}</div><p class="error" id="err-pago" hidden>Elegí cómo pensás pagar.</p></fieldset>
<div class="note" id="obra-note" hidden role="status">Por ahora atendemos de manera particular. Si querés venir igual, podés pagar en efectivo, por transferencia o con tarjeta.</div>
<fieldset aria-describedby="err-cuando"><legend>¿Cuándo querés venir?</legend><div class="chips">{chips("cuando", CUANDO)}</div><p class="error" id="err-cuando" hidden>Elegí cuándo querés venir.</p></fieldset>
<fieldset aria-describedby="err-sede"><legend>¿Qué sede te queda mejor?</legend><div class="chips">{chips("sede", [(k, f"{v['nombre']} · {v['ref']}") for k, v in SEDES.items()], sede)}</div><p class="error" id="err-sede" hidden>Elegí una sede.</p></fieldset>
<div class="price"><strong>La consulta tiene un costo de {CONSULTA}.</strong> Por WhatsApp te damos valores aproximados de tu tratamiento; el valor final te lo da el doctor personalmente en la consulta.</div>
<button class="btn" type="submit">Enviar por WhatsApp</button>
<p class="hint">Se abre WhatsApp con tu mensaje escrito. <a href="/privacidad/">Privacidad</a></p>
</form>
<div class="done" id="done" hidden role="status">
<p class="done-title">Tu mensaje está listo</p>
<p>Si WhatsApp no se abrió, tocá el botón.</p>
<p class="code">Código de tu consulta: <strong id="done-code"></strong></p>
<a class="btn" id="done-open" href="#" rel="noopener">Abrir WhatsApp</a>
</div>
</section>"""


def page_data():
    data = {
        "sedes": {k: {"nombre": v["nombre"], "wa": v["wa"]} for k, v in SEDES.items()},
        "motivos": {k: {"label": l, "valor": val} for k, l, val in MOTIVOS},
        "pagos": {k: l for k, l in PAGOS},
        "cuando": {k: {"label": l, "factor": f} for k, l, f in CUANDO},
    }
    return '<script type="application/json" id="dc-data">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def trust():
    return """<section class="block" aria-labelledby="h-trust">
<h2 id="h-trust">Por qué Dental Ciudad</h2>
<ul class="ticks">
<li>Más de 8 años atendiendo en Capital.</li>
<li>Más del 98% de reseñas positivas en Google Maps.</li>
<li>Un especialista por área: implantes, prótesis, estética, ortodoncia y conductos.</li>
<li>Medidas con escáner 3D y radiografías digitales en el momento.</li>
<li>Atención particular: efectivo, transferencia o tarjeta.</li>
</ul>
</section>"""


def tratamientos_grid():
    items = "".join(f'<li><a href="/{t["slug"]}/"><strong>{esc(t["h1"])}</strong><span>{esc(t["lead"])}</span></a></li>' for t in TRATAMIENTOS)
    return f"""<section class="block" aria-labelledby="h-trat"><h2 id="h-trat">Tratamientos</h2><ul class="grid">{items}</ul></section>"""


def sedes_block():
    cards = []
    for slug, s in SEDES.items():
        hor = f"<p>{esc(s['horario'])}</p>" if s["horario"] else ""
        cards.append(f"""<li class="sede"><h3><a href="/{slug}/">Sede {esc(s['nombre'])}</a></h3>
<p>{esc(s['calle'])}, {esc(s['ref'])}.</p>{hor}
<p class="links"><a href="{esc(s['maps'])}" target="_blank" rel="noopener">Cómo llegar</a> <a href="https://wa.me/{s['wa']}" target="_blank" rel="noopener">WhatsApp {esc(s['tel_label'])}</a></p></li>""")
    return f"""<section class="block" aria-labelledby="h-sedes"><h2 id="h-sedes">Sedes</h2><ul class="sedes">{''.join(cards)}</ul></section>"""


def faq_block():
    items = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ)
    return f'<section class="block" aria-labelledby="h-faq"><h2 id="h-faq">Preguntas</h2><div class="faq">{items}</div></section>'


def foot(assets):
    return f"""<footer class="foot wrap">
<p>{BRAND} · Microcentro: {esc(SEDES['microcentro']['calle'])} · Once: {esc(SEDES['once']['calle'])}</p>
<p><a href="/privacidad/">Privacidad</a> · <button type="button" class="linkbtn" data-cookie-settings>Cookies</button></p>
</footer>
<a class="sticky btn" href="#turno" id="sticky">Pedí tu consulta</a>
{page_data()}
<script src="{assets['js']}" defer></script>
</body></html>
"""


def page(path, title, desc, hero_h1, hero_lead, body_html, assets, motivo=None, sede=None, extra=""):
    return (head(title, desc, path, assets) + "<body>\n" + topbar() +
            f"""<main class="wrap">
<section class="hero"><h1>{esc(hero_h1)}</h1><p class="lead">{esc(hero_lead)}</p>
<p class="pills"><span>Atención particular</span><span>Consulta {CONSULTA}</span><span>Microcentro y Once</span></p></section>
{form(motivo, sede)}
{body_html}
{extra}
</main>
""" + foot(assets))


# ---------------------------------------------------------------- páginas
def build():
    if os.path.isdir(OUT):
        for name in os.listdir(OUT):
            p = os.path.join(OUT, name)
            if name in ("_headers", "_redirects", "robots.txt", "favicon.svg"):
                continue
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    assets = {"css": hashed("site.css"), "js": hashed("site.js")}
    urls = []

    write("index.html", page(
        "/", f"{BRAND} | Dentistas en Microcentro y Once, CABA",
        "Clínica odontológica en Microcentro y Once: implantes, prótesis, carillas, ortodoncia y conductos. Atención particular. Pedí tu consulta por WhatsApp.",
        "Dentistas en Microcentro y Once",
        "Implantes, prótesis, carillas, ortodoncia y conductos, con un especialista por área.",
        tratamientos_grid() + trust() + sedes_block() + faq_block(), assets))
    urls.append("/")

    for slug, s in SEDES.items():
        hor = f"<p>{esc(s['horario'])}</p>" if s["horario"] else ""
        body = f"""<section class="block" aria-labelledby="h-llegar"><h2 id="h-llegar">Cómo llegar</h2>
<p class="big">{esc(s['calle'])}</p><p>{esc(s['ref'].capitalize())}. {esc(s['llegada'])}</p>{hor}
<p class="links"><a href="{esc(s['maps'])}" target="_blank" rel="noopener">Abrir en el mapa</a> <a href="https://wa.me/{s['wa']}" target="_blank" rel="noopener">WhatsApp {esc(s['tel_label'])}</a></p></section>"""
        write(f"{slug}/index.html", page(
            f"/{slug}/", f"Dentista en {s['nombre']}, CABA | {BRAND}",
            f"Dental Ciudad sede {s['nombre']}: {s['calle']}, {s['ref']}. Implantes, prótesis, carillas, ortodoncia y conductos. Atención particular.",
            f"Dentista en {s['nombre']}", f"{s['calle']}, {s['ref']}.",
            body + tratamientos_grid() + trust() + faq_block(), assets, sede=slug))
        urls.append(f"/{slug}/")

    for t in TRATAMIENTOS:
        body = '<section class="block prose">' + "".join(f"<p>{esc(p)}</p>" for p in t["body"]) + "</section>"
        write(f"{t['slug']}/index.html", page(
            f"/{t['slug']}/", f"{t['title']} | {BRAND}", t["desc"], t["h1"], t["lead"],
            body + trust() + sedes_block() + faq_block(), assets, motivo=t["motivo"]))
        urls.append(f"/{t['slug']}/")

    priv = f"""<section class="block prose"><h1>Privacidad</h1>
<p>Responsable: {BRAND}, sedes {esc(SEDES['microcentro']['calle'])} y {esc(SEDES['once']['calle'])}, Ciudad Autónoma de Buenos Aires. Contacto: dentalciudad1@gmail.com.</p>
<p>El formulario no pide tu nombre ni tu teléfono. Lo que elegís (qué querés resolver, cómo pensás pagar, cuándo querés venir y la sede) se escribe en un mensaje de WhatsApp que mandás vos, junto con un código de consulta. Ese mensaje lo recibe la recepción de la sede para responderte y coordinar el turno.</p>
<p>La página usa Google Analytics y Google Ads para saber cuánta gente la visita y qué anuncios traen consultas. A Google se le avisa que hubo una consulta y su valor estimado, sin tu nombre, tu teléfono ni datos de salud.</p>
<p>Podés pedir acceso, corrección o eliminación de tus datos escribiendo al WhatsApp de cualquiera de las sedes o a dentalciudad1@gmail.com (Ley 25.326). La Agencia de Acceso a la Información Pública es el órgano de control de esa ley y atiende denuncias y reclamos.</p>
<p>Actualizada el {date.today().strftime('%d/%m/%Y')}.</p></section>"""
    write("privacidad/index.html", head(f"Privacidad | {BRAND}", "Política de privacidad de Dental Ciudad.", "/privacidad/", assets) +
          "<body>\n" + topbar() + f'<main class="wrap">{priv}</main>' + foot(assets))
    urls.append("/privacidad/")

    write("404.html", head(f"Página no encontrada | {BRAND}", "Página no encontrada.", "/404", assets, noindex=True) +
          "<body>\n" + topbar() + '<main class="wrap"><section class="block prose"><h1>Esta página no existe</h1><p><a href="/">Volver al inicio</a></p></section></main>' + foot(assets))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("listo:", OUT, len(urls), "páginas")


if __name__ == "__main__":
    build()
