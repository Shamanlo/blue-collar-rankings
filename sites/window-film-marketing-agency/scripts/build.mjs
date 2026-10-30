// Static site generator for windowfilmmarketingagency.com
// Reads scripts/content.mjs and writes the finished site to public/.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { site, services, webDesignIndex, webDesign, specialties, home, about, reel, work } from "./content.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUT = path.join(ROOT, "public");
const ASSET_V = Date.now().toString(36);
fs.rmSync(OUT, { recursive: true, force: true });

// ---------- helpers ----------
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const jsonLd = (o) => `<script type="application/ld+json">${JSON.stringify(o).replace(/</g, "\\u003c")}</script>`;

function write(rel, html) {
  const file = path.join(OUT, rel);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, html);
}
function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name), d = path.join(dst, e.name);
    e.isDirectory() ? copyDir(s, d) : fs.copyFileSync(s, d);
  }
}

// ---------- icons (24px stroke icons) ----------
const ICONS = {
  spark: '<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="3"/>',
  pin: '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
  store: '<path d="M3 9.5 4.5 4h15L21 9.5M3 9.5h18M3 9.5a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0M5 12v8h14v-8M10 20v-5h4v5"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  star: '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
  layout: '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 9h18M9 9v11"/>',
  refresh: '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8M4 4v4h4M4 13a8 8 0 0 0 14.3 4.9L20 16M20 20v-4h-4"/>',
  map: '<path d="m9 4-6 2.5v13.5l6-2.5 6 2.5 6-2.5V4l-6 2.5zM9 4v13.5M15 6.5V20"/>',
  image: '<rect x="3" y="4" width="18" height="16" rx="2.5"/><circle cx="8.5" cy="9.5" r="1.5"/><path d="m21 16-5-5-9 9"/>',
  form: '<rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M8 8h8M8 12h8M8 16h5"/>',
  shield: '<path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.4 7.5 9.5 4.3-1.1 7.5-4.9 7.5-9.5V6z"/><path d="m9 12 2 2 4-4"/>',
  home: '<path d="M3 11 12 3.5 21 11M5.5 9v11h13V9"/><rect x="9.5" y="12" width="5" height="5" rx=".5"/>',
  building: '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M8 7h2M14 7h2M8 11h2M14 11h2M8 15h2M14 15h2M10.5 21v-3h3v3"/>',
  lock: '<rect x="4.5" y="10.5" width="15" height="10.5" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3M12 14.5v2.5"/>',
  spray: '<path d="M8 9h6v12H8zM9.5 9V6h3v3M14 4h1M17 3h1M17 6h1M20 4.5h1M17 9h1"/>',
  grid: '<rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="M3.5 12h17M12 3.5v17"/><path d="M14 6.5l4 4M14 9.5l1.5 1.5" />',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>',
  car: '<path d="M5 16.5h14M3.5 16.5v-4l2-5h13l2 5v4h-2M5.5 16.5H3.5M6.5 12h11"/><circle cx="7.5" cy="17" r="1.8"/><circle cx="16.5" cy="17" r="1.8"/>',
  video: '<rect x="2.5" y="6" width="13" height="12" rx="2.5"/><path d="m15.5 10.5 6-3.5v10l-6-3.5"/>',
  social: '<path d="M20.5 11.5a8 8 0 0 1-11.9 7l-5.1 1.5 1.5-4.9a8 8 0 1 1 15.5-3.6z"/><path d="M8.5 11.5h.01M12.5 11.5h.01M16.5 11.5h.01"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  calendar: '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
  send: '<path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4z"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  chev: '<path d="m6 9 6 6 6-6"/>',
  x: '<path d="M6 6l12 12M18 6 6 18"/>',
};
const icon = (name, size = 22) =>
  `<svg class="i" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]}</svg>`;

const LOGO_MARK = `<svg class="logo-mark" width="36" height="36" viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="lg-tint" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFC94D"/><stop offset="1" stop-color="#F08A00"/></linearGradient></defs><rect x="2" y="2" width="36" height="36" rx="9" fill="#0C1B2A"/><rect x="8" y="8" width="11" height="11" rx="2" fill="url(#lg-tint)"/><rect x="21" y="8" width="11" height="11" rx="2" fill="#2A4A63"/><rect x="8" y="21" width="11" height="11" rx="2" fill="#2A4A63"/><rect x="21" y="21" width="11" height="11" rx="2" fill="url(#lg-tint)" opacity=".55"/></svg>`;
const LOGO = `<a class="logo" href="/" aria-label="${esc(site.name)} home">${LOGO_MARK}<span class="logo-txt"><b>Window Film</b><small>Marketing Agency</small></span></a>`;

