#!/usr/bin/env python3
"""Genera la web de Dental Ciudad en public/.

Una sola web (dentalciudad.ar) con una página por sede y una por tratamiento.
Lo que se edita: textos y datos en este archivo, estilos en site.css, comportamiento en site.js, marca en marca/,
fotos originales en fotos/ (recortes y tamaños en FOTOS, abajo). public/ se genera con `python3 src/build.py` y no se
edita a mano. Cloudflare Pages publica public/ tal cual. Las fotos procesadas se guardan en .cache/img/ para no
rehacerlas en cada corrida.

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

from PIL import Image

SRC = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(SRC)
OUT = os.path.join(PROJ, "public")
MARCA = os.path.join(PROJ, "marca")
FOTOS_DIR = os.path.join(PROJ, "fotos")
CACHE = os.path.join(PROJ, ".cache", "img")
LOGO_VARIANTE = "verde-agua"   # "" = logo original verde lima; "verde-agua" = el verde corrido al verde agua de la referencia
                               # «Vidrio con luz interior» (Eduardo, 25/10 14:35: «con ese estilo y colores»)
HUE_AGUA = 183                 # tono del verde agua de la referencia (el lima del logo está en ~85°)
SITE = "https://dentalciudad.ar"
BRAND = "Dental Ciudad"
TODAY = date.today().isoformat()
ANIOS = "8"
INSTAGRAM = "https://www.instagram.com/dentalciudad1/"
EMAIL = "dentalciudad1@gmail.com"
RESPONSABLE = ""   # FALTA: "Od. Nombre Apellido, M.N. 12345" (responsable para el pie; lo pasa Eduardo)

esc = lambda s: html.escape(str(s), quote=True)
cap = lambda s: s[:1].upper() + s[1:]   # primera letra en mayúscula sin tocar el resto (Galerías Pacífico)

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
        "foto": "micro-recepcion",
        "foto_alt": "Recepción de la sede Microcentro de Dental Ciudad, en Av. Córdoba 679",
        "transporte": "Subte B (Florida) y C (Lavalle) a dos cuadras; colectivos por Av. Córdoba.",
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
        "foto": "once-box",
        "foto_alt": "Consultorio de la sede Once de Dental Ciudad, con una odontóloga atendiendo",
        "transporte": "Subte A y H (Plaza Miserere), tren Sarmiento (estación Once) y decenas de colectivos.",
    },
}
for s in SEDES.values():
    s["maps"] = f"https://www.google.com/maps/search/?api=1&query={BRAND.replace(' ', '%20')}%20{s['nombre']}&query_place_id={s['place_id']}"
    s["reviews"] = s["maps"]
RESENAS_TOTAL = sum(int(s["rating"][1]) for s in SEDES.values())

# Fotos: nombre público → (archivo original en fotos/, recorte (izq, arriba, der, abajo) o None, texto alternativo).
FOTOS = {
    "hero": ("micro-escaner-3d", (0, 560, 1932, 2009), "Odontóloga de Dental Ciudad mostrando un escaneo 3D en la computadora, con una paciente en el sillón"),
    "micro-recepcion": ("micro-recepcion-arbol", (760, 560, 1932, 1440), SEDES["microcentro"]["foto_alt"]),
    "micro-sala": ("micro-sala-espera", (0, 700, 1932, 2149), "Sala de espera de la sede Microcentro"),
    "once-box": ("once-box-trabajo", (320, 60, 2576, 1752), SEDES["once"]["foto_alt"]),
    "once-rx": ("once-rx-poster", (0, 120, 960, 840), "Radiovisiógrafo de la sede Once"),
    "micro-tec": ("micro-tecnologia", (0, 150, 960, 870), "Radiovisiógrafo y escáner 3D de la sede Microcentro"),
    "rx-imax": ("once-rx-imax", (0, 500, 1932, 1949), "Equipo de rayos digital con la radiografía en la computadora"),
    "rx-portatil": ("micro-rx-portatil", (0, 400, 1932, 1849), "Rayos X portátil y la radiografía en pantalla"),
    "box-vidrio": ("once-box-vidrio", (0, 290, 960, 1010), "Odontóloga explicándole el tratamiento a una paciente en el consultorio"),
    "box-arriba": ("once-box-trabajo-arriba", (0, 500, 1932, 1949), "Odontóloga atendiendo a una paciente"),
}
ANCHOS = (480, 800, 1200, 1600)

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
     "card": "Una raíz nueva de titanio y, sobre ella, el diente.",
     "desc": "Implantes dentales en CABA, sedes Microcentro y Once. Atención particular. Consulta con el odontólogo que se dedica a implantes.",
     "foto": "rx-imax",
     "body": [
         "Un implante es una raíz nueva: un tornillo chico de titanio que se coloca en el hueso y sobre el que va el diente. "
         "Funciona como el taco que ponés en la pared para que el cuadro no se caiga: el diente queda firme y no depende de los dientes de al lado.",
         "Sirve cuando falta uno o varios dientes, y también para sostener una prótesis que hoy se mueve.",
         "El odontólogo revisa el hueso con imágenes, te dice si sos candidato y te arma el plan con tiempos y valor."]},
    {"slug": "protesis", "motivo": "protesis", "title": "Prótesis dentales: flexibles, removibles y fijas", "h1": "Prótesis dentales",
     "lead": "Flexibles, removibles (las de ganchos) o completas, hechas a tu medida.",
     "card": "Flexibles, removibles o completas, a medida.",
     "desc": "Prótesis dentales flexibles, removibles y completas en CABA, sedes Microcentro y Once. Atención particular.",
     "foto": "micro-tec",
     "body": [
         "La prótesis reemplaza los dientes que faltan. La flexible es liviana y se adapta a la encía, sin ganchos de metal a la vista; "
         "la removible de ganchos (la que mucha gente llama arañita) se apoya en los dientes que tenés; la completa reemplaza toda la arcada.",
         "Tomamos las medidas con escáner 3D, sin la pasta de impresión de siempre.",
         "Te muestran qué tipo te conviene según los dientes que tenés y el doctor te da el valor."]},
    {"slug": "carillas", "motivo": "carillas", "title": "Carillas y diseño de sonrisa", "h1": "Carillas y diseño de sonrisa",
     "lead": "Para la sonrisa que hoy tapás con la mano en las fotos.",
     "card": "Cerámica, zirconio o resina; diseño digital antes de empezar.",
     "desc": "Carillas de cerámica, zirconio y resina en CABA, sedes Microcentro y Once. Diseño de sonrisa. Atención particular.",
     "foto": "hero",
     "body": [
         "Una carilla es una lámina finita que se pega en la cara de adelante del diente. Cambia color, forma y largo. "
         "La de cerámica es como una taza de loza: no se mancha con el café ni con el mate.",
         "Hay de cerámica, de zirconio y de resina. La elección depende de cómo están tus dientes y de qué buscás.",
         "Se revisan tus dientes y tu mordida, y se planifica el diseño digital para que veas cómo te va a quedar antes de empezar. El valor lo da el doctor después de revisarte."]},
    {"slug": "ortodoncia", "motivo": "ortodoncia", "title": "Ortodoncia: brackets y alineadores invisibles", "h1": "Ortodoncia",
     "lead": "Brackets o alineadores invisibles para ordenar los dientes.",
     "card": "Brackets o alineadores invisibles.",
     "desc": "Ortodoncia con brackets y alineadores invisibles en CABA, sedes Microcentro y Once. Atención particular.",
     "foto": "box-vidrio",
     "body": [
         "La ortodoncia mueve los dientes de a poco hasta su lugar. Con brackets es una guía pegada a los dientes; "
         "con alineadores son placas transparentes que te sacás para comer.",
         "Sirve para dientes torcidos, separados o montados, y para cuando la mordida no cierra bien.",
         "Revisan tu mordida, te explican las opciones y los tiempos, y te dan el valor."]},
    {"slug": "conducto", "motivo": "conducto", "title": "Tratamiento de conducto (endodoncia)", "h1": "Tratamiento de conducto",
     "lead": "Para salvar el diente en vez de sacarlo.",
     "card": "Salvar el diente que duele en vez de sacarlo.",
     "desc": "Tratamiento de conducto (endodoncia) en CABA, sedes Microcentro y Once. Atención particular.",
     "foto": "rx-portatil",
     "body": [
         "Cuando la caries llega al nervio, el diente duele con el frío, con el calor o solo. El conducto limpia el interior del diente y lo sella, "
         "como cuando se cambia un caño tapado sin tirar la pared.",
         "Se hace con anestesia y con radiografías en el momento, para ver el trabajo mientras se hace.",
         "Con una radiografía te dicen si el diente se puede salvar y el doctor te da el valor."]},
    {"slug": "arreglos", "motivo": "arreglo", "title": "Arreglos de caries y dientes rotos", "h1": "Arreglos y caries",
     "lead": "Caries, un diente partido, una obturación que se cayó.",
     "card": "Caries, dientes partidos, obturaciones que se cayeron.",
     "desc": "Arreglos de caries, obturaciones y dientes rotos en CABA, sedes Microcentro y Once. Atención particular.",
     "foto": "once-rx",
     "body": [
         "La caries es un agujero que va creciendo si no se tapa. El arreglo saca la parte dañada y la rellena con un material del color del diente, "
         "como se repara un bache antes de que se haga más grande.",
         "También se arreglan dientes astillados o partidos y se cambian obturaciones viejas que se mancharon o se rompieron.",
         "Se revisa con radiografía qué tan profunda está la caries y el doctor te da el valor."]},
    {"slug": "limpieza", "motivo": "limpieza", "title": "Limpieza dental y control", "h1": "Limpieza y control",
     "lead": "Sarro, manchas y encías que sangran: una limpieza cada seis meses evita problemas grandes.",
     "card": "Sarro y manchas afuera; control de encías y caries.",
     "desc": "Limpieza dental y control en CABA, sedes Microcentro y Once. Atención particular.",
     "foto": "box-arriba", "panel": "Para sacar turno",
     "body": [
         "La limpieza saca el sarro y las manchas que el cepillo ya no saca, sobre todo detrás de los dientes de abajo y cerca de la encía. "
         "Si la encía sangra cuando te cepillás, no es para dejar de cepillarte: es la señal de que hay que limpiar.",
         "En el mismo turno se revisan las caries y las encías, y si hace falta se toma una radiografía.",
         "Escribinos y coordinamos el turno; el doctor te dice cada cuánto te conviene volver."]},
    {"slug": "urgencias", "motivo": "urgencia", "title": "Urgencias dentales: dolor de muela, también los sábados", "h1": "Dolor de muela o urgencia",
     "lead": "Si te duele, escribinos y te buscamos un turno lo antes posible. También los sábados.",
     "card": "Si te duele, te buscamos turno lo antes posible. También los sábados.",
     "desc": "Atención de urgencias dentales y dolor de muela en CABA, sedes Microcentro y Once, de lunes a sábado. Atención particular.",
     "foto": "once-box", "panel": "Si te duele ahora",
     "body": [
         "Muela que late, encía hinchada, un diente partido o una corona que se salió: escribinos con una foto si podés.",
         "Primero se calma el dolor y se ve qué lo causa. Después se arma el tratamiento.",
         f"Urgencias los sábados: Microcentro de {SEDES['microcentro']['sabado_urgencias']}, Once de {SEDES['once']['sabado_urgencias']}."]},
    {"slug": "ninos", "motivo": "ninos", "title": "Odontopediatría: dentista para chicos", "h1": "Dentista para chicos",
     "lead": "Odontopediatría en las dos sedes, para que la primera visita sea tranquila.",
     "card": "Odontopediatría en las dos sedes.",
     "desc": "Odontopediatría en CABA, sedes Microcentro y Once. Controles, limpiezas y arreglos para chicos. Atención particular.",
     "foto": "micro-sala", "panel": "Para sacar turno",
     "body": [
         "Atendemos chicos desde los primeros dientes. La primera visita suele ser para conocer el consultorio, sentarse en el sillón y revisar, "
         "sin apuro, para que la próxima vez vengan sin miedo.",
         "Controles, limpieza, selladores y arreglos de caries, explicando cada paso al chico y a los padres.",
         "Escribinos por WhatsApp con la edad y qué le pasa, y coordinamos el turno."]},
]

FAQ = [
    ("¿Cuánto cuesta la consulta?", "Te lo decimos por WhatsApp apenas escribís, junto con valores aproximados de tu tratamiento. El valor final lo da el doctor en la consulta, después de revisarte."),
    ("¿Trabajan con obra social o prepaga?", "Por ahora atendemos de manera particular. Se puede pagar en efectivo, por transferencia o con tarjeta."),
    ("¿Hay que sacar turno o puedo ir directo?", "Con turno. Escribinos por WhatsApp y la recepción te da día y hora; si es una urgencia, te buscamos el primer lugar libre."),
    ("¿Atienden chicos?", "Sí, odontopediatría en las dos sedes."),
    ("¿Atienden urgencias los sábados?", f"Sí. Microcentro de {SEDES['microcentro']['sabado_urgencias']} y Once de {SEDES['once']['sabado_urgencias']}."),
    ("¿Tienen ascensor?", "En Microcentro sí (piso 3). La sede de Once está en planta baja."),
    ("¿Quién responde el WhatsApp?", "Una persona de la recepción de la sede que elijas, en el horario de atención."),
]

# ---------------------------------------------------------------- íconos (SVG en línea, sin pedidos de red)
ICO_WA = ('<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>')
ICO_TEL = ('<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>')
ICO_STAR = '<svg class="star" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2.5l2.9 6.1 6.7.8-4.9 4.6 1.3 6.6L12 17.3l-6 3.3 1.3-6.6L2.4 9.4l6.7-.8z"/></svg>'
ICO_PIN = ('<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3" fill="none" stroke="currentColor" stroke-width="2"/></svg>')


# ---------------------------------------------------------------- utilidades
def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def hashed(src_path, published_name, sub=""):
    with open(src_path, "rb") as f:
        data = f.read()
    h = hashlib.md5(data).hexdigest()[:8]
    base, ext = os.path.splitext(published_name)
    rel = f"assets/{sub}{base}.{h}{ext}"
    os.makedirs(os.path.dirname(os.path.join(OUT, rel)), exist_ok=True)
    with open(os.path.join(OUT, rel), "wb") as f:
        f.write(data)
    return "/" + rel


def agua(im):
    """Corre el verde lima del logo al verde agua de la referencia (solo los píxeles verdes; gris y negro quedan)."""
    import colorsys
    import numpy as np
    rgba = np.array(im.convert("RGBA")).astype(np.float32)
    r, g, b, a = rgba[..., 0] / 255, rgba[..., 1] / 255, rgba[..., 2] / 255, rgba[..., 3]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    d = mx - mn
    sat = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    # tono en grados
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc, gc, bc = (mx - r) / np.maximum(d, 1e-6), (mx - g) / np.maximum(d, 1e-6), (mx - b) / np.maximum(d, 1e-6)
    h = np.where(m & (mx == r), (bc - gc), h)
    h = np.where(m & (mx == g), 2.0 + rc - bc, h)
    h = np.where(m & (mx == b), 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0 * 360
    greenish = (a > 0) & (sat > 0.25) & (h > 55) & (h < 125)
    h2 = np.where(greenish, (h - 85 + HUE_AGUA) % 360, h)
    # de vuelta a RGB
    hh = h2 / 60.0
    i = np.floor(hh) % 6
    f = hh - np.floor(hh)
    p_ = mx * (1 - sat); q = mx * (1 - sat * f); t = mx * (1 - sat * (1 - f))
    r2 = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [mx, q, p_, p_, t, mx])
    g2 = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [t, mx, mx, q, p_, p_])
    b2 = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [p_, p_, t, mx, mx, q])
    out = rgba.copy()
    out[..., 0] = np.where(greenish, r2 * 255, rgba[..., 0])
    out[..., 1] = np.where(greenish, g2 * 255, rgba[..., 1])
    out[..., 2] = np.where(greenish, b2 * 255, rgba[..., 2])
    return Image.fromarray(out.clip(0, 255).astype("uint8"), "RGBA")


def brand_source(name):
    """PNG del logo pedido, en la variante elegida (generada en caché a partir del original)."""
    orig = os.path.join(MARCA, "png", name)
    if not LOGO_VARIANTE:
        return orig
    os.makedirs(CACHE, exist_ok=True)
    with open(orig, "rb") as fh:
        key = hashlib.md5(fh.read()).hexdigest()[:8]
    dst = os.path.join(CACHE, f"{LOGO_VARIANTE}-{HUE_AGUA}-{key}-{name}")
    if not os.path.exists(dst):
        agua(Image.open(orig)).save(dst, optimize=True)
    return dst


def copy_brand():
    web = os.path.join(MARCA, "web")
    if not LOGO_VARIANTE:
        for name in ("favicon.ico", "favicon-96.png", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "icon-512-maskable.png", "og.jpg"):
            shutil.copy(os.path.join(web, name), os.path.join(OUT, name))
    else:
        iso = Image.open(brand_source("isotipo-1024.png")).convert("RGBA")
        from PIL import ImageDraw

        def square(size, pad, bg=None):
            c = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
            inner = int(size * (1 - 2 * pad))
            i = iso.copy(); i.thumbnail((inner, inner), Image.LANCZOS)
            c.alpha_composite(i, ((size - i.width) // 2, (size - i.height) // 2))
            return c
        square(256, 0.04).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
        square(96, 0.04).save(os.path.join(OUT, "favicon-96.png"), optimize=True)
        square(180, 0.12, (255, 255, 255, 255)).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)
        square(192, 0.08).save(os.path.join(OUT, "icon-192.png"), optimize=True)
        square(512, 0.08).save(os.path.join(OUT, "icon-512.png"), optimize=True)
        square(512, 0.2, (255, 255, 255, 255)).save(os.path.join(OUT, "icon-512-maskable.png"), optimize=True)
        og = Image.new("RGBA", (1200, 630), (244, 250, 252, 255))
        h = Image.open(brand_source("logo-horizontal.png")).convert("RGBA"); h.thumbnail((900, 300), Image.LANCZOS)
        og.alpha_composite(h, ((1200 - h.width) // 2, (630 - h.height) // 2 - 20))
        ImageDraw.Draw(og).rectangle([0, 600, 1200, 630], fill="#0A9AA3")
        og.convert("RGB").save(os.path.join(OUT, "og.jpg"), quality=90, optimize=True)
    write("site.webmanifest", json.dumps({
        "name": BRAND, "short_name": BRAND, "start_url": "/", "display": "browser", "background_color": "#F4FAFC", "theme_color": "#0A9AA3",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, ensure_ascii=False))
    # Logo de la cabecera: WebP a 3x del PNG (el SVG trazado pesa 58 KB y tarda en dibujarse)
    os.makedirs(CACHE, exist_ok=True)
    with open(brand_source("logo-horizontal.png"), "rb") as fh:
        tag = f"{LOGO_VARIANTE or 'original'}-{hashlib.md5(fh.read()).hexdigest()[:8]}"
    logo = os.path.join(CACHE, f"logo-{tag}-720.webp")
    if not os.path.exists(logo):
        im = Image.open(brand_source("logo-horizontal.png")).convert("RGBA")
        im.thumbnail((720, 720), Image.LANCZOS)
        im.save(logo, "WEBP", quality=90, method=6)
    out = {"logo": hashed(logo, "logo-horizontal.webp")}
    # logo blanco para el pie
    blanco = os.path.join(CACHE, f"logo-blanco-{tag}-520.webp")
    if not os.path.exists(blanco):
        im = Image.open(brand_source("logo-horizontal-blanco.png")).convert("RGBA")
        im.thumbnail((520, 520), Image.LANCZOS)
        im.save(blanco, "WEBP", quality=90, method=6)
    out["logo_blanco"] = hashed(blanco, "logo-blanco.webp")
    return out


def fotos():
    """Recorta y achica cada foto a los anchos de ANCHOS, en AVIF y WebP; devuelve {nombre: {w, h, avif, webp}}."""
    os.makedirs(CACHE, exist_ok=True)
    out = {}
    for name, (orig, box, alt) in FOTOS.items():
        src = os.path.join(FOTOS_DIR, orig + ".jpg")
        with open(src, "rb") as f:
            key = hashlib.md5(f.read() + repr(box).encode() + b"v1").hexdigest()[:8]
        im = None
        entry = {"alt": alt, "avif": {}, "webp": {}, "key": key}
        cw = (box[2] - box[0]) if box else Image.open(src).width
        anchos = [w for w in ANCHOS if w <= cw]
        if cw < ANCHOS[-1] and cw not in anchos:
            anchos.append(cw)
        for w_eff in anchos:
            for fmt, ext in (("AVIF", "avif"), ("WEBP", "webp")):
                cname = f"{name}-{w_eff}.{key}.{ext}"
                cpath = os.path.join(CACHE, cname)
                if not os.path.exists(cpath):
                    if im is None:
                        im = Image.open(src).convert("RGB")
                        if box:
                            im = im.crop(box)
                    r = im.resize((w_eff, round(im.height * w_eff / im.width)), Image.LANCZOS)
                    if fmt == "AVIF":
                        r.save(cpath, "AVIF", quality=58, speed=6)
                    else:
                        r.save(cpath, "WEBP", quality=80, method=6)
                rel = f"assets/img/{cname}"
                os.makedirs(os.path.join(OUT, "assets", "img"), exist_ok=True)
                shutil.copy(cpath, os.path.join(OUT, rel))
                entry[ext][w_eff] = "/" + rel
        ws = sorted(entry["webp"])
        with Image.open(os.path.join(CACHE, f"{name}-{ws[-1]}.{key}.webp")) as big:
            entry["w"], entry["h"] = big.size
        out[name] = entry
    return out


def picture(f, name, sizes, cls="", eager=False, width=None):
    """<picture> con AVIF + WebP, ancho/alto para que no salte la página."""
    e = f[name]
    srcset = lambda d: ", ".join(f"{u} {w}w" for w, u in sorted(d.items()))
    biggest = max(e["webp"])
    attrs = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture class="{cls}"><source type="image/avif" srcset="{srcset(e["avif"])}" sizes="{sizes}">'
            f'<img src="{e["webp"][biggest]}" srcset="{srcset(e["webp"])}" sizes="{sizes}" width="{e["w"]}" height="{e["h"]}" '
            f'alt="{esc(e["alt"])}" decoding="async" {attrs}></picture>')


def hours_ld(spec):
    out = []
    for days, opens, closes in spec:
        out.append({"@type": "OpeningHoursSpecification", "dayOfWeek": days, "opens": opens, "closes": closes})
    return out


def ld_json(f):
    org_id = SITE + "/#org"
    graph = [{
        "@type": "Organization", "@id": org_id, "name": BRAND, "url": SITE + "/", "email": EMAIL,
        "logo": SITE + "/icon-512.png", "sameAs": [INSTAGRAM],
    }]
    for slug, s in SEDES.items():
        img = f[s["foto"]]["webp"][max(f[s["foto"]]["webp"])]
        graph.append({
            "@type": "Dentist", "@id": f"{SITE}/{slug}/#sede", "name": f"{BRAND} {s['nombre']}",
            "url": f"{SITE}/{slug}/", "telephone": s["tel"], "image": SITE + img,
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


def head(title, desc, path, assets, noindex=False, preload=None):
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    pre = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">' if preload else ""
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
<meta name="theme-color" content="#F4FAFC">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="{assets['font']}" as="font" type="font/woff2" crossorigin>
{pre}
<link rel="stylesheet" href="{assets['css']}">
{assets['ld'] if not noindex else ''}
</head>
"""


