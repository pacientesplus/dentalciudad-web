#!/usr/bin/env python3
"""Genera la web de Dental Ciudad en public/.

Una sola web (dentalciudad.ar) con una página por sede y una por tratamiento.
Lo que se edita: textos y datos en este archivo, estilos en site.css, comportamiento en site.js, marca en marca/.
public/ se genera con `python3 src/build.py` y no se edita a mano. Cloudflare Pages publica public/ tal cual.

Reglas que cumple (ver PLAN.md): Ley 17.132 (sin precios de consulta, sin "gratis", sin cuotas anunciadas, sin
testimonios copiados, sin "especialista" salvo registrados, sin superlativos ni promesas), Google (ficha y web con los
mismos datos, Dentist por sede, sin reseñas propias en datos estructurados), WCAG 2.2 AA, Core Web Vitals.
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
MARCA = os.path.join(PROJ, "marca")
LOGO_VARIANTE = ""   # "" = logo original verde lima (elegido por Eduardo 25/10); "verde-agua" = la variante corrida al verde agua
SITE = "https://dentalciudad.ar"
BRAND = "Dental Ciudad"
TODAY = date.today().isoformat()
ANIOS = "8"
INSTAGRAM = "https://www.instagram.com/dentalciudad1/"
EMAIL = "dentalciudad1@gmail.com"
RESPONSABLE = ""   # FALTA: "Od. Nombre Apellido, M.N. 12345" (responsable para el pie; lo pasa Eduardo)

esc = lambda s: html.escape(str(s), quote=True)

# ---------------------------------------------------------------- sedes (datos iguales a la ficha de Google, 25/10/2026)
SEDES = {
    "microcentro": {
        "nombre": "Microcentro",
        "calle": "Av. Córdoba 679, piso 3, oficina C",
        "cp": "C1054AAF",
        "ref": "a pasos de Galerías Pacífico",
        "llegada": "Edificio con ascensor. Anunciate con el portero: vas a Odontología, piso 3, oficina C.",
        "acceso": "Con ascensor",
        "wa": "5491124577716",
        "tel_label": "11 2457-7716",
        "tel": "+541124577716",
        "place_id": "ChIJIZBFbgHLvJUR4VjFR-ApDE4",
        "geo": (-34.5986251, -58.3765316),
        "rating": ("4,9", "93"),   # nota y cantidad de reseñas en Google al 25/10/2026 (actualizar de vez en cuando)
        "horario": [("Lunes", "9:00 a 18:30"), ("Martes a viernes", "9:00 a 18:00"), ("Sábados", "9:00 a 13:00"), ("Domingos", "cerrado")],
        "horario_ld": [("Monday", "09:00", "18:30"), (["Tuesday", "Wednesday", "Thursday", "Friday"], "09:00", "18:00"), ("Saturday", "09:00", "13:00")],
        "sabado_urgencias": "9:00 a 13:00",
    },
    "once": {
        "nombre": "Once",
        "calle": "Av. Rivadavia 3033, planta baja 6",
        "cp": "C1203AAC",
        "ref": "frente a Plaza Miserere",
        "llegada": "Está en planta baja, sin escaleras. Tocá el timbre de la planta baja 6 y te abrimos.",
        "acceso": "Planta baja",
        "wa": "5491161460061",
        "tel_label": "11 6146-0061",
        "tel": "+541161460061",
        "place_id": "ChIJ1xIPwEvLvJURMba3r37Xgmo",
        "geo": (-34.6102394, -58.4093233),
        "rating": ("4,8", "157"),
        "horario": [("Lunes", "9:00 a 17:00"), ("Martes a sábados", "9:00 a 18:00"), ("Domingos", "cerrado")],
        "horario_ld": [("Monday", "09:00", "17:00"), (["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "09:00", "18:00")],
        "sabado_urgencias": "9:00 a 18:00",
    },
}
for s in SEDES.values():
    s["maps"] = f"https://www.google.com/maps/search/?api=1&query={BRAND.replace(' ', '%20')}%20{s['nombre']}&query_place_id={s['place_id']}"
    s["reviews"] = s["maps"]

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
    ("ninos", "Niños", 3),
]
PAGOS = [("particular", "Particular (efectivo, transferencia o tarjeta)"), ("obra", "Con obra social o prepaga")]
CUANDO = [("hoy", "Hoy", 1.0), ("semana", "Esta semana", 0.9), ("mes", "Este mes", 0.6)]

PRECIO_TXT = ("Atención particular. El valor de la consulta y valores aproximados de tu tratamiento te los pasamos por "
              "WhatsApp; el valor final te lo da el doctor personalmente en la consulta.")

# Páginas de tratamiento: un anuncio de Google por tratamiento manda a su página.
TRATAMIENTOS = [
    {"slug": "implantes", "motivo": "implantes", "title": "Implantes dentales en Microcentro y Once", "h1": "Implantes dentales",
     "lead": "Para volver a morder con confianza donde hoy falta un diente.",
     "desc": "Implantes dentales en CABA, sedes Microcentro y Once. Atención particular. Consulta con el odontólogo que se dedica a implantes.",
     "body": [
         "Un implante es una raíz nueva: un tornillo chico de titanio que se coloca en el hueso y sobre el que va el diente. "
         "Funciona como el taco que ponés en la pared para que el cuadro no se caiga: el diente queda firme y no depende de los dientes de al lado.",
         "Sirve cuando falta uno o varios dientes, y también para sostener una prótesis que hoy se mueve.",
         "En la consulta el odontólogo revisa el hueso con imágenes, te dice si sos candidato y te arma el plan con tiempos y valor."]},
    {"slug": "protesis", "motivo": "protesis", "title": "Prótesis dentales: flexibles, removibles y fijas", "h1": "Prótesis dentales",
     "lead": "Flexibles, removibles (las de ganchos) o completas, hechas a tu medida.",
     "desc": "Prótesis dentales flexibles, removibles y completas en CABA, sedes Microcentro y Once. Atención particular.",
     "body": [
         "La prótesis reemplaza los dientes que faltan. La flexible es liviana y se adapta a la encía, sin ganchos de metal a la vista; "
         "la removible de ganchos (la que mucha gente llama arañita) se apoya en los dientes que tenés; la completa reemplaza toda la arcada.",
         "Tomamos las medidas con escáner 3D, sin la pasta de impresión de siempre.",
         "En la consulta te muestran qué tipo te conviene según los dientes que tenés y el doctor te da el valor."]},
    {"slug": "carillas", "motivo": "carillas", "title": "Carillas y diseño de sonrisa", "h1": "Carillas y diseño de sonrisa",
     "lead": "Para la sonrisa que hoy tapás con la mano en las fotos.",
     "desc": "Carillas de cerámica, zirconio y resina en CABA, sedes Microcentro y Once. Diseño de sonrisa. Atención particular.",
     "body": [
         "Una carilla es una lámina finita que se pega en la cara de adelante del diente. Cambia color, forma y largo. "
         "La de cerámica es como una taza de loza: no se mancha con el café ni con el mate.",
         "Hay de cerámica, de zirconio y de resina. La elección depende de cómo están tus dientes y de qué buscás.",
         "Antes de empezar se hace el diseño digital para que veas cómo te va a quedar. El valor final lo da el doctor en la consulta."]},
    {"slug": "ortodoncia", "motivo": "ortodoncia", "title": "Ortodoncia: brackets y alineadores invisibles", "h1": "Ortodoncia",
     "lead": "Brackets o alineadores invisibles para ordenar los dientes.",
     "desc": "Ortodoncia con brackets y alineadores invisibles en CABA, sedes Microcentro y Once. Atención particular.",
     "body": [
         "La ortodoncia mueve los dientes de a poco hasta su lugar. Con brackets es una guía pegada a los dientes; "
         "con alineadores son placas transparentes que te sacás para comer.",
         "Sirve para dientes torcidos, separados o montados, y para cuando la mordida no cierra bien.",
         "En la consulta revisan tu mordida, te explican las opciones y los tiempos, y te dan el valor."]},
    {"slug": "conducto", "motivo": "conducto", "title": "Tratamiento de conducto (endodoncia)", "h1": "Tratamiento de conducto",
     "lead": "Para salvar el diente en vez de sacarlo.",
     "desc": "Tratamiento de conducto (endodoncia) en CABA, sedes Microcentro y Once. Atención particular.",
     "body": [
         "Cuando la caries llega al nervio, el diente duele con el frío, con el calor o solo. El conducto limpia el interior del diente y lo sella, "
         "como cuando se cambia un caño tapado sin tirar la pared.",
         "Se hace con anestesia y con radiografías en el momento, para ver el trabajo mientras se hace.",
         "En la consulta te dicen si el diente se puede salvar y el doctor te da el valor."]},
    {"slug": "urgencias", "motivo": "urgencia", "title": "Urgencias dentales: dolor de muela, también los sábados", "h1": "Dolor de muela o urgencia",
     "lead": "Si te duele, escribinos y te buscamos un turno lo antes posible. También los sábados.",
     "desc": "Atención de urgencias dentales y dolor de muela en CABA, sedes Microcentro y Once, de lunes a sábado. Atención particular.",
     "body": [
         "Muela que late, encía hinchada, un diente partido o una corona que se salió: escribinos con una foto si podés.",
         "Primero se calma el dolor y se ve qué lo causa. Después se arma el tratamiento.",
         f"Urgencias los sábados: Microcentro de {SEDES['microcentro']['sabado_urgencias']}, Once de {SEDES['once']['sabado_urgencias']}."]},
    {"slug": "ninos", "motivo": "ninos", "title": "Odontopediatría: dentista para chicos", "h1": "Dentista para chicos",
     "lead": "Odontopediatría en las dos sedes, para que la primera visita sea tranquila.",
     "desc": "Odontopediatría en CABA, sedes Microcentro y Once. Controles, limpiezas y arreglos para chicos. Atención particular.",
     "body": [
         "Atendemos chicos desde los primeros dientes. La primera visita suele ser para conocer el consultorio, sentarse en el sillón y revisar, "
         "sin apuro, para que la próxima vez vengan sin miedo.",
         "Controles, limpieza, selladores y arreglos de caries, explicando cada paso al chico y a los padres.",
         "Escribinos por WhatsApp con la edad y qué le pasa, y coordinamos el turno."]},
]

FAQ = [
    ("¿Cuánto cuesta la consulta?", "Te lo decimos por WhatsApp apenas escribís, junto con valores aproximados de tu tratamiento. El valor final lo da el doctor en la consulta, después de revisarte."),
    ("¿Trabajan con obra social o prepaga?", "Por ahora atendemos de manera particular. Se puede pagar en efectivo, por transferencia o con tarjeta."),
    ("¿Atienden chicos?", "Sí, odontopediatría en las dos sedes."),
    ("¿Atienden urgencias los sábados?", f"Sí. Microcentro de {SEDES['microcentro']['sabado_urgencias']} y Once de {SEDES['once']['sabado_urgencias']}."),
    ("¿Tienen ascensor?", "En Microcentro sí (piso 3). La sede de Once está en planta baja."),
    ("¿Quién responde el WhatsApp?", "Una persona de la recepción de la sede que elijas, en el horario de atención."),
]


# ---------------------------------------------------------------- utilidades
def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def hashed(src_path, published_name):
    with open(src_path, "rb") as f:
        data = f.read()
    h = hashlib.md5(data).hexdigest()[:8]
    base, ext = os.path.splitext(published_name)
    rel = f"assets/{base}.{h}{ext}"
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, rel), "wb") as f:
        f.write(data)
    return "/" + rel


def copy_brand():
    web = os.path.join(MARCA, "web")
    for name in ("favicon.ico", "favicon.svg", "favicon-96.png", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "icon-512-maskable.png", "og.jpg"):
        shutil.copy(os.path.join(web, name), os.path.join(OUT, name))
    write("site.webmanifest", json.dumps({
        "name": BRAND, "short_name": BRAND, "start_url": "/", "display": "browser", "background_color": "#FFFFFF", "theme_color": "#2E7D1F",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, ensure_ascii=False))
    logo_dir = os.path.join(MARCA, LOGO_VARIANTE) if LOGO_VARIANTE else os.path.join(MARCA, "svg")
    return hashed(os.path.join(logo_dir, "logo-horizontal.svg"), "logo-horizontal.svg")


def hours_ld(spec):
    out = []
    for days, opens, closes in spec:
        out.append({"@type": "OpeningHoursSpecification", "dayOfWeek": days, "opens": opens, "closes": closes})
    return out


def ld_json():
    org_id = SITE + "/#org"
    graph = [{
        "@type": "Organization", "@id": org_id, "name": BRAND, "url": SITE + "/", "email": EMAIL,
        "logo": SITE + "/icon-512.png", "sameAs": [INSTAGRAM],
    }]
    for slug, s in SEDES.items():
        graph.append({
            "@type": "Dentist", "@id": f"{SITE}/{slug}/#sede", "name": f"{BRAND} {s['nombre']}",
            "url": f"{SITE}/{slug}/", "telephone": s["tel"], "image": SITE + "/og.jpg",
            "parentOrganization": {"@id": org_id}, "sameAs": [INSTAGRAM],
            "currenciesAccepted": "ARS", "paymentAccepted": "Efectivo, transferencia, tarjeta",
            "address": {"@type": "PostalAddress", "streetAddress": s["calle"], "addressLocality": "Ciudad Autónoma de Buenos Aires",
                        "postalCode": s["cp"], "addressRegion": "CABA", "addressCountry": "AR"},
            "geo": {"@type": "GeoCoordinates", "latitude": s["geo"][0], "longitude": s["geo"][1]},
            "hasMap": s["maps"],
            "openingHoursSpecification": hours_ld(s["horario_ld"]),
        })
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
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_AR">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2E7D1F">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="{assets['css']}">
{ld_json() if not noindex else ''}
</head>
"""


