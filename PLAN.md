# Web de Dental Ciudad: análisis de estándares (25/10/2026)

Pedido de Eduardo: antes de publicar, separar por aspectos qué exige cada estándar, qué cumple la versión 1, qué falta,
qué la haría mejor que lo que hay, y qué decisiones no se habían tomado.

## 1. Ley argentina de publicidad médica y odontológica (Ley 17.132 + Decreto 6216/67; rige en CABA)
Texto de la ley (fuente: Biblioteca AFIP, texto vigente):
- Art. 10: todo anuncio que exceda «nombre, apellido, profesión, título, especialidades y cargos técnicos actuales» debe
  ser autorizado; **«En ningún caso podrán anunciarse precios de consulta, ventajas económicas o gratuidad de servicios»**.
- Art. 30 (odontólogos), prohíbe: anunciar tratamientos a término fijo; características técnicas de equipos que induzcan
  a error; «anunciar o prometer la confección de aparatos protésicos en los que se exalten sus virtudes»; anunciar
  especializaciones no reconocidas o anunciarse como especialista sin estar registrado (art. 31: el título de
  especialista lo autoriza el Ministerio, por 5 años); «publicar falsos éxitos terapéuticos, estadísticas ficticias»;
  técnicas personales; **«publicar cartas de agradecimiento de pacientes»**.
- Decreto 6216/67 art. 10: sin «términos encomiásticos, superlativos ni imperativos»; sin anunciar «formas de tratamiento,
  diagnóstico o pronóstico»; el establecimiento se anuncia con el nombre con que fue habilitado.
- Lo que no sé: cuánto se controla hoy. Todo el sector (y las webs actuales de la clínica) incumple partes de esto.

Qué hace la web nueva: sin precio de consulta (decisión de Eduardo pendiente), sin «gratis», sin cuotas anunciadas, sin
testimonios copiados (enlace a Google con la nota real), sin «especialista» salvo registrados, sin «sin dolor» / «100 %» /
«duran más» / «Best Medical Clinic», sin promesas de plazos. Nombre del responsable y matrícula en el pie.

## 2. Formulario que filtra (lo que piden los que convierten y lo que agregamos)
- Lo que hacen los que convierten: una acción principal arriba, llamada como secundaria, respuesta rápida (<5 min cae
  el contacto de 78 % a 34 % según Redefine Web), preguntas de calificación (tratamiento, cuándo, cómo paga), una página
  por servicio, sin formularios largos.
- Versión 1: 4 preguntas (qué, cómo paga, cuándo, sede), WhatsApp de la sede con mensaje armado y código DC-…,
  obra social → aviso y no cuenta como conversión, valor interno = tratamiento × cuándo.
- Falta: botón «Llamar» secundario; horario de respuesta visible; atribución a la cuenta de Google Ads que trajo el clic
  (sede de aterrizaje), no solo la elegida; página /equipo/; versión en inglés.

## 3. Google Ads (landing page experience, política de salud)
- Relevancia: una página por tratamiento = un grupo de anuncios por tratamiento. Transparencia: razón social, sedes,
  contacto, privacidad, responsable. Velocidad y móvil: sin constructor, sin fuentes externas.
- Salud = categoría sensible: no conversiones avanzadas, no Customer Match, no subir quién pagó, nombres de conversión
  neutros («Consulta web»), `allow_ad_personalization_signals: false`. Modo de consentimiento v2 para EEE/UK/CH.
- Conversión con valor (puntos) → puja «maximizar valor». Una acción de conversión por cuenta (Micro y Once).

## 4. Google local y búsqueda
- Ficha de Google: el nombre debe ser el real («Dental Ciudad»); hoy «Dental Microcentro | Odontología Integral, Implantes
  y Carillas» y «Dental Ciudad | …» llevan descripciones de servicios (no permitido, riesgo de suspensión) y dos nombres
  distintos para la misma cadena. Horarios de la ficha: Micro lun 9–18:30, mar–vie 9–18, sáb 9–13; Once lun 9–17,
  mar–sáb 9–18. La web los copia iguales (NAP consistente). Cada ficha enlaza a su página de sede.