def topbar(assets):
    return f"""<a class="skip" href="#turno">Ir al formulario de turnos</a>
<header class="top">
<div class="wrap top-row">
<a class="mark" href="/" aria-label="{BRAND}, inicio"><img src="{assets['logo']}" alt="{BRAND}" width="236" height="56" decoding="async"></a>
<nav class="topnav" aria-label="Secciones">
<a href="/#tratamientos">Tratamientos</a><a href="/#equipo">Equipo</a><a href="/#sedes">Sedes</a><a href="/microcentro/">Microcentro</a><a href="/once/">Once</a><a href="/#preguntas">Preguntas</a>
</nav>
<a class="btn glass lit btn-top" href="#turno">Pedir turno</a>
<details class="menu"><summary aria-label="Menú"><span></span><span></span><span></span></summary>
<nav aria-label="Secciones"><a href="/#tratamientos">Tratamientos</a><a href="/#equipo">Equipo</a><a href="/#sedes">Sedes</a><a href="/microcentro/">Sede Microcentro</a><a href="/once/">Sede Once</a><a href="/#preguntas">Preguntas</a><a href="#turno">Pedir turno</a></nav></details>
</div>
</header>"""


def rating_line(sede=None):
    if sede:
        s = SEDES[sede]
        return (f'<p class="rating">{ICO_STAR}<span><strong>{s["rating"][0]}</strong> en Google, con {s["rating"][1]} reseñas de pacientes de esta sede.</span> '
                f'<a href="{esc(s["reviews"])}" target="_blank" rel="noopener">Leer reseñas</a></p>')
    m, o = SEDES["microcentro"], SEDES["once"]
    return (f'<p class="rating">{ICO_STAR}<span><strong>{m["rating"][0]}</strong> en Google en Microcentro y <strong>{o["rating"][0]}</strong> en Once, '
            f'con {RESENAS_TOTAL} reseñas.</span> <a href="{esc(m["reviews"])}" target="_blank" rel="noopener">Leer reseñas</a></p>')