def topbar(assets):
    return f"""<a class="skip" href="#turno">Ir al formulario</a>
<header class="top wrap">
<a class="mark" href="/" aria-label="{BRAND}, inicio"><img src="{assets['logo']}" alt="{BRAND}" width="236" height="56" decoding="async"></a>
<nav class="topnav" aria-label="Sedes"><a href="/microcentro/">Microcentro</a><a href="/once/">Once</a></nav>
</header>"""


def chips(name, items, checked=None):
    out = []
    for it in items:
        key, label = it[0], it[1]
        chk = " checked" if checked == key else ""
        out.append(f'<label class="chip"><input type="radio" name="{name}" value="{esc(key)}"{chk}><span>{esc(label)}</span></label>')
    return "".join(out)


def form(motivo=None, sede=None):
    sede_items = [(k, f"{v['nombre']} · {v['ref']}") for k, v in SEDES.items()]
    return f"""<section class="card" id="turno" aria-labelledby="h-form">
<h2 id="h-form">Pedí tu consulta</h2>
<p class="sub">Cuatro toques y se abre el WhatsApp de la sede con tu mensaje listo. Te responde una persona de la recepción en el horario de atención.</p>
<form class="form" id="lead-form" novalidate>
<fieldset aria-describedby="err-motivo"><legend>¿Qué querés resolver?</legend><div class="chips">{chips("motivo", MOTIVOS, motivo)}</div><p class="error" id="err-motivo" hidden>Elegí qué querés resolver.</p></fieldset>
<fieldset aria-describedby="err-pago"><legend>¿Cómo pensás pagar?</legend><div class="chips">{chips("pago", PAGOS)}</div><p class="error" id="err-pago" hidden>Elegí cómo pensás pagar.</p></fieldset>
<div class="note" id="obra-note" hidden role="status">Por ahora atendemos de manera particular. Si querés venir igual, podés pagar en efectivo, por transferencia o con tarjeta.</div>
<fieldset aria-describedby="err-cuando"><legend>¿Cuándo querés venir?</legend><div class="chips">{chips("cuando", CUANDO)}</div><p class="error" id="err-cuando" hidden>Elegí cuándo querés venir.</p></fieldset>
<fieldset aria-describedby="err-sede"><legend>¿Qué sede te queda mejor?</legend><div class="chips">{chips("sede", sede_items, sede)}</div><p class="error" id="err-sede" hidden>Elegí una sede.</p></fieldset>
<div class="price">{esc(PRECIO_TXT)}</div>
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


def page_data(landing_sede):
    data = {
        "landing": landing_sede or "",
        "sedes": {k: {"nombre": v["nombre"], "wa": v["wa"]} for k, v in SEDES.items()},
        "motivos": {k: {"label": l, "valor": val} for k, l, val in MOTIVOS},
        "pagos": {k: l for k, l in PAGOS},
        "cuando": {k: {"label": l, "factor": f} for k, l, f in CUANDO},
    }
    return '<script type="application/json" id="dc-data">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def trust():
    m, o = SEDES["microcentro"], SEDES["once"]
    return f"""<section class="block" aria-labelledby="h-trust">
