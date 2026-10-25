# dentalciudad.ar

Marca: `marca/` (kit generado con `src/make_brand.py`; la web usa el logo original; la variante `verde-agua` queda en el kit y se cambia con `LOGO_VARIANTE` en `src/build.py`). Análisis de estándares y decisiones: `PLAN.md`.
Fotos: originales en `fotos/`; recortes, textos alternativos y tamaños en `FOTOS` de `src/build.py` (se generan en AVIF y WebP
a 480/800/1200/1600 px, con caché en `.cache/img/`). Letra: Figtree variable alojada en `src/fonts/` (sin pedidos a Google Fonts).
Lighthouse móvil del 25/10 (versión 3): rendimiento 100, accesibilidad 100, buenas prácticas 100, SEO 100.

Estructura de la portada (versión 5, 25/10, orden pedido por Eduardo: primero imágenes): cabecera con menú y botón · portada con
foto del consultorio, botones y nota de Google · las sedes (foto, dirección, horarios, nota de Google, WhatsApp, llamar, cómo
llegar) · tecnología (radiovisiógrafo, escáner 3D, rayos portátil) · tratamientos (9, cada uno con su página) · cómo trabajamos
(foto + 4 puntos) · el equipo (por especialidades, sin nombres) · pedí tu turno (el formulario de 4 preguntas) · preguntas
frecuentes · pie. Las páginas de sede y de tratamiento repiten el esquema con su foto y el formulario preseleccionado.
Estilo «Vidrio con luz interior» (referencia de Eduardo): botones y opciones de vidrio con la luz encendida en lo elegido;
paleta verde agua + azul marino + fondo helado; el logo se corre al verde agua en el build (`LOGO_VARIANTE`, `HUE_AGUA`).
Marca: los originales están en `marca/originales/`; `python3 src/make_brand.py marca/originales/isotipo.png
marca/originales/logo-vertical.jpg marca/originales/logotipo.jpg` regenera el kit (letras sin relleno blanco adentro).

Web de Dental Ciudad: una sola web, una página por sede (`/microcentro/`, `/once/`) y una por tratamiento
(`/implantes/`, `/protesis/`, `/carillas/`, `/ortodoncia/`, `/conducto/`, `/arreglos/`, `/limpieza/`, `/urgencias/`, `/ninos/`). Aparte de todo lo demás
(no toca el servidor "edu", la agenda ni la caja).

- `src/` es lo que se edita: textos y datos en `src/build.py`, estilos en `src/site.css`, comportamiento en `src/site.js`.
- `public/` se genera con `python3 src/build.py` y no se edita a mano. Cloudflare Pages publica `public/`.

## El formulario (filtra, no adorna)
Tres pasos (Eduardo, 25/10: «tres pasitos nada más»): qué querés resolver, cómo pensás pagar y sede. No pide nombre ni
teléfono. Abre el WhatsApp de la sede con el mensaje armado («Quiero / Pago / Sede / Código DC-XXXXX»).

- Conversión a Google Ads solo si paga particular. Obra social / prepaga: aviso "atendemos de manera particular" y no cuenta.
- Valor (puntos relativos, no plata) = el del tratamiento: implantes 10, prótesis 8, carillas 8, ortodoncia 6, conducto 4,
  consulta 3, urgencia 3, niños 3, arreglo 2, limpieza 1.
- La conversión va a la cuenta de Google Ads de la sede elegida (`CONFIG.ads` en `src/site.js`).
- Política de Google: la salud es categoría sensible. No se manda nombre, teléfono ni datos de salud, no se usan
  conversiones avanzadas ni se sube quién pagó. Nombres de conversión neutros ("Consulta web").

## Falta
- `CONFIG` en `src/site.js`: Analytics y, por sede, el AW-… y la etiqueta de "Consulta web".
- `RESPONSABLE` en `src/build.py` (nombre y matrícula para el pie). «El equipo» va por especialidades, sin nombres (Eduardo, 25/10).
- Confirmar horarios (hoy, los de la ficha de Google).
- Que la caja reconozca el código `DC-…` del mensaje (lo hace Code en caja-whatsapp).
- Dominio: dentalciudad.ar a este proyecto y dentalmicrocentro.ar redirigido a /microcentro/ (con OK de Eduardo).