def hero(f, h1, lead, foto, eager=True, cta_sede=None, chips_html=""):
    """Portada: texto a la izquierda, foto grande a la derecha."""
    if cta_sede:
        s = SEDES[cta_sede]
        ctas = (f'<a class="btn glass lit" href="https://wa.me/{s["wa"]}" target="_blank" rel="noopener">{ICO_WA}<span>Escribir por WhatsApp</span></a>'
                f'<a class="btn glass" href="tel:{s["tel"]}" data-llamar="{cta_sede}">{ICO_TEL}<span>Llamar {esc(s["tel_label"])}</span></a>')
    else:
        ctas = f'<a class="btn glass lit" href="#turno">{ICO_WA}<span>Pedir turno por WhatsApp</span></a><a class="btn glass" href="#sedes"><span>Ver las sedes</span></a>'
    return f"""<section class="hero">
<div class="wrap hero-grid">
<div class="hero-text">
<h1>{esc(h1)}</h1>
<p class="lead">{esc(lead)}</p>
{chips_html}
<div class="ctas">{ctas}</div>
{rating_line(cta_sede)}
</div>
{picture(f, foto, "(min-width: 900px) 52vw, 100vw", "hero-photo", eager=eager)}
</div>
</section>"""


def chips(name, items, checked=None):
    out = []
    for it in items:
        key, label = it[0], it[1]
        chk = " checked" if checked == key else ""
        out.append(f'<label class="opt"><input type="radio" name="{name}" value="{esc(key)}"{chk}><span class="glass"><b>{esc(label)}</b></span></label>')
    return "".join(out)