<h2 id="h-trust">Por qué Dental Ciudad</h2>
<ul class="ticks">
<li>Más de {ANIOS} años atendiendo en Capital, en Microcentro y en Once.</li>
<li>En Google: Microcentro {m['rating'][0]} con {m['rating'][1]} reseñas, Once {o['rating'][0]} con {o['rating'][1]} reseñas. <a href="{esc(m['reviews'])}" target="_blank" rel="noopener">Leerlas</a>.</li>
<li>Un odontólogo dedicado a cada área: implantes y cirugía, prótesis, estética, ortodoncia, conductos y chicos.</li>
<li>Medidas con escáner 3D y radiografías digitales en el momento.</li>
<li>Atención particular: efectivo, transferencia o tarjeta.</li>
</ul>
</section>"""


def tratamientos_grid():
    items = "".join(f'<li><a href="/{t["slug"]}/"><strong>{esc(t["h1"])}</strong><span>{esc(t["lead"])}</span></a></li>' for t in TRATAMIENTOS)
    return f"""<section class="block" aria-labelledby="h-trat"><h2 id="h-trat">Tratamientos</h2><ul class="grid">{items}</ul></section>"""


def horario_html(s):
    rows = "".join(f"<tr><th scope=\"row\">{esc(d)}</th><td>{esc(h)}</td></tr>" for d, h in s["horario"])
    return f'<table class="hours"><caption class="sr-only">Horario de la sede {esc(s["nombre"])}</caption><tbody>{rows}</tbody></table>'


def sede_card(slug, s, full=False):
    body = f"""<p>{esc(s['calle'])}, {esc(s['ref'])}. {esc(s['acceso'])}.</p>{horario_html(s)}