// ---------- sections ----------
const groups = [
  { key: "services", label: "Marketing", base: "/services/", items: services, all: "All marketing services" },
  { key: "web-design", label: "Web Design", base: "/web-design/", items: webDesign, all: "Web design overview" },
  { key: "specialties", label: "Who We Serve", base: "/specialties/", items: specialties, all: "All film specialties" },
];
const url = (g, p) => `${g.base}${p.slug}/`;

function header(active) {
  const drop = (g) => `<li class="has-drop${active === g.key ? " is-active" : ""}">
      <button class="nav-top" aria-expanded="false">${esc(g.label)}${icon("chev", 16)}</button>
      <div class="drop"><ul>${g.items.map((p) => `<li><a href="${url(g, p)}">${icon(p.icon, 18)}<span>${esc(p.nav)}</span></a></li>`).join("")}</ul>
      <a class="drop-all" href="${g.base}">${esc(g.all)} ${icon("arrow", 16)}</a></div></li>`;
  return `<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap hdr">
  ${LOGO}
  <nav class="nav" aria-label="Main"><ul class="nav-list">
    ${groups.map(drop).join("")}
    <li><a class="nav-top${active === "about" ? " is-active" : ""}" href="/about/">About</a></li>
    <li><a class="nav-top${active === "contact" ? " is-active" : ""}" href="/contact/">Contact</a></li>
  </ul></nav>
  <div class="hdr-cta">
    <a class="btn btn-primary btn-sm" href="/contact/#form">Free Marketing Audit</a>
    <button class="menu-btn" aria-label="Open menu" aria-expanded="false">${icon("menu", 24)}</button>
  </div>
</div></header>`;
}

function footer() {
  const col = (g) => `<div><h4>${esc(g.label)}</h4><ul>${g.items.map((p) => `<li><a href="${url(g, p)}">${esc(p.nav)}</a></li>`).join("")}</ul></div>`;
  return `<footer class="site-footer"><div class="wrap">
  <div class="ftr-grid">
    <div class="ftr-brand">${LOGO}<p>${esc(site.tagline)}</p>
      <p><a class="ftr-mail" href="mailto:${site.email}">${icon("mail", 18)}${site.email}</a></p></div>
    ${groups.map(col).join("")}
    <div><h4>Company</h4><ul><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="/contact/?topic=call#form">Book a call</a></li><li><a href="/privacy/">Privacy</a></li></ul></div>
  </div>
  <div class="ftr-bottom"><span>© ${site.year} ${esc(site.name)}</span><span>Marketing and web design for window film companies.</span></div>
</div></footer>`;
}