def form(motivo=None, sede=None):
    sede_items = [(k, f"{v['nombre']}, {v['ref']}") for k, v in SEDES.items()]
    return f"""<section class="section section-wash section-form" id="turno" aria-labelledby="h-form">
<div class="wrap">
<div class="form-head"><h2 id="h-form">Pedí tu turno por WhatsApp</h2>
<p class="sub">Elegí cuatro cosas y se abre el WhatsApp de la sede con tu mensaje escrito. Te responde una persona de la recepción en el horario de atención.</p></div>
<div class="form-panel">
<form class="form" id="lead-form" novalidate>
<fieldset aria-describedby="err-motivo"><legend>¿Qué querés resolver?</legend><div class="opts">{chips("motivo", MOTIVOS, motivo)}</div><p class="error" id="err-motivo" hidden>Elegí qué querés resolver.</p></fieldset>
<fieldset aria-describedby="err-pago"><legend>¿Cómo pensás pagar?</legend><div class="opts opts-2">{chips("pago", PAGOS)}</div><p class="error" id="err-pago" hidden>Elegí cómo pensás pagar.</p></fieldset>
<div class="note" id="obra-note" hidden role="status">Por ahora atendemos de manera particular. Si querés venir igual, podés pagar en efectivo, por transferencia o con tarjeta.</div>
<fieldset aria-describedby="err-cuando"><legend>¿Cuándo querés venir?</legend><div class="opts opts-3">{chips("cuando", CUANDO)}</div><p class="error" id="err-cuando" hidden>Elegí cuándo querés venir.</p></fieldset>
<fieldset aria-describedby="err-sede"><legend>¿Qué sede te queda mejor?</legend><div class="opts opts-2">{chips("sede", sede_items, sede)}</div><p class="error" id="err-sede" hidden>Elegí una sede.</p></fieldset>
<p class="price">{esc(PRECIO_TXT)}</p>
<div class="form-send"><button class="btn glass lit btn-big" type="submit">{ICO_WA}<span>Enviar por WhatsApp</span></button>
<p class="hint">Se abre WhatsApp con tu mensaje escrito. No pedimos ni guardamos datos. <a href="/privacidad/">Privacidad</a></p></div>
</form>
<div class="done" id="done" hidden role="status">
<p class="done-title">Tu mensaje está listo</p>
<p>Si WhatsApp no se abrió, tocá el botón.</p>
<p class="code">Código de tu consulta: <strong id="done-code"></strong></p>
<a class="btn glass lit" id="done-open" href="#" rel="noopener">{ICO_WA}<span>Abrir WhatsApp</span></a>
</div>
</div>
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


def tratamientos_grid():
    items = "".join(f'<li><a href="/{t["slug"]}/"><strong>{esc(t["h1"])}</strong><span>{esc(t["card"])}</span></a></li>' for t in TRATAMIENTOS)
    return f"""<section class="section" id="tratamientos" aria-labelledby="h-trat"><div class="wrap">