<p class="links"><a href="{esc(s['maps'])}" target="_blank" rel="noopener">Cómo llegar</a> <a href="https://wa.me/{s['wa']}" target="_blank" rel="noopener">WhatsApp {esc(s['tel_label'])}</a> <a href="tel:{s['tel']}" data-llamar="{slug}">Llamar</a></p>"""
    if full:
        return body
    return f'<li class="sede"><h3><a href="/{slug}/">Sede {esc(s["nombre"])}</a></h3>{body}</li>'


def sedes_block():
    cards = "".join(sede_card(k, v) for k, v in SEDES.items())
    return f"""<section class="block" aria-labelledby="h-sedes"><h2 id="h-sedes">Sedes</h2><ul class="sedes">{cards}</ul></section>"""


def faq_block():
    items = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ)
    return f'<section class="block" aria-labelledby="h-faq"><h2 id="h-faq">Preguntas</h2><div class="faq">{items}</div></section>'


def foot(assets, landing_sede=None):
    resp = f"<p>Responsable: {esc(RESPONSABLE)}</p>" if RESPONSABLE else ""
    return f"""<footer class="foot wrap">
<p>{BRAND} · Microcentro: {esc(SEDES['microcentro']['calle'])} · Once: {esc(SEDES['once']['calle'])} · <a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a></p>
{resp}
<p><a href="/privacidad/">Privacidad</a> · <button type="button" class="linkbtn" data-cookie-settings>Cookies</button> · Actualizado el {date.today().strftime('%d/%m/%Y')}</p>
</footer>
<a class="sticky btn" href="#turno" id="sticky">Pedí tu consulta</a>
{page_data(landing_sede)}
<script src="{assets['js']}" defer></script>
</body></html>
"""


def page(path, title, desc, hero_h1, hero_lead, body_html, assets, motivo=None, sede=None):
    return (head(title, desc, path, assets) + "<body>\n" + topbar(assets) +
            f"""<main class="wrap">
