(() => {
  "use strict";

  /* Lo que dice FALTA se completa cuando se prenda esa parte. */
  const CONFIG = {
    analyticsId: "",   // FALTA: Google Analytics 4 de Dental Ciudad (G-...)
    // Una cuenta de Google Ads por sede: la conversión va a la cuenta de la sede que eligió la persona.
    ads: {
      microcentro: { id: "", label: "" },  // FALTA: AW-... y etiqueta de "Consulta web" de la cuenta de Microcentro
      once: { id: "", label: "" }          // FALTA: AW-... y etiqueta de "Consulta web" de la cuenta de Once
    },
    currency: "USD"   // los valores son puntos relativos, no plata real
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

  /* Formulario */
  const dataEl = $("dc-data");
  const form = $("lead-form");
  if (!dataEl || !form) return;
  const D = JSON.parse(dataEl.textContent);
  const pick = (name) => { const n = form.querySelector('input[name="' + name + '"]:checked'); return n ? n.value : ""; };

  function makeRef() {
    const abc = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";
    const buf = new Uint32Array(5);
    try { crypto.getRandomValues(buf); } catch (e) { for (let i = 0; i < 5; i++) buf[i] = Math.floor(Math.random() * 1e9); }
    return "DC-" + Array.from(buf, (n) => abc[n % abc.length]).join("");
  }

  const syncObra = () => { $("obra-note").hidden = pick("pago") !== "obra"; };
  form.addEventListener("change", (e) => {
    const n = e.target.name;
    if (n) { const err = $("err-" + n); if (err) err.hidden = true; }
    if (n === "pago") syncObra();
  });
  syncObra();

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const v = { motivo: pick("motivo"), pago: pick("pago"), cuando: pick("cuando"), sede: pick("sede") };
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
      "Cuándo: " + D.cuando[v.cuando].label.toLowerCase(),
      "Sede: " + sede.nombre,
      "Código: " + ref
    ];
    const text = lines.join("\n");
    const url = "https://wa.me/" + sede.wa + "?text=" + encodeURIComponent(text);

    /* Conversión: solo si paga particular. Valor = tratamiento × cuándo. Sin nombre, teléfono ni datos de salud. */
    const ads = CONFIG.ads[v.sede];
    if (v.pago === "particular" && typeof window.gtag === "function") {
      const value = Math.round(D.motivos[v.motivo].valor * D.cuando[v.cuando].factor * 10) / 10;
      if (ads && ads.id && ads.label) {
        window.gtag("event", "conversion", { send_to: ads.id + "/" + ads.label, value, currency: CONFIG.currency, transaction_id: ref });
      }
      if (CONFIG.analyticsId) window.gtag("event", "generate_lead", { value, currency: CONFIG.currency, sede: v.sede });
    }

    $("done-code").textContent = ref;
    $("done-open").href = url;
    $("done").hidden = false;
    if (window.top === window.self) setTimeout(() => { location.href = url; }, 400);
  });

  /* Botón fijo: se esconde cuando el formulario está a la vista */
  const sticky = $("sticky");
  const card = $("turno");
  if (sticky && card && "IntersectionObserver" in window) {
    new IntersectionObserver((en) => { sticky.hidden = en[0].isIntersecting; }).observe(card);
  }
})();