<div class="section-head"><h2 id="h-trat">Tratamientos</h2><p class="sub">Un odontólogo dedicado a cada área. Tocá uno para ver cómo es y pedir turno.</p></div>
<ul class="tiles">{items}</ul></div></section>"""


def como(f):
    return f"""<section class="section section-wash" id="como" aria-labelledby="h-como"><div class="wrap split">
{picture(f, "box-vidrio", "(min-width: 900px) 40vw, 100vw", "split-photo")}
<div class="split-text">
<h2 id="h-como">Cómo trabajamos</h2>
<dl class="puntos">
<div><dt>Un odontólogo para cada tratamiento</dt><dd>Endodoncia, ortodoncia, cirugía maxilofacial, odontopediatría, prótesis y estética, cada una con el suyo. En la primera consulta te revisa quien te va a tratar.</dd></div>
<div><dt>Imágenes en el momento</dt><dd>Radiografías digitales en el sillón y escáner 3D para tomar medidas sin pasta de impresión. Ves en la pantalla lo mismo que ve el doctor.</dd></div>
<div><dt>Sabés qué se va a hacer antes de empezar</dt><dd>Te explican el plan paso a paso y te dan el presupuesto por escrito. Atención particular: efectivo, transferencia o tarjeta.</dd></div>
<div><dt>{ANIOS} años en el centro de la ciudad</dt><dd>Dos sedes, en Microcentro y en Once, con turnos de lunes a sábado y urgencias los sábados.</dd></div>
</dl>
</div>
</div></section>"""


EQUIPO = [
    ("Endodoncia", "Tratamientos de conducto: salvar el diente que duele en vez de sacarlo.", "/conducto/"),
    ("Ortodoncia", "Brackets y alineadores invisibles.", "/ortodoncia/"),
    ("Cirugía maxilofacial", "Implantes, extracciones complejas y muelas de juicio.", "/implantes/"),
    ("Odontopediatría", "Chicos desde los primeros dientes.", "/ninos/"),
    ("Prótesis", "Flexibles, removibles y completas, a medida.", "/protesis/"),
    ("Estética", "Diseño de sonrisa, carillas de porcelana y carillas de resina.", "/carillas/"),
]


def equipo():
    items = "".join(f'<li><a href="{u}"><strong>{esc(t)}</strong><span>{esc(d)}</span></a></li>' for t, d, u in EQUIPO)
    return f"""<section class="section" id="equipo" aria-labelledby="h-equipo"><div class="wrap">