<section class="hero"><h1>{esc(hero_h1)}</h1><p class="lead">{esc(hero_lead)}</p>
<p class="pills"><span>Atención particular</span><span>Microcentro y Once</span><span>Lunes a sábado</span></p></section>
{form(motivo, sede)}
{body_html}
</main>
""" + foot(assets, sede))


# ---------------------------------------------------------------- páginas
def build():
    if os.path.isdir(OUT):
        for name in os.listdir(OUT):
            p = os.path.join(OUT, name)
            if name in ("_headers", "_redirects"):
                continue
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    assets = {"css": hashed(os.path.join(SRC, "site.css"), "site.css"), "js": hashed(os.path.join(SRC, "site.js"), "site.js")}
    assets["logo"] = copy_brand()
    urls = []

    write("index.html", page(
        "/", f"{BRAND} | Dentistas en Microcentro y Once, CABA",
        "Clínica odontológica en Microcentro y Once: implantes, prótesis, carillas, ortodoncia, conductos y chicos. Atención particular. Pedí tu consulta por WhatsApp.",
        "Dentistas en Microcentro y Once",
        "Implantes, prótesis, carillas, ortodoncia, conductos y odontopediatría, con un odontólogo dedicado a cada área.",
        tratamientos_grid() + trust() + sedes_block() + faq_block(), assets))
    urls.append("/")

    for slug, s in SEDES.items():
        body = f"""<section class="block" aria-labelledby="h-llegar"><h2 id="h-llegar">Cómo llegar</h2>