- Datos estructurados: `Dentist` por sede (dirección, geo, teléfono, horarios, mapa, redes, organización madre).
  No `aggregateRating` propio (Google no muestra estrellas de reseñas propias para LocalBusiness desde 2019).
  `FAQPage` ya no produce nada en Google (dejó de mostrarse el 7/5/2026): las preguntas van como texto.
- Técnico: sitemap, robots, canonical, 404, favicon en múltiplos de 48 px (.ico + PNG + SVG), Open Graph por página.
- Salud = YMYL: Google pide saber quién responde: nombres de los profesionales, matrícula, foto, fecha de actualización.

## 5. Velocidad (Core Web Vitals: LCP ≤ 2,5 s · INP ≤ 200 ms · CLS ≤ 0,1)
Letra del sistema, un CSS y un JS chicos, imágenes WebP/AVIF con ancho y alto, Cloudflare. Se mide con Lighthouse antes
de publicar y con Search Console después.

## 6. Accesibilidad (WCAG 2.2 AA)
Contraste ≥ 4,5:1, botones ≥ 44 px, fieldset/legend por pregunta, errores enlazados, foco visible, `lang="es-AR"`,
enlace «saltar al formulario», `prefers-reduced-motion`, nada que dependa solo del color.

## 7. Seguridad y datos personales
La web no guarda nada: lo que la persona elige viaja en su propio WhatsApp a la recepción. Cabeceras HSTS, nosniff,
referrer, permissions, frame + CSP. Solo Google como tercero, con consentimiento donde corresponde. Privacidad con
responsable, derechos (Ley 25.326) y órgano de control.

## 8. Medición
GA4 propio de la clínica, Ads por sede con valor, Search Console, enlaces de la ficha con UTM, código DC-… que la caja
reconoce (origen «web», motivo, sede, cuándo) para cruzar con los pagos de la agenda sin mandarle nada a Google.

## 9. Lo que la hace mejor que lo que hay
Formulario que califica y le pone valor a cada consulta; cruce web → WhatsApp → pago adentro del sistema propio; una
web liviana sin constructor; cumple la ley que el resto ignora; sedes con datos iguales a la ficha; versión en inglés
para los extranjeros que ya llegan (las reseñas en Google lo muestran); después, turno online real desde AGO.

## 10. Decisiones y datos que faltan (en orden)
1. Precio de la consulta en la web: la ley lo prohíbe anunciar. Propuesta: la web dice «Atención particular»; el valor
   lo dice el WhatsApp (bot o recepción) en la primera respuesta. Decide Eduardo.
2. Profesionales: nombre, matrícula, área, si tienen especialidad registrada, foto. Responsable/director para el pie.
3. Una sola web (dentalciudad.ar) con /microcentro/ y /once/; dentalmicrocentro.ar redirige. Fecha del cambio.
4. Nombre de las fichas de Google: **decidido (Eduardo, 25/10 18:03): «Dental Ciudad Microcentro» y «Dental Ciudad Once»** (lo mismo que la web pone en los datos estructurados). Lo cambia Eduardo en «Editar perfil»; Google puede tardar unos días en mostrarlo y a veces pide volver a verificar.
5. Horarios (confirmar los de la ficha), teléfono fijo si hay, ascensor en Micro (piso 3), acceso en Once, niños sí/no,
   urgencias sábados, formas de pago (tarjeta, cuotas: solo por WhatsApp).
6. Fotos reales (sedes, equipo) y logo. Nada de antes/después por ahora.
7. Instagram de cada sede (handles actuales).
8. Versión en inglés: ahora o después.
9. Google Ads: ID y etiqueta «Consulta web» de cada cuenta; GA4 de la clínica; acceso a Search Console.
10. Caja: que reconozca el código DC-… (tarea para Code, cambio chico, solo lectura del mensaje).
11. Años en Capital: 7 u 8 (la web vieja dice 7, los anuncios 8).