<div class="section-head"><h2 id="h-equipo">El equipo</h2><p class="sub">No hay un dentista que hace de todo: cada área la atiende el odontólogo que se dedica a eso.</p></div>
<ul class="tiles">{items}</ul>
<p class="labs">Las prótesis, las carillas y las coronas se hacen con varios de los mejores laboratorios odontológicos de la ciudad.</p>
</div></section>"""


def tecnologia(f):
    return f"""<section class="section" id="tecnologia" aria-labelledby="h-tec"><div class="wrap">
<div class="section-head"><h2 id="h-tec">Tecnología en el consultorio</h2><p class="sub">Lo que hace falta para diagnosticar bien está en la misma sala, no en otro lado.</p></div>
<ul class="tec">
<li>{picture(f, "rx-imax", "(min-width: 760px) 50vw, 100vw")}<h3>Radiografías digitales en el sillón</h3><p>El radiovisiógrafo toma la placa y la muestra en la pantalla al instante, con menos radiación que la radiografía de antes. Se usa en conductos, implantes y para ver qué tan profunda está una caries.</p></li>
<li>{picture(f, "micro-tec", "(min-width: 760px) 50vw, 100vw")}<h3>Escáner 3D en vez de la pasta de impresión</h3><p>Una cámara chica recorre los dientes y arma el modelo en la computadora. Sirve para prótesis, carillas y alineadores, sin la cubeta con pasta que daba arcadas.</p></li>
<li>{picture(f, "rx-portatil", "(min-width: 760px) 50vw, 100vw")}<h3>Rayos X portátil</h3><p>El equipo va hasta el sillón: la placa se toma sin que te levantes ni cambies de sala, y aparece en la pantalla del consultorio.</p></li>
</ul>
</div></section>"""


def horario_html(s):
    rows = "".join(f"<tr><th scope=\"row\">{esc(d)}</th><td>{esc(h)}</td></tr>" for d, h in s["horario"])
    return f'<table class="hours"><caption class="sr-only">Horario de la sede {esc(s["nombre"])}</caption><tbody>{rows}</tbody></table>'


def sede_card(f, slug, s):
    return f"""<li class="sede">
