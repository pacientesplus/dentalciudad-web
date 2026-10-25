# dentalciudad.ar

Marca: `marca/` (kit generado con `src/make_brand.py`; la web usa el logo original; la variante `verde-agua` queda en el kit y se cambia con `LOGO_VARIANTE` en `src/build.py`). Análisis de estándares y decisiones: `PLAN.md`.
Lighthouse móvil del 25/10: rendimiento 99, accesibilidad 100, buenas prácticas 100, SEO 100.

Web de Dental Ciudad: una sola web, una página por sede (`/microcentro/`, `/once/`) y una por tratamiento
(`/implantes/`, `/protesis/`, `/carillas/`, `/ortodoncia/`, `/conducto/`, `/urgencias/`). Aparte de todo lo demás
(no toca el servidor "edu", la agenda ni la caja).

- `src/` es lo que se edita: textos y datos en `src/build.py`, estilos en `src/site.css`, comportamiento en `src/site.js`.
- `public/` se genera con `python3 src/build.py` y no se edita a mano. Cloudflare Pages publica `public/`.

## El formulario (filtra, no adorna)
Cuatro preguntas: qué querés resolver, cómo pensás pagar, cuándo querés venir y sede. No pide nombre ni teléfono.
Abre el WhatsApp de la sede con el mensaje armado y un código `DC-XXXXX`.

- Conversión a Google Ads solo si paga particular. Obra social / prepaga: aviso "atendemos de manera particular" y no cuenta.
- Valor (puntos relativos, no plata) = tratamiento × cuándo. Tratamiento: implantes 10, prótesis 8, carillas 8,
  ortodoncia 6, conducto 4, consulta 3, urgencia 3, arreglo 2, limpieza 1. Cuándo: hoy ×1, esta semana ×0,9, este mes ×0,6.
- La conversión va a la cuenta de Google Ads de la sede elegida (`CONFIG.ads` en `src/site.js`).
- Política de Google: la salud es categoría sensible. No se manda nombre, teléfono ni datos de salud, no se usan
  conversiones avanzadas ni se sube quién pagó. Nombres de conversión neutros ("Consulta web").

## Falta
- `CONFIG` en `src/site.js`: Analytics y, por sede, el AW-… y la etiqueta de "Consulta web".
- `RESPONSABLE` en `src/build.py` (nombre y matrícula para el pie) y fotos reales.
- Confirmar horarios (hoy, los de la ficha de Google).
- Que la caja reconozca el código `DC-…` del mensaje (lo hace Code en caja-whatsapp).
- Dominio: dentalciudad.ar a este proyecto y dentalmicrocentro.ar redirigido a /microcentro/ (con OK de Eduardo).