<p class="big">{esc(s['calle'])}</p><p>{esc(s['ref'].capitalize())}. {esc(s['llegada'])}</p>{sede_card(slug, s, full=True)}</section>"""
        write(f"{slug}/index.html", page(
            f"/{slug}/", f"Dentista en {s['nombre']}, CABA | {BRAND}",
            f"Dental Ciudad sede {s['nombre']}: {s['calle']}, {s['ref']}. Implantes, prótesis, carillas, ortodoncia, conductos y chicos. Atención particular.",
            f"Dentista en {s['nombre']}", f"{s['calle']}, {s['ref']}. {s['acceso']}.",
            body + tratamientos_grid() + trust() + faq_block(), assets, sede=slug))
        urls.append(f"/{slug}/")

    for t in TRATAMIENTOS:
        body = '<section class="block prose">' + "".join(f"<p>{esc(p)}</p>" for p in t["body"]) + "</section>"
        write(f"{t['slug']}/index.html", page(
            f"/{t['slug']}/", f"{t['title']} | {BRAND}", t["desc"], t["h1"], t["lead"],
            body + trust() + sedes_block() + faq_block(), assets, motivo=t["motivo"]))
        urls.append(f"/{t['slug']}/")

    priv = f"""<section class="block prose"><h1>Privacidad</h1>
<p>Responsable: {BRAND}, sedes {esc(SEDES['microcentro']['calle'])} y {esc(SEDES['once']['calle'])}, Ciudad Autónoma de Buenos Aires. Contacto: {EMAIL}.</p>
<p>El formulario no pide tu nombre ni tu teléfono. Lo que elegís (qué querés resolver, cómo pensás pagar, cuándo querés venir y la sede) se escribe en un mensaje de WhatsApp que mandás vos, junto con un código de consulta. Ese mensaje lo recibe la recepción de la sede para responderte y coordinar el turno. Esta página no guarda nada de eso.</p>
<p>La página usa Google Analytics y Google Ads para saber cuánta gente la visita y qué anuncios traen consultas. A Google se le avisa que hubo una consulta y su valor estimado, sin tu nombre, tu teléfono ni datos de salud. En el Espacio Económico Europeo, el Reino Unido y Suiza eso solo pasa si aceptás las cookies.</p>
<p>Podés pedir acceso, corrección o eliminación de tus datos escribiendo al WhatsApp de cualquiera de las sedes o a {EMAIL} (Ley 25.326). La Agencia de Acceso a la Información Pública es el órgano de control de esa ley y atiende denuncias y reclamos.</p>
<p>Actualizada el {date.today().strftime('%d/%m/%Y')}.</p></section>"""
    write("privacidad/index.html", head(f"Privacidad | {BRAND}", "Política de privacidad de Dental Ciudad.", "/privacidad/", assets) +
          "<body>\n" + topbar(assets) + f'<main class="wrap">{priv}</main>' + foot(assets))
    urls.append("/privacidad/")

    write("404.html", head(f"Página no encontrada | {BRAND}", "Página no encontrada.", "/404", assets, noindex=True) +
          "<body>\n" + topbar(assets) + '<main class="wrap"><section class="block prose"><h1>Esta página no existe</h1><p><a href="/">Volver al inicio</a></p></section></main>' + foot(assets))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("listo:", OUT, len(urls), "páginas")


if __name__ == "__main__":
    build()