<a class="sede-photo" href="/{slug}/" tabindex="-1" aria-hidden="true">{picture(f, s["foto"], "(min-width: 760px) 50vw, 100vw")}</a>
<div class="sede-body">
<h3><a href="/{slug}/">Sede {esc(s["nombre"])}</a></h3>
<p class="addr">{ICO_PIN}<span>{esc(s['calle'])}, {esc(s['ref'])}. {esc(s['acceso'])}.</span></p>
{horario_html(s)}
<p class="rating rating-small">{ICO_STAR}<span><strong>{s['rating'][0]}</strong> en Google, {s['rating'][1]} reseñas</span></p>
<div class="sede-ctas">
<a class="btn glass lit" href="https://wa.me/{s['wa']}" target="_blank" rel="noopener">{ICO_WA}<span>WhatsApp {esc(s['tel_label'])}</span></a>
<a class="btn glass" href="tel:{s['tel']}" data-llamar="{slug}">{ICO_TEL}<span>Llamar</span></a>
<a class="textlink" href="{esc(s['maps'])}" target="_blank" rel="noopener">Cómo llegar</a>
</div>
</div>
</li>"""


def sedes_block(f):
    cards = "".join(sede_card(f, k, v) for k, v in SEDES.items())
    return f"""<section class="section section-wash" id="sedes" aria-labelledby="h-sedes"><div class="wrap">
<div class="section-head"><h2 id="h-sedes">Las sedes</h2><p class="sub">Las dos en el centro, sobre avenidas, cerca del subte. Elegí la que te quede mejor.</p></div>
<ul class="sedes">{cards}</ul></div></section>"""


def faq_block():
    items = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ)
    return f'<section class="section" id="preguntas" aria-labelledby="h-faq"><div class="wrap"><h2 id="h-faq">Preguntas frecuentes</h2><div class="faq">{items}</div></div></section>'


def foot(assets, landing_sede=None):
    resp = f"<p>Responsable: {esc(RESPONSABLE)}</p>" if RESPONSABLE else ""
    cols = ""
    for slug, s in SEDES.items():
        hs = "<br>".join(f"{esc(d)}: {esc(h)}" for d, h in s["horario"] if h != "cerrado")
        cols += (f'<div class="foot-col"><h3><a href="/{slug}/">Sede {esc(s["nombre"])}</a></h3><p>{esc(s["calle"])}<br>{esc(cap(s["ref"]))}</p>'
                 f'<p>{hs}</p><p><a href="https://wa.me/{s["wa"]}" target="_blank" rel="noopener">WhatsApp {esc(s["tel_label"])}</a></p></div>')
    trat = "".join(f'<a href="/{t["slug"]}/">{esc(t["h1"])}</a>' for t in TRATAMIENTOS)
    return f"""<footer class="foot">
<div class="wrap foot-grid">
<div class="foot-brand"><img src="{assets['logo_blanco']}" alt="{BRAND}" width="260" height="65" loading="lazy" decoding="async">
<p>Clínica odontológica en Microcentro y Once, Ciudad de Buenos Aires. Atención particular, de lunes a sábado.</p>
<p><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a></p>{resp}</div>
{cols}
<div class="foot-col foot-links"><h3>Tratamientos</h3>{trat}</div>
</div>
<div class="wrap foot-legal"><a href="/privacidad/">Privacidad</a><button type="button" class="linkbtn" data-cookie-settings>Cookies</button><span>Actualizado el {date.today().strftime('%d/%m/%Y')}</span></div>
</footer>
<div class="sticky" id="sticky"><a class="btn glass lit" href="#turno">{ICO_WA}<span>Pedir turno</span></a></div>
{page_data(landing_sede)}
<script src="{assets['js']}" defer></script>
</body></html>
"""


# ---------------------------------------------------------------- páginas
def build():
    if os.path.isdir(OUT):
        for name in os.listdir(OUT):
            p = os.path.join(OUT, name)
            if name in ("_headers", "_redirects"):
                continue
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    f = fotos()
    assets = {"css": hashed(os.path.join(SRC, "site.css"), "site.css"), "js": hashed(os.path.join(SRC, "site.js"), "site.js"),
              "font": hashed(os.path.join(SRC, "fonts", "figtree-latin-wght-normal.woff2"), "figtree.woff2")}
    assets.update(copy_brand())
    assets["ld"] = ld_json(f)
    # la hoja de estilos nombra la fuente por su ruta publicada
    css_path = os.path.join(OUT, assets["css"].lstrip("/"))
    with open(css_path, encoding="utf-8") as fh:
        css = fh.read().replace("__FONT__", assets["font"])
    with open(css_path, "w", encoding="utf-8") as fh:
        fh.write(css)
    urls = []

    def shell(path, title, desc, body, sede=None, noindex=False):
        return head(title, desc, path, assets, noindex=noindex) + "<body>\n" + topbar(assets) + "<main>\n" + body + "</main>\n" + foot(assets, sede)

    write("index.html", shell(
        "/", f"{BRAND} | Dentistas en Microcentro y Once, CABA",
        "Clínica odontológica en Microcentro y Once: implantes, prótesis, carillas, ortodoncia, conductos y chicos. Atención particular. Pedí tu turno por WhatsApp.",
        hero(f, "Tu dentista en Microcentro y Once",
             "Implantes, prótesis, carillas, ortodoncia, conductos y odontopediatría. Dos sedes en el centro de Buenos Aires, con turnos de lunes a sábado.",
             "hero")
        + sedes_block(f) + tecnologia(f) + tratamientos_grid() + como(f) + equipo() + form() + faq_block()))
    urls.append("/")

    for slug, s in SEDES.items():
        otra = "once" if slug == "microcentro" else "microcentro"
        hs = horario_html(s)
        body = f"""<section class="section" aria-labelledby="h-llegar"><div class="wrap split split-rev">