function layout({ path: p, title, desc, active, body, ld = [] }) {
  const canonical = site.url + p;
  const org = { "@type": "ProfessionalService", "@id": site.url + "/#org", name: site.name, url: site.url + "/", email: site.email, description: site.tagline, logo: site.url + "/img/icon-512.png", areaServed: "US", knowsAbout: ["Window film marketing", "Window tinting SEO", "Answer engine optimization", "Web design for window film companies", "Video editing for window film companies", "Social media management for window film companies"] };
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="${esc(site.name)}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${canonical}">
<meta property="og:image" content="${site.url}/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0C1B2A">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=DM+Mono:wght@400;500&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site.css?v=${ASSET_V}">
${jsonLd({ "@context": "https://schema.org", "@graph": [org, ...ld] })}
</head>
<body>
${header(active)}
<main id="main">
${body}
</main>
${footer()}
<script src="/js/site.js?v=${ASSET_V}" defer></script>
</body>
</html>
`;
}

const crumbs = (trail) => `<nav class="crumbs" aria-label="Breadcrumb">${trail.map(([n, u], i) => (i < trail.length - 1 ? `<a href="${u}">${esc(n)}</a><span>/</span>` : `<span aria-current="page">${esc(n)}</span>`)).join("")}</nav>`;
const crumbLd = (trail) => ({ "@type": "BreadcrumbList", itemListElement: trail.map(([n, u], i) => ({ "@type": "ListItem", position: i + 1, name: n, item: site.url + u })) });
const faqLd = (faq) => ({ "@type": "FAQPage", mainEntity: faq.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })) });

const ctaButtons = (second = ["Submit a Form", "#form", "send"]) => `<div class="hero-ctas">
  <a class="btn btn-primary" href="/contact/?topic=call#form">Book a Call ${icon("calendar", 18)}</a>
  <a class="btn btn-ghost" href="${second[1]}">${second[0]} ${icon(second[2], 18)}</a>
</div>`;

const card = (g, p) => `<a class="card svc-card" href="${url(g, p)}"><span class="svc-ic">${icon(p.icon, 24)}</span><h3>${esc(p.nav)}</h3><p>${esc(p.card)}</p><span class="more">Learn more ${icon("arrow", 16)}</span></a>`;

function faqSection(faq, h = "Questions, answered") {
  return `<section class="sec" id="faq"><div class="wrap narrow">
  <div class="sec-head center"><p class="eyebrow">FAQ</p><h2>${esc(h)}</h2></div>
  <div class="faq">${faq.map((f, i) => `<details${i === 0 ? " open" : ""}><summary>${esc(f.q)}<span class="plus" aria-hidden="true"></span></summary><p>${esc(f.a)}</p></details>`).join("")}</div>
</div></section>`;
}

function leadForm() {
  const films = ["Residential tint", "Commercial film", "Security & safety film", "Anti-graffiti film", "Decorative & privacy film", "Solar & skylight film", "Auto tint & PPF"];
  return `<form class="lead" action="https://api.web3forms.com/submit" method="POST" data-key="${esc(site.web3formsKey)}" data-email="${site.email}">
  <input type="hidden" name="access_key" value="${esc(site.web3formsKey)}">
  <input type="hidden" name="subject" value="New lead from ${site.domain}">
  <input type="hidden" name="from_name" value="${esc(site.name)} website">
  <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
  <div class="f-row">
    <label>Your name<input name="name" autocomplete="name" required></label>
    <label>Company<input name="company" autocomplete="organization" required></label>
  </div>
  <div class="f-row">
    <label>Email<input type="email" name="email" autocomplete="email" required></label>
    <label>Phone<input type="tel" name="phone" autocomplete="tel"></label>
  </div>
  <div class="f-row">
    <label>Website<input name="website" placeholder="yourtintcompany.com" inputmode="url"></label>
    <label>What do you need?<select name="topic">
      <option value="Free marketing audit">Free marketing audit</option>
      <option value="Book a call">Book a call</option>
      <option value="New website">New website or redesign</option>
      <option value="Local SEO / AI search">Local SEO / AI search</option>
      <option value="Video editing">Video editing</option>
      <option value="Social media management">Social media management</option>
    </select></label>
  </div>
  <fieldset class="chips"><legend>Films you install</legend>
    ${films.map((f) => `<label class="chip"><input type="checkbox" name="films" value="${esc(f)}"><span>${esc(f)}</span></label>`).join("")}
  </fieldset>
  <label>Service area and anything else we should know<textarea name="message" rows="4" placeholder="Cities you serve, film brands you carry, what's working and what isn't"></textarea></label>
  <button class="btn btn-primary btn-wide" type="submit">Send ${icon("send", 18)}</button>
  <p class="f-status" role="status" aria-live="polite"></p>
</form>`;
}

// Client work: a phone-framed YouTube Short that loads the player only on tap
function ytPhone(w) {
  return `<div class="reel-phone"><div class="phone" data-yt="${w.youtube}" data-title="${esc(w.client + ": " + w.title)}">
      <img src="${w.poster}" width="540" height="960" alt="${esc(w.client + " video: " + w.title)}" loading="lazy">
      <button class="reel-play" type="button" aria-label="Play the ${esc(w.client)} video"><svg width="34" height="34" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z" fill="currentColor"/></svg></button>
      <span class="reel-sound">YouTube Short</span>
    </div></div>`;
}
function workSection(head = {}) {
  const [w, ...more] = work;
  const [ctaT, ctaU] = head.cta || ["See video editing", "/services/video-editing/"];
  return `<section class="sec${head.cls === undefined ? " sec-tint" : head.cls}" id="work"><div class="wrap split">
  <div>
    <p class="eyebrow">${esc(head.eyebrow || "Client work")}</p>
    <h2>${head.h || 'Short-form video for <span class="hl">window film installers</span>'}</h2>
    <p class="lead-sm">${esc(head.lead || "We edit Shorts, Reels and TikToks for film companies from footage their teams shoot on the job. Here's one we made for MD Window Films.")}</p>
    <div class="card work-card"><p class="work-kind">${esc(w.kind)}</p><h3>${esc(w.client)}</h3><p>${esc(w.desc)}</p></div>
    <div class="hero-ctas"><a class="btn btn-primary" href="${ctaU}">${esc(ctaT)} ${icon("arrow", 18)}</a><a class="btn btn-ghost" href="https://www.youtube.com/shorts/${w.youtube}" target="_blank" rel="noopener">Watch on YouTube</a></div>
  </div>
  ${ytPhone(w)}
</div>${more.length ? `<div class="wrap work-grid">${more.map(ytPhone).join("")}</div>` : ""}</section>`;
}

function ctaSection(h = ["Are buyers finding you, ", "or your competitors?"]) {
  return `<section class="sec cta-dark" id="form"><div class="wrap cta-grid">
  <div class="cta-copy">
    <p class="eyebrow">Free marketing audit</p>
    <h2>${esc(h[0])}<span class="hl">${esc(h[1])}</span></h2>
    <p>Tell us where you install and what films you sell. We'll search your market on Google and five AI assistants and send back who shows up, why, and what to fix first.</p>
    <ul class="ticks">
      <li>${icon("check", 18)}No cost, no obligation</li>
      <li>${icon("check", 18)}Real results from Google and 5 AI assistants</li>
      <li>${icon("check", 18)}Plain-English next steps, by film type</li>
    </ul>
    <p class="small">Prefer email? <a href="mailto:${site.email}">${site.email}</a></p>
  </div>
  <div class="card form-card">${leadForm()}</div>
</div></section>`;
}

// ---------- pages ----------
const pages = [];
const addPage = (p, opts) => {
  pages.push(p);
  write(p === "/" ? "index.html" : p.slice(1) + "index.html", layout({ path: p, ...opts }));
};

// Home
{
  const svcCards = services.map((p) => card(groups[0], p)).join("");
  const s = home.sim;
  const simData = { questions: s.questions, signals: s.signals.map((x) => x.key) };
  const body = `
<section class="hero"><div class="wrap hero-inner">
  <p class="badge">${esc(home.badge)}</p>
  <h1>${esc(home.h1[0])}<span class="hl">${esc(home.h1[1])}</span></h1>
  <p class="lead">${esc(home.lead)}</p>
  ${ctaButtons()}
</div></section>

<section class="reel-sec" id="reel"><div class="wrap reel-grid">
  <div class="reel-copy">
    <p class="eyebrow">Watch · ${reel.duration} seconds</p>
    <h2>Your next <span class="hl">$20,000 job</span> is searching right now</h2>
    <p class="lead-sm">${esc(reel.lead)}</p>
    <ul class="ticks">${reel.points.map(([b, d]) => `<li>${icon("check", 18)}<span><b>${esc(b)}.</b> ${esc(d)}</span></li>`).join("")}</ul>
    <div class="hero-ctas"><a class="btn btn-primary" href="/contact/#form">Get a Free Marketing Audit ${icon("arrow", 18)}</a></div>
  </div>
  <div class="reel-phone">
    <div class="phone" data-reel>
      <img src="/video/reel-poster.jpg" width="540" height="960" alt="${esc(reel.alt)}">
      <button class="reel-play" type="button" data-src="/video/reel.mp4" aria-label="Play the ${reel.duration}-second video with sound"><svg width="34" height="34" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z" fill="currentColor"/></svg></button>
      <span class="reel-sound">Tap for sound</span>
    </div>
  </div>
</div></section>

<section class="sec sim-sec" id="try-it"><div class="wrap">
  <div class="sec-head center"><p class="eyebrow">Try it yourself</p>
    <h2>See how buyers pick <span class="hl">a window film company</span></h2>
    <p>Pick a buyer's question, choose where they ask it, then switch on the signals we build. Watch what happens to your company in the answer.</p></div>
  <div class="sim" data-sim>
    <script type="application/json" class="sim-data">${JSON.stringify(simData).replace(/</g, "\\u003c")}</script>
    <div class="sim-left">
      <div class="card sim-card"><h3><span class="num">1</span>Pick a buyer's question</h3><div class="sim-qs">${s.questions.map((q, i) => `<button class="sim-q${i === 0 ? " is-on" : ""}" data-q="${i}" aria-pressed="${i === 0}">${esc(q.q)}</button>`).join("")}</div></div>
      <div class="card sim-card"><h3><span class="num">2</span>Where they ask</h3><div class="sim-chs">${s.channels.map((c, i) => `<button class="sim-ch${i === 0 ? " is-on" : ""}" data-ch="${esc(c)}" aria-pressed="${i === 0}">${esc(c)}</button>`).join("")}</div></div>
      <div class="card sim-card"><h3><span class="num">3</span>Switch on the signals</h3><div class="sim-ts">${s.signals.map((x) => `<label class="sim-t"><input type="checkbox" data-sig="${x.key}"><span class="sw" aria-hidden="true"></span><span class="sim-t-txt"><strong>${esc(x.t)}</strong><small>${esc(x.d)}</small></span></label>`).join("")}</div>
        <div class="sim-btns"><button class="btn btn-dark btn-sm" data-all>Turn all on</button><button class="btn btn-ghost btn-sm" data-reset>Reset</button></div></div>
    </div>
    <div class="sim-right">
      <div class="card sim-answer">
        <div class="sim-meter"><div class="sim-meter-top"><span>Chance you're recommended</span><b data-pct>6%</b></div><div class="bar"><i data-bar style="width:6%"></i></div><span class="sim-state" data-state>INVISIBLE</span></div>
        <div class="sim-chat"><p class="sim-ask" data-ask></p><div class="sim-reply" data-reply></div></div>
      </div>
      <p class="sim-note">Illustration only. Real answers vary by market; your free audit shows what buyers actually see.</p>
    </div>
  </div>
</div></section>

<section class="strip"><div class="wrap"><p>Getting you found everywhere buyers look</p><ul>${home.platforms.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div></section>

<section class="sec" id="services"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">What we do</p><h2>More estimates for the <span class="hl">films you sell</span></h2>
    <p>Everything a window film company needs to get found and booked, run by people who know the difference between a 4 mil safety film and a 14 mil security film.</p></div>
  <div class="grid-3">${svcCards}</div>
  <div class="center-btn"><a class="btn btn-primary" href="/contact/#form">Get a Free Marketing Audit ${icon("arrow", 18)}</a></div>
</div></section>

${workSection()}

<section class="sec sec-dark" id="web-design"><div class="wrap split">
  <div>
    <p class="eyebrow">Web design</p>
    <h2>Websites built to <span class="hl">sell window film</span></h2>
    <p class="lead-sm">A page for every film type, proof for every buyer and an estimate form that collects what you need to quote.</p>
    <ul class="ticks">${webDesign[0].points.items.map((x) => `<li>${icon("check", 18)}<span><b>${esc(x.t)}.</b> ${esc(x.d)}</span></li>`).join("")}</ul>
    <div class="hero-ctas"><a class="btn btn-primary" href="/web-design/">See web design ${icon("arrow", 18)}</a></div>
  </div>
  ${browserMock()}
</div></section>

<section class="sec" id="how"><div class="wrap">
  <div class="sec-head center"><p class="eyebrow">How it works</p><h2>From hard to find <span class="hl">to fully booked</span></h2>
    <p>A clear, repeatable process. No tricks, just making your company easy for buyers, Google and AI to understand and trust.</p></div>
  <ol class="steps">${home.steps.map((x, i) => `<li class="card"><span class="step-n">0${i + 1}</span><h3>${esc(x.t)}</h3><p>${esc(x.d)}</p></li>`).join("")}</ol>
</div></section>

<section class="sec sec-tint" id="who"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">Who we serve</p><h2>Built for every kind of <span class="hl">window film company</span></h2>
    <p>Residential installers, commercial contractors, security specialists, decorative studios and tint shops with an auto bay. Each film has its own buyers, and we market to each one.</p></div>
  <div class="grid-4">${specialties.map((p) => `<a class="card spec-card" href="${url(groups[2], p)}"><span class="svc-ic">${icon(p.icon, 22)}</span><h3>${esc(p.nav)}</h3><p>${esc(p.card)}</p><span class="more">Learn more ${icon("arrow", 16)}</span></a>`).join("")}
  <a class="card spec-card spec-cta" href="/contact/#form"><h3>Not sure where to start?</h3><p>Get a free audit of your market and see which films are worth pushing first.</p><span class="more">Get my audit ${icon("arrow", 16)}</span></a></div>
</div></section>

<section class="sec" id="compare"><div class="wrap">
  <div class="sec-head center"><p class="eyebrow">Why a specialist</p><h2>Generic agency vs. <span class="hl">window film agency</span></h2></div>
  <div class="table-wrap"><table class="compare"><thead><tr><th></th><th>Generic marketing agency</th><th>Window Film Marketing Agency</th></tr></thead>
  <tbody>${home.compare.rows.map((r) => `<tr><th scope="row">${esc(r[0])}</th><td>${esc(r[1])}</td><td>${icon("check", 18)}${esc(r[2])}</td></tr>`).join("")}</tbody></table></div>
</div></section>

${faqSection(home.faq)}
${ctaSection()}`;
  const videoLd = { "@type": "VideoObject", name: reel.title, description: reel.lead, thumbnailUrl: site.url + "/video/reel-poster.jpg", contentUrl: site.url + "/video/reel.mp4", uploadDate: reel.uploaded, duration: `PT${reel.duration}S`, publisher: { "@id": site.url + "/#org" } };
  addPage("/", { title: home.metaTitle, desc: home.metaDesc, active: "home", body, ld: [faqLd(home.faq), videoLd, { "@type": "WebSite", "@id": site.url + "/#site", url: site.url + "/", name: site.name, publisher: { "@id": site.url + "/#org" } }] });
}

function browserMock() {
  return `<div class="mock" aria-hidden="true">
    <div class="mock-bar"><i></i><i></i><i></i><span>yourtintcompany.com/commercial-window-film/</span></div>
    <div class="mock-body">
      <div class="mock-nav"><b></b><span></span><span></span><span></span><em>Free Estimate</em></div>
      <div class="mock-hero"><small>COMMERCIAL WINDOW FILM</small><strong>Cut heat and glare without losing the view</strong><div class="mock-btns"><em>Request a site survey</em><span>View projects</span></div></div>
      <div class="mock-specs"><div><b>99%</b><small>UV rejected</small></div><div><b>60%+</b><small>Solar heat cut</small></div><div><b>8–14 mil</b><small>Security film</small></div></div>
      <div class="mock-cards"><div><i class="sw1"></i><small>Solar film</small></div><div><i class="sw2"></i><small>Security film</small></div><div><i class="sw3"></i><small>Frosted privacy</small></div></div>
    </div>
  </div>`;
}

// Detail page (services, web design, specialties)
function detailPage(g, p) {
  const u = url(g, p);
  const trail = [["Home", "/"], [g.label, g.base], [p.nav, u]];
  const others = g.items.filter((x) => x !== p);
  const parts = [];
  parts.push(`<section class="hero hero-sub"><div class="wrap">${crumbs(trail)}
  <p class="eyebrow">${esc(p.eyebrow)}</p><h1>${esc(p.title)}</h1><p class="lead">${esc(p.lead)}</p>${ctaButtons()}</div></section>`);
  parts.push(`<section class="sec"><div class="wrap split split-top"><div><p class="eyebrow">Why it matters</p><h2>${esc(p.intro.h)}</h2></div><div class="prose">${p.intro.p.map((x) => `<p>${esc(x)}</p>`).join("")}</div></div></section>`);
  parts.push(`<section class="sec sec-tint"><div class="wrap"><div class="sec-head"><p class="eyebrow">${esc(p.nav)}</p><h2>${esc(p.points.h)}</h2></div>
  <div class="grid-3">${p.points.items.map((x, i) => `<div class="card pt-card"><span class="step-n">${String(i + 1).padStart(2, "0")}</span><h3>${esc(x.t)}</h3><p>${esc(x.d)}</p></div>`).join("")}</div></div></section>`);
  if (p.work) parts.push(workSection({ cls: "", ...p.work }));
  if (p.sitemap) parts.push(`<section class="sec"><div class="wrap"><div class="sec-head"><p class="eyebrow">Site structure</p><h2>${esc(p.sitemap.h)}</h2><p>Modeled on how buyers actually shop for film: by property type, then by film, then by proof.</p></div>
  <div class="sitemap"><div class="sm-root">${icon("home", 18)} Home</div><div class="sm-cols">${p.sitemap.groups.map((x) => `<div class="card sm-col"><h3>${esc(x.t)}</h3><ul>${x.items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul></div>`).join("")}</div></div></div></section>`);
  if (p.asks) parts.push(`<section class="sec sec-dark"><div class="wrap split split-top"><div><p class="eyebrow">${esc(p.asks.eyebrow || "Search demand")}</p><h2>${esc(p.asks.h)}</h2><p class="lead-sm">${esc(p.asks.sub || "We build pages, profiles and reviews that answer these exact questions, so Google and AI assistants send the buyer to you.")}</p></div>
  <ul class="asks">${p.asks.items.map((x) => `<li>${icon("spark", 18)}<span>${esc(x)}</span></li>`).join("")}</ul></div></section>`);
  if (p.jargon) parts.push(`<section class="sec"><div class="wrap"><div class="sec-head"><p class="eyebrow">We speak film</p><h2>The terms your buyers compare</h2><p>We write your pages with the specs and vocabulary buyers use when comparing installers, explained in plain English.</p></div>
  <dl class="gloss">${p.jargon.map((x) => `<div class="card"><dt>${esc(x.t)}</dt><dd>${esc(x.d)}</dd></div>`).join("")}</dl></div></section>`);
  parts.push(`<section class="sec sec-tint"><div class="wrap"><div class="sec-head"><p class="eyebrow">Keep exploring</p><h2>More ${esc(g.label.toLowerCase())}</h2></div><div class="grid-3">${others.slice(0, 6).map((x) => card(g, x)).join("")}</div></div></section>`);
  if (p.faq?.length) parts.push(faqSection(p.faq));
  parts.push(ctaSection());
  const svcLd = { "@type": "Service", name: p.title, description: p.metaDesc, provider: { "@id": site.url + "/#org" }, areaServed: "US", audience: { "@type": "BusinessAudience", name: "Window film and window tinting companies" }, url: site.url + u };
  addPage(u, { title: p.metaTitle, desc: p.metaDesc, active: g.key, body: parts.join("\n"), ld: [crumbLd(trail), svcLd, ...(p.faq?.length ? [faqLd(p.faq)] : [])] });
}

// Group index pages
function indexPage(g, meta, extra = "") {
  const trail = [["Home", "/"], [g.label, g.base]];
  const body = `<section class="hero hero-sub"><div class="wrap">${crumbs(trail)}
  <p class="eyebrow">${esc(meta.eyebrow)}</p><h1>${esc(meta.title)}</h1><p class="lead">${esc(meta.lead)}</p>${ctaButtons()}</div></section>
<section class="sec"><div class="wrap"><div class="grid-3">${g.items.map((p) => card(g, p)).join("")}</div></div></section>
${extra}
${ctaSection()}`;
  addPage(g.base, { title: meta.metaTitle, desc: meta.metaDesc, active: g.key, body, ld: [crumbLd(trail)] });
}

indexPage(groups[0], { eyebrow: "Marketing services", title: "Marketing Services for Window Film Companies", metaTitle: "Marketing Services for Window Film Companies", metaDesc: "Local SEO, AI search optimization, Google Business Profile, video editing, social media management and review generation for window tinting and window film companies.", lead: "Every service is built around how residential, commercial and security film buyers search, compare and book." });
indexPage(groups[1], webDesignIndex, `<section class="sec sec-dark"><div class="wrap split"><div><p class="eyebrow">What you get</p><h2>Every site, <span class="hl">built to book estimates</span></h2>
<ul class="ticks">${webDesign[0].points.items.map((x) => `<li>${icon("check", 18)}<span><b>${esc(x.t)}.</b> ${esc(x.d)}</span></li>`).join("")}</ul></div>${browserMock()}</div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><p class="eyebrow">Site structure</p><h2>${esc(webDesign[0].sitemap.h)}</h2></div>
<div class="sitemap"><div class="sm-root">${icon("home", 18)} Home</div><div class="sm-cols">${webDesign[0].sitemap.groups.map((x) => `<div class="card sm-col"><h3>${esc(x.t)}</h3><ul>${x.items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul></div>`).join("")}</div></div></div></section>
${faqSection(webDesign[0].faq, "Web design questions")}`);
indexPage(groups[2], { eyebrow: "Who we serve", title: "Marketing for Every Kind of Window Film Company", metaTitle: "Who We Serve | Marketing for Window Film Companies", metaDesc: "Marketing for residential tint, commercial window film, security film, anti-graffiti, decorative, solar and skylight film, and auto tint and PPF shops.", lead: "Each film type has its own buyers, searches and proof. Pick yours to see how we market it." });

for (const g of groups) for (const p of g.items) detailPage(g, p);

// About
{
  const trail = [["Home", "/"], ["About", "/about/"]];
  const body = `<section class="hero hero-sub"><div class="wrap">${crumbs(trail)}
  <p class="eyebrow">About us</p><h1>Marketing built only for <span class="hl">window film companies</span></h1><p class="lead">${esc(about.lead)}</p>${ctaButtons()}</div></section>
<section class="sec"><div class="wrap split split-top"><div><p class="eyebrow">Why we exist</p><h2>Window film isn't a generic trade. Its marketing shouldn't be either.</h2></div><div class="prose">${about.why.map((x) => `<p>${esc(x)}</p>`).join("")}</div></div></section>
<section class="sec sec-tint"><div class="wrap"><div class="sec-head"><p class="eyebrow">How we work</p><h2>What you can count on</h2></div>
<div class="grid-2">${about.values.map((x) => `<div class="card pt-card"><h3>${esc(x.t)}</h3><p>${esc(x.d)}</p></div>`).join("")}</div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head center"><p class="eyebrow">How it works</p><h2>From hard to find <span class="hl">to fully booked</span></h2></div>
<ol class="steps">${home.steps.map((x, i) => `<li class="card"><span class="step-n">0${i + 1}</span><h3>${esc(x.t)}</h3><p>${esc(x.d)}</p></li>`).join("")}</ol></div></section>
${ctaSection()}`;
  addPage("/about/", { title: about.metaTitle, desc: about.metaDesc, active: "about", body, ld: [crumbLd(trail), { "@type": "AboutPage", url: site.url + "/about/", about: { "@id": site.url + "/#org" } }] });
}

// Contact
{
  const trail = [["Home", "/"], ["Contact", "/contact/"]];
  const body = `<section class="hero hero-sub"><div class="wrap">${crumbs(trail)}
  <p class="eyebrow">Contact</p><h1>Let's get your film company <span class="hl">found and booked</span></h1>
  <p class="lead">Book a call or send the form. We'll come back with a free audit of your market: who ranks, who AI recommends, and what to fix first.</p></div></section>
${ctaSection(["Tell us about ", "your film company"])}`;
  addPage("/contact/", { title: "Contact | Window Film Marketing Agency", desc: "Book a call or request a free marketing audit for your window film company.", active: "contact", body, ld: [crumbLd(trail), { "@type": "ContactPage", url: site.url + "/contact/" }] });
}

// Privacy
{
  const trail = [["Home", "/"], ["Privacy", "/privacy/"]];
  const body = `<section class="hero hero-sub"><div class="wrap">${crumbs(trail)}<h1>Privacy policy</h1><p class="lead">Last updated October ${site.year}.</p></div></section>
<section class="sec"><div class="wrap narrow prose">
<p>${esc(site.name)} ("we") runs ${site.domain}. This page explains what we collect and why.</p>
<h2>What we collect</h2><p>When you send a form, we receive the details you enter (name, company, email, phone, website and message). Forms are delivered to our inbox by Web3Forms. We use this information only to respond to you and prepare your audit or proposal.</p>
<h2>Videos</h2><p>Client videos on this site come from YouTube and only load when you press play. After that, YouTube's privacy policy applies to that video.</p>
<h2>Analytics</h2><p>We may use privacy-friendly, cookie-free analytics (Cloudflare Web Analytics) to count visits. It does not track you across sites.</p>
<h2>Sharing</h2><p>We don't sell your information. We share it only with services that help us run this site and deliver our work, or when required by law.</p>
<h2>Your choices</h2><p>Email <a href="mailto:${site.email}">${site.email}</a> to see, correct or delete what we have about you.</p>
</div></section>`;
  addPage("/privacy/", { title: "Privacy Policy | Window Film Marketing Agency", desc: "How Window Film Marketing Agency handles information sent through this website.", active: "", body });
}

// 404
write("404.html", layout({ path: "/404", title: "Page not found | Window Film Marketing Agency", desc: "That page doesn't exist.", active: "", body: `<section class="hero hero-sub"><div class="wrap"><p class="eyebrow">404</p><h1>That page is <span class="hl">tinted out</span></h1><p class="lead">We couldn't find that page. Try the home page or one of these.</p><div class="hero-ctas"><a class="btn btn-primary" href="/">Home ${icon("arrow", 18)}</a><a class="btn btn-ghost" href="/web-design/">Web design</a><a class="btn btn-ghost" href="/services/">Marketing services</a></div></div></section>` }).replace(/<link rel="canonical"[^>]*>\n/, '<meta name="robots" content="noindex">\n'));

// sitemap, robots, llms.txt
const today = new Date().toISOString().slice(0, 10);
write("sitemap.xml", `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map((p) => `  <url><loc>${site.url}${p}</loc><lastmod>${today}</lastmod></url>`).join("\n")}
</urlset>
`);
write("robots.txt", `User-agent: *\nAllow: /\n\nSitemap: ${site.url}/sitemap.xml\n`);
write("llms.txt", `# ${site.name}

> ${site.tagline} We work only with window tinting and window film companies: residential, commercial, security and safety, anti-graffiti, decorative and privacy, solar and skylight, and auto tint and PPF.

Contact: ${site.email} or ${site.url}/contact/

## Marketing services
${services.map((p) => `- [${p.nav}](${site.url}${url(groups[0], p)}): ${p.card}`).join("\n")}

## Web design
${webDesign.map((p) => `- [${p.nav}](${site.url}${url(groups[1], p)}): ${p.card}`).join("\n")}

## Who we serve
${specialties.map((p) => `- [${p.nav}](${site.url}${url(groups[2], p)}): ${p.card}`).join("\n")}
`);

copyDir(path.join(ROOT, "static"), OUT);
console.log(`Built ${pages.length} pages into public/`);
