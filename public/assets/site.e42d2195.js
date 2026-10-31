(() => {
  "use strict";

  /* Lo que dice FALTA se completa cuando se prenda esa parte. */
  const CONFIG = {
    analyticsId: "",   // FALTA: Google Analytics 4 de Dental Ciudad (G-...)
    // Una cuenta de Google Ads por sede: la conversión va a la cuenta de la sede que eligió la persona.
    ads: {
      microcentro: { id: "AW-17043697075", label: "NscFCKi3qa8dELPbiL8_" },  // "Web a WhatsApp", cuenta 173-963-7756
      once: { id: "AW-16487213569", label: "WddDCIaisq8dEIHU27U9" }           // "Web a WhatsApp", cuenta de Once
    },
    // Modo de la conversión (Eduardo, 31/10/2026): "contacto" = todas valen lo mismo (el valor fijo está en Google Ads);
    // "montos" = manda el valor estimado por motivo. Se cambia acá y en la acción de Google Ads, juntos.
    modo: "contacto",
    currency: "USD"   // solo en modo "montos": los valores son puntos relativos, no plata real
  };

  const $ = (id) => document.getElementById(id);
  const el = (tag, cls) => { const n = document.createElement(tag); if (cls) n.className = cls; return n; };
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sin almacenamiento */ } }
  };

  /* Consentimiento (modo de consentimiento v2 de Google): denegado por defecto en el EEE, Reino Unido y Suiza. */
  const CONSENT_REGIONS = ["AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IS","IE","IT","LV","LI","LT",
    "LU","MT","NL","NO","PL","PT","RO","SK","SI","ES","SE","GB","CH"];
  const inEuropeTime = (() => {
    try { return /^Europe\//.test(Intl.DateTimeFormat().resolvedOptions().timeZone || ""); } catch (e) { return false; }
  })();
  const consentChoice = () => { const v = store.get("dc_consent"); return v === "granted" || v === "denied" ? v : null; };
  const consentState = (on) => {
    const v = on ? "granted" : "denied";
    return { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v };
  };

  const adsIds = Object.values(CONFIG.ads).map((a) => a.id).filter(Boolean);
  const tagIds = [CONFIG.analyticsId].concat(adsIds).filter(Boolean);
  (function loadGtag() {
    if (!tagIds.length) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    const g = window.gtag;
    g("consent", "default", Object.assign(consentState(false), { region: CONSENT_REGIONS, wait_for_update: 500 }));
    g("consent", "default", consentState(true));
    const c = consentChoice();
    if (c) g("consent", "update", consentState(c === "granted"));
    g("set", "url_passthrough", true);
    g("set", "ads_data_redaction", true);
    g("js", new Date());
    // Dental: sin personalización de anuncios (política de salud de Google).
    tagIds.forEach((id) => g("config", id, { allow_ad_personalization_signals: false }));
    const s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(tagIds[0]);
    document.head.appendChild(s);
  })();

  function setConsent(on) {
    store.set("dc_consent", on ? "granted" : "denied");
    if (typeof window.gtag === "function") window.gtag("consent", "update", consentState(on));
  }
  function showConsent() {
    if (!tagIds.length) return;
    if (document.querySelector(".consent")) return;
    const box = el("div", "consent");
    box.setAttribute("role", "region");
    box.setAttribute("aria-label", "Cookies");
    const p = el("p");
    p.textContent = "Usamos cookies de Google Analytics y Google Ads para saber cuánta gente visita la página y qué anuncios traen consultas. ";
    const a = el("a"); a.href = "/privacidad/"; a.textContent = "Más información"; p.appendChild(a);
    const row = el("div", "consent-actions");
    const no = el("button", "btn btn-line"); no.type = "button"; no.textContent = "Rechazar";
    const yes = el("button", "btn"); yes.type = "button"; yes.textContent = "Aceptar";
    const close = (on) => { setConsent(on); box.remove(); };
    no.addEventListener("click", () => close(false));
    yes.addEventListener("click", () => close(true));
    row.append(no, yes); box.append(p, row); document.body.appendChild(box);
  }
  if (tagIds.length && inEuropeTime && !consentChoice()) showConsent();
  document.querySelectorAll("[data-cookie-settings]").forEach((b) => {
    if (!tagIds.length) { b.hidden = true; return; }
    b.addEventListener("click", showConsent);
  });

  /* Menú del teléfono: se cierra al elegir */
  document.querySelectorAll("details.menu").forEach((m) => {
    m.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => { m.open = false; }));
    document.addEventListener("click", (e) => { if (m.open && !m.contains(e.target)) m.open = false; });
  });

  /* Formulario */
  const dataEl = $("dc-data");
  const form = $("lead-form");
  if (!dataEl || !form) return;
  const D = JSON.parse(dataEl.textContent);
  const pick = (name) => { const n = form.querySelector('input[name="' + name + '"]:checked'); return n ? n.value : ""; };

  /* Sede de aterrizaje: cada cuenta de Google Ads manda a la página de su sede. Se guarda en la pestaña para que la
     conversión vaya a la cuenta que pagó el clic aunque la persona después elija la otra sede. */
  const ss = { get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* sin almacenamiento */ } } };
  if (D.landing && !ss.get("dc_landing")) ss.set("dc_landing", D.landing);
  const landing = ss.get("dc_landing") || "";

  /* Toques en "Llamar" (evento para Analytics, no es conversión) */
  document.querySelectorAll("[data-llamar]").forEach((a) => {
    a.addEventListener("click", () => { if (typeof window.gtag === "function" && CONFIG.analyticsId) window.gtag("event", "llamar", { sede: a.dataset.llamar }); });
  });

  function makeRef() {
    const abc = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";
    const buf = new Uint32Array(5);
    try { crypto.getRandomValues(buf); } catch (e) { for (let i = 0; i < 5; i++) buf[i] = Math.floor(Math.random() * 1e9); }
    return "DC-" + Array.from(buf, (n) => abc[n % abc.length]).join("");
  }

  const syncObra = () => { $("obra-note").hidden = pick("pago") !== "obra"; };
  const syncPasos = () => { form.querySelectorAll("fieldset.paso").forEach((fs) => { fs.classList.toggle("listo", !!fs.querySelector("input:checked")); }); };
  form.addEventListener("change", (e) => {
    const n = e.target.name;
    if (n) { const err = $("err-" + n); if (err) err.hidden = true; }
    if (n === "pago") syncObra();
    syncPasos();
    if (n) avanzar(e.target.closest("fieldset.paso"));
    pausa = false;
    setTimeout(demo, 1100);
  });

  const reducir = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  /* Pista: «Elegí una opción» en el primer paso sin responder y una mano que va tocando opciones de ese paso, sin
     elegirlas. Se va cuando la persona toca el formulario y vuelve en el paso siguiente. */
  const panel = form.closest(".form-panel");
  const mano = el("div", "mano");
  mano.setAttribute("aria-hidden", "true");
  mano.innerHTML = '<svg viewBox="0 0 24 24"><path d="M9 11.24V7.5C9 6.12 10.12 5 11.5 5S14 6.12 14 7.5v3.74c1.21-.81 2-2.18 2-3.74C16 5.01 13.99 3 11.5 3S7 5.01 7 7.5c0 1.56.79 2.93 2 3.74zm9.84 4.63l-4.54-2.26c-.17-.07-.35-.11-.54-.11H13v-6c0-.83-.67-1.5-1.5-1.5S10 6.67 10 7.5v10.74l-3.43-.72c-.08-.01-.15-.03-.24-.03-.31 0-.59.13-.79.33l-.79.8 4.94 4.94c.27.27.65.44 1.06.44h6.79c.75 0 1.33-.55 1.44-1.28l.75-5.27c.01-.07.02-.14.02-.2 0-.62-.38-1.16-.91-1.38z"/></svg>';
  if (panel) panel.appendChild(mano);
  let manoT = null, visible = false, pausa = false;
  const pasosAll = () => Array.from(form.querySelectorAll("fieldset.paso"));
  const activo = () => pasosAll().find((p) => !p.querySelector("input:checked"));
  function apagarMano() { clearTimeout(manoT); mano.classList.remove("on", "tap"); form.querySelectorAll(".pista").forEach((o) => o.classList.remove("pista")); }
  function demo() {
    apagarMano();
    const fs = activo();
    pasosAll().forEach((p) => p.classList.toggle("activo", p === fs));
    const envio = form.querySelector(".form-send");
    if (envio) envio.classList.toggle("listo", !fs);
    if (!panel || !visible || pausa || reducir) return;
    const opts = fs ? Array.from(fs.querySelectorAll(".opt span")).slice(0, 4) : [form.querySelector('button[type="submit"]')];
    let i = 0;
    const paso = () => {
      const o = opts[i % opts.length];
      const pr = panel.getBoundingClientRect(), r = o.getBoundingClientRect();
      const fx = fs ? 0.8 : 0.72;
      mano.style.transform = "translate(" + (r.left - pr.left + r.width * fx - 21) + "px," + (r.top - pr.top + r.height * 0.55 - 9) + "px)";
      mano.classList.add("on");
      manoT = setTimeout(() => {
        mano.classList.add("tap"); o.classList.add("pista");
        manoT = setTimeout(() => {
          mano.classList.remove("tap"); o.classList.remove("pista"); i++;
          manoT = setTimeout(paso, fs ? (i % opts.length === 0 ? 1400 : 450) : 900);
        }, 380);
      }, 850);
    };
    paso();
  }
  if (panel && "IntersectionObserver" in window) {
    new IntersectionObserver((en) => { visible = en[0].isIntersecting; demo(); }, { threshold: 0.25 }).observe(panel);
  }
  if (panel) panel.addEventListener("pointerdown", () => { pausa = true; apagarMano(); });

  /* Al elegir una opción, la pantalla sube sola hasta el próximo paso sin responder (o el botón de enviar) y lo deja a
     un tercio de la altura, donde está el dedo (Eduardo, 25/10). */
  function avanzar(fs) {
    if (!fs) return;
    const pasos = Array.from(form.querySelectorAll("fieldset.paso"));
    const resto = pasos.slice(pasos.indexOf(fs) + 1);
    let destino = resto.find((p) => !p.querySelector("input:checked"));
    if (!destino) destino = form.querySelector(".form-send");
    if (!destino) return;
    const nota = $("obra-note");
    if (fs.querySelector('input[name="pago"]') && nota && !nota.hidden) destino = nota;
    setTimeout(() => {
      const y = destino.getBoundingClientRect().top + window.scrollY - window.innerHeight / 3;
      window.scrollTo({ top: Math.max(0, y), behavior: reducir ? "auto" : "smooth" });
    }, 120);
  }
  syncObra();
  syncPasos();

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const v = { motivo: pick("motivo"), pago: pick("pago"), sede: pick("sede") };
    const missing = Object.keys(v).filter((k) => !v[k]);
    missing.forEach((k) => { $("err-" + k).hidden = false; });
    if (missing.length) {
      const first = form.querySelector('input[name="' + missing[0] + '"]');
      if (first) first.focus();
      return;
    }
    const sede = D.sedes[v.sede];
    const ref = makeRef();
    const lines = [
      "Hola, les escribo desde la web.",
      "",
      "Quiero: " + D.motivos[v.motivo].label,
      "Pago: " + (v.pago === "obra" ? "con obra social o prepaga" : "particular"),
      "Sede: " + sede.nombre,
      "Código: " + ref
    ];
    const text = lines.join("\n");
    const url = "https://wa.me/" + sede.wa + "?text=" + encodeURIComponent(text);

    /* Conversión: solo si paga particular. Valor = el del tratamiento. Sin nombre, teléfono ni datos de salud.
       Va a la cuenta de la sede de aterrizaje (la que pagó el clic); si entró por el inicio, a la de la sede elegida. */
    const ads = CONFIG.ads[landing] || CONFIG.ads[v.sede];
    if (v.pago === "particular" && typeof window.gtag === "function") {
      const value = D.motivos[v.motivo].valor;
      if (ads && ads.id && ads.label) {
        const conv = { send_to: ads.id + "/" + ads.label, transaction_id: ref };
        if (CONFIG.modo === "montos") Object.assign(conv, { value, currency: CONFIG.currency });
        window.gtag("event", "conversion", conv);
      }
      if (CONFIG.analyticsId) window.gtag("event", "generate_lead", { value, currency: CONFIG.currency, sede: v.sede, aterrizaje: landing || "inicio", motivo: v.motivo });
    }

    $("done-code").textContent = ref;
    $("done-open").href = url;
    $("done").hidden = false;
    if (window.top === window.self) setTimeout(() => { location.href = url; }, 400);
  });

  /* Botón fijo: se esconde mientras los botones de la portada o el formulario están a la vista */
  const sticky = $("sticky");
  const watch = [document.querySelector(".hero .ctas"), $("turno")].filter(Boolean);
  if (sticky && watch.length && "IntersectionObserver" in window) {
    const seen = new Map();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => seen.set(en.target, en.isIntersecting));
      sticky.hidden = Array.from(seen.values()).some(Boolean);
    });
    watch.forEach((el) => io.observe(el));
  }
})();