<div class="split-text">
<h2 id="h-llegar">Cómo llegar</h2>
<p class="big">{esc(s['calle'])}</p>
<p>{esc(cap(s['ref']))}. {esc(s['llegada'])}</p>
<p>{esc(s['transporte'])}</p>
<h3 class="h-small">Horario</h3>{hs}
<p class="links"><a class="textlink" href="{esc(s['maps'])}" target="_blank" rel="noopener">Abrir en Google Maps</a></p>
<p class="otra">¿Te queda mejor la otra sede? <a href="/{otra}/">Ver la sede {esc(SEDES[otra]['nombre'])}</a>.</p>
</div>
{picture(f, "micro-sala" if slug == "microcentro" else "once-rx", "(min-width: 900px) 40vw, 100vw", "split-photo")}
</div></section>"""
        write(f"{slug}/index.html", shell(
            f"/{slug}/", f"Dentista en {s['nombre']}, CABA | {BRAND}",
            f"Dental Ciudad sede {s['nombre']}: {s['calle']}, {s['ref']}. Implantes, prótesis, carillas, ortodoncia, conductos y chicos. Atención particular.",
            hero(f, f"Dentista en {s['nombre']}", f"{cap(s['ref'])}. {s['acceso']}. Implantes, prótesis, carillas, ortodoncia, conductos y chicos, con turnos de lunes a sábado.",
                 s["foto"], cta_sede=slug)
            + body + tecnologia(f) + tratamientos_grid() + como(f) + equipo() + form(sede=slug) + faq_block(), sede=slug))
        urls.append(f"/{slug}/")

    for t in TRATAMIENTOS:
        paras = "".join(f"<p>{esc(p)}</p>" for p in t["body"][:-1])
        body = f"""<section class="section"><div class="wrap"><div class="prose"><h2>En qué consiste</h2>{paras}
<div class="consulta"><h3>{esc(t.get("panel", "En la primera consulta"))}</h3><p>{esc(t["body"][-1])}</p>
<a class="btn glass lit" href="#turno">{ICO_WA}<span>Pedir turno por WhatsApp</span></a></div></div></div></section>"""
        write(f"{t['slug']}/index.html", shell(
            f"/{t['slug']}/", f"{t['title']} | {BRAND}", t["desc"],
            hero(f, t["h1"], t["lead"], t["foto"]) + body + como(f) + sedes_block(f) + form(motivo=t["motivo"]) + faq_block()))
        urls.append(f"/{t['slug']}/")

    priv = f"""<section class="section"><div class="wrap"><div class="prose"><h1>Privacidad</h1>
<p>Responsable: {BRAND}, sedes {esc(SEDES['microcentro']['calle'])} y {esc(SEDES['once']['calle'])}, Ciudad Autónoma de Buenos Aires. Contacto: {EMAIL}.</p>
<p>El formulario no pide tu nombre ni tu teléfono. Lo que elegís (qué querés resolver, cómo pensás pagar, cuándo querés venir y la sede) se escribe en un mensaje de WhatsApp que mandás vos, junto con un código de consulta. Ese mensaje lo recibe la recepción de la sede para responderte y coordinar el turno. Esta página no guarda nada de eso.</p>
<p>La página usa Google Analytics y Google Ads para saber cuánta gente la visita y qué anuncios traen consultas. A Google se le avisa que hubo una consulta y su valor estimado, sin tu nombre, tu teléfono ni datos de salud. En el Espacio Económico Europeo, el Reino Unido y Suiza eso solo pasa si aceptás las cookies.</p>
<p>Podés pedir acceso, corrección o eliminación de tus datos escribiendo al WhatsApp de cualquiera de las sedes o a {EMAIL} (Ley 25.326). La Agencia de Acceso a la Información Pública es el órgano de control de esa ley y atiende denuncias y reclamos.</p>
<p>Actualizada el {date.today().strftime('%d/%m/%Y')}.</p></div></div></section>"""
    write("privacidad/index.html", shell("/privacidad/", f"Privacidad | {BRAND}", "Política de privacidad de Dental Ciudad.", priv))
    urls.append("/privacidad/")

    write("404.html", shell("/404", f"Página no encontrada | {BRAND}", "Página no encontrada.",
                            '<section class="section"><div class="wrap"><div class="prose"><h1>Esta página no existe</h1><p><a href="/">Volver al inicio</a></p></div></div></section>', noindex=True))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("listo:", OUT, len(urls), "páginas")


if __name__ == "__main__":
    build()
