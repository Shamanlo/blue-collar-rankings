// Static site generator for bluecollarrankings.com
// Reads data/*.json and writes the finished site to public/.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { topBadge, areaBadge } from "./badges.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUT = path.join(ROOT, "public");
const data = JSON.parse(fs.readFileSync(path.join(ROOT, "data/rankings.json"), "utf8"));
const biz = JSON.parse(fs.readFileSync(path.join(ROOT, "data/businesses.json"), "utf8"));
const { site } = data;
const YEAR = site.year;

// ---------- helpers ----------
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const slugify = (s) => s.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const fmtDate = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
const words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"];
const toSec = (t) => t.split(":").reduce((a, b) => a * 60 + +b, 0);
const naked = (url) => `<a href="${esc(url)}" rel="noopener" target="_blank">${esc(url)}</a>`;
const telHref = (p) => "tel:+1" + String(p).replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
const listJoin = (a) => (a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1]);

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

// ---------- derived data ----------
const rankings = data.rankings
  .map((r) => {
    const url = `/rankings/${r.stateSlug}/${r.citySlug}/${r.slug}/`;
    const area = `${r.city}, ${r.stateAbbr}`;
    const title = `The ${r.count} Best ${r.tradePlural} in ${r.city}`;
    const badgeBase = `${r.citySlug}-${r.slug}-${YEAR}`;
    return {
      ...r, url, area, title,
      topTitle: `#1 Top Ranked ${r.tradePlural.replace(/ies$/, "y").replace(/s$/, "")} in ${area}, ${YEAR}: ${r.winner}`,
      areaTitle: `Best in ${r.city}: ${r.tradePlural}, ranked ${YEAR} by Blue Collar Rankings`,
      topPng: `/badges/${badgeBase}-top-ranked.png`,
      areaPng: `/badges/${badgeBase}-best-in-${r.citySlug}.png`,
      thumb: `/img/thumbs/${r.videoId}.jpg`,
      w: biz[r.winner] || {},
    };
  })
  .sort((a, b) => b.published.localeCompare(a.published) || a.city.localeCompare(b.city));

const cities = [];
for (const r of rankings) {
  let c = cities.find((x) => x.citySlug === r.citySlug && x.stateSlug === r.stateSlug);
  if (!c) cities.push((c = { city: r.city, citySlug: r.citySlug, state: r.state, stateSlug: r.stateSlug, stateAbbr: r.stateAbbr, url: `/rankings/${r.stateSlug}/${r.citySlug}/`, rankings: [] }));
  c.rankings.push(r);
}
cities.sort((a, b) => a.city.localeCompare(b.city));
const states = [...new Set(cities.map((c) => c.stateSlug))].map((s) => {
  const cs = cities.filter((c) => c.stateSlug === s);
  return { state: cs[0].state, stateSlug: s, url: `/rankings/${s}/`, cities: cs, count: cs.reduce((n, c) => n + c.rankings.length, 0) };
}).sort((a, b) => a.state.localeCompare(b.state));
const uniqueBiz = new Set(rankings.flatMap((r) => [r.winner, ...r.contenders]));

// ---------- layout ----------
const NAV = [["/rankings/", "Rankings"], ["/rankings/#cities", "Cities"], ["/badges/", "Badges"], ["/methodology/", "How we rank"], ["/about/", "About"]];

function layout({ title, description, canonical, body, active = "", ogImage = "/img/og-default.jpg", jsonld = [] }) {
  const full = canonical.startsWith("http") ? canonical : site.url + canonical;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${full}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="${esc(site.name)}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${full}">
<meta property="og:image" content="${ogImage.startsWith("http") ? ogImage : site.url + ogImage}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#012456">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="preload" href="/fonts/oswald-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/fonts.css">
<link rel="stylesheet" href="/css/styles.css">
${jsonld.map((j) => `<script type="application/ld+json">${JSON.stringify(j)}</script>`).join("\n")}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="${esc(site.name)} home"><img src="/img/logo-wide.png" alt="${esc(site.name)}" width="653" height="112"></a>
    <button class="menu-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
    <nav class="nav" id="nav">
      ${NAV.map(([h, l]) => `<a href="${h}"${active === h ? ' aria-current="page"' : ""}>${l}</a>`).join("\n      ")}
      <a class="btn btn-primary btn-sm" href="${site.youtube}" rel="noopener" target="_blank">Watch on YouTube</a>
    </nav>
  </div>
</header>
<main id="main">
${body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="foot-logo" href="/"><img src="/img/logo-wide.png" alt="${esc(site.name)}" width="653" height="112"></a>
        <p>Local contractor rankings and home service breakdowns. One trade, one town, one video at a time.</p>
      </div>
      <div>
        <h4>Rankings</h4>
        <ul>
          <li><a href="/rankings/">All ${YEAR} rankings</a></li>
          ${states.map((s) => `<li><a href="${s.url}">${esc(s.state)}</a></li>`).join("\n          ")}
        </ul>
      </div>
      <div>
        <h4>Cities</h4>
        <ul>
          ${cities.map((c) => `<li><a href="${c.url}">${esc(c.city)}, ${c.stateAbbr}</a></li>`).join("\n          ")}
        </ul>
      </div>
      <div>
        <h4>About</h4>
        <ul>
          <li><a href="/methodology/">How we rank</a></li>
          <li><a href="/badges/">Badges</a></li>
          <li><a href="/about/">About us</a></li>
          <li><a href="${site.youtube}" rel="noopener" target="_blank">YouTube</a></li>
        </ul>
      </div>
    </div>
    <div class="legal">© ${YEAR} ${esc(site.name)}. Rankings are editorial opinion based on publicly available information as of the date shown on each ranking. They are not a license, certification or guarantee of work.</div>
  </div>
</footer>
<script>
document.querySelector('.menu-toggle').addEventListener('click',function(){var n=document.getElementById('nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)});
document.querySelectorAll('[data-copy]').forEach(function(b){b.addEventListener('click',function(){var t=document.getElementById(b.dataset.copy).textContent;navigator.clipboard.writeText(t).then(function(){var l=b.textContent;b.textContent='Copied';setTimeout(function(){b.textContent=l},1600)})})});
</script>
</body>
</html>
`;
}

const orgLd = { "@context": "https://schema.org", "@type": "Organization", name: site.name, url: site.url, logo: site.url + "/img/logo-square.jpg", sameAs: [site.youtube] };
const crumbsLd = (items) => ({ "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: items.map(([name, url], i) => ({ "@type": "ListItem", position: i + 1, name, item: site.url + url })) });
const crumbsHtml = (items) => `<ol class="crumbs">${items.map(([n, u], i) => `<li>${i === items.length - 1 ? esc(n) : `<a href="${u}">${esc(n)}</a>`}</li>`).join("")}</ol>`;

// ---------- components ----------
const card = (r) => `<a class="card" href="${r.url}">
  <div class="card-thumb" style="background-image:url('${r.thumb}')"><span class="play">Watch the ranking</span></div>
  <div class="card-body">
    <span class="card-meta">${esc(r.area)} · ${r.count} ranked · ${fmtDate(r.published)}</span>
    <h3>${esc(r.title)}</h3>
    <div class="winner"><span class="pill-1">#1</span><span>Top-rated: <b>${esc(r.winner)}</b></span></div>
  </div>
</a>`;
const cards = (list) => `<div class="cards">${list.map(card).join("\n")}</div>`;

const heroBars = `<div class="hero-bars" aria-hidden="true"><i style="height:90px"></i><i style="height:140px"></i><i style="height:190px"></i><i style="height:240px"></i><i style="height:300px"></i></div>`;

const sampleTop = rankings.find((r) => r.citySlug === "iowa-city") || rankings[0];
const badgeDuo = `<div class="badge-duo">
  <div class="badge-card">
    ${topBadge({ id: "duo-top", area: sampleTop.area, trade: sampleTop.badgeTrade, year: YEAR, title: "#1 Top Ranked badge" })}
    <div><span class="eyebrow">For the winner</span><h3>#1 Top Ranked</h3><p>Awarded to one business per ranking: the company we'd call first after comparing everyone in the video. It carries the trade, the city and the year.</p></div>
  </div>
  <div class="badge-card">
    ${areaBadge({ id: "duo-area", area: sampleTop.city, trade: sampleTop.badgeTrade, year: YEAR, title: "Best in Area badge" })}
    <div><span class="eyebrow">For every business ranked</span><h3>Best in ${esc(sampleTop.city)}</h3><p>Making one of our rankings means a business stood out from everyone else doing that job in town. Every company we rank earns a Best in Area badge for its city and trade.</p></div>
  </div>
</div>`;

const steps = `<div class="steps">
  <div class="step"><div><h3>Pick one trade in one town</h3><p>Each ranking covers a single job, like drain cleaning or water heater installs, in a single market. Homeowners don't hire "contractors," they hire someone to fix one thing.</p></div></div>
  <div class="step"><div><h3>Build the field from public sources</h3><p>We pull the companies that actually do that work locally, then describe each one from its own website, or its Google listing when a site isn't available.</p></div></div>
  <div class="step"><div><h3>Compare what matters to the homeowner</h3><p>Quality, reliability, value and real performance: who answers, who prices up front, who fixes the cause, and how many real customers back up the rating.</p></div></div>
  <div class="step"><div><h3>Publish the video and the reasons</h3><p>The contenders are listed alphabetically and the top-rated pick is revealed at the end, with the reasons it won written out on its ranking page.</p></div></div>
</div>`;

const band = `<section class="band"><div class="wrap"><div><h2>New rankings every week</h2><p>Subscribe on YouTube and see who we'd call first in your town.</p></div><a class="btn" href="${site.youtube}?sub_confirmation=1" rel="noopener" target="_blank">Subscribe on YouTube</a></div></section>`;

// ---------- pages ----------
function homePage() {
  const body = `
<section class="hero">
  ${heroBars}
  <div class="wrap">
    <span class="eyebrow">${YEAR} Edition</span>
    <h1>Local trades, ranked.</h1>
    <p class="lede">We research, compare and rank the plumbers, electricians, restoration crews, remodelers and other pros in your area, then tell you who we'd call first. One trade, one town, one video at a time.</p>
    <div class="actions"><a class="btn btn-primary" href="/rankings/">Browse the rankings</a><a class="btn btn-ghost" href="/methodology/">How we rank</a></div>
  </div>
</section>
<div class="stats"><div class="wrap"><div class="stats-grid">
  <div class="stat"><div class="k">Rankings</div><div class="v">${rankings.length}</div></div>
  <div class="stat"><div class="k">Cities</div><div class="v">${cities.length}</div></div>
  <div class="stat"><div class="k">States</div><div class="v">${states.length}</div></div>
  <div class="stat"><div class="k">Businesses ranked</div><div class="v">${uniqueBiz.size}</div></div>
</div></div></div>

<section class="section">
  <div class="wrap">
    <div class="section-head"><div><span class="eyebrow">Latest</span><h2>The ${YEAR} rankings</h2></div><p>Every ranking comes with the full video, a write-up of each company, and the reasons our top-rated pick won.</p></div>
    ${cards(rankings)}
  </div>
</section>

<section class="section section-alt" id="cities">
  <div class="wrap">
    <div class="section-head"><div><span class="eyebrow">Browse</span><h2>By city</h2></div><p>Every ranking is filed under the town it serves.</p></div>
    <div class="tiles">${cities.map((c) => `<a class="tile" href="${c.url}"><b>${esc(c.city)}</b><span>${esc(c.state)} · ${c.rankings.length} ranking${c.rankings.length > 1 ? "s" : ""}</span></a>`).join("")}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><div><span class="eyebrow">Recognition</span><h2>Two badges, earned</h2></div><p>Businesses can display their badge on their website, truck wraps and quotes. <a href="/badges/">About the badges</a></p></div>
    ${badgeDuo}
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <div class="section-head"><div><span class="eyebrow">Methodology</span><h2>How a ranking is made</h2></div></div>
    ${steps}
  </div>
</section>
${band}`;
  return layout({
    title: `${site.name} | Local contractor rankings for ${YEAR}`,
    description: "Blue Collar Rankings compares local plumbers, electricians, restoration companies, remodelers and other pros, then shows you who to call first. Watch the rankings and see the top-rated pick in your town.",
    canonical: "/",
    body,
    jsonld: [orgLd, { "@context": "https://schema.org", "@type": "WebSite", name: site.name, url: site.url }],
  });
}

function rankingsIndex() {
  const byTrade = [...rankings].sort((a, b) => a.tradePlural.localeCompare(b.tradePlural));
  const body = `
<section class="hero hero-sub"><div class="wrap">
  ${crumbsHtml([["Home", "/"], ["Rankings", "/rankings/"]])}
  <span class="eyebrow">${YEAR} Rankings</span>
  <h1>Every ranking, every town</h1>
  <p class="lede">${rankings.length} rankings across ${cities.length} cities. Pick your town and trade, watch the breakdown, and see who came out on top.</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">All rankings</span><h2>Newest first</h2></div></div>
  ${cards(rankings)}
</div></section>
<section class="section section-alt" id="cities"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Browse</span><h2>By state and city</h2></div></div>
  ${states.map((s) => `<h3 style="margin-top:28px"><a href="${s.url}" style="text-decoration:none">${esc(s.state)}</a></h3><div class="tiles">${s.cities.map((c) => `<a class="tile" href="${c.url}"><b>${esc(c.city)}</b><span>${c.rankings.length} ranking${c.rankings.length > 1 ? "s" : ""}</span></a>`).join("")}</div>`).join("\n")}
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Browse</span><h2>By trade</h2></div></div>
  <div class="cat-list">${byTrade.map((r) => `<div class="cat"><h3><a href="${r.url}">${esc(r.tradePlural)}</a></h3><p>${esc(r.area)} · ${r.count} companies ranked</p><p><span class="pill-1">#1</span> ${esc(r.winner)}</p></div>`).join("")}</div>
</div></section>
${band}`;
  return layout({ title: `All ${YEAR} Rankings | ${site.name}`, description: `Browse all ${rankings.length} Blue Collar Rankings by city and trade, from Iowa City drain cleaners to Denver electricians.`, canonical: "/rankings/", body, active: "/rankings/", jsonld: [crumbsLd([["Home", "/"], ["Rankings", "/rankings/"]])] });
}

function statePage(s) {
  const trail = [["Home", "/"], ["Rankings", "/rankings/"], [s.state, s.url]];
  const list = rankings.filter((r) => r.stateSlug === s.stateSlug);
  const body = `
<section class="hero hero-sub"><div class="wrap">
  ${crumbsHtml(trail)}
  <span class="eyebrow">${YEAR} Rankings · ${esc(s.state)}</span>
  <h1>Top-rated pros in ${esc(s.state)}</h1>
  <p class="lede">${s.count} ranking${s.count > 1 ? "s" : ""} across ${listJoin(s.cities.map((c) => c.city))}.</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="tiles" style="margin-bottom:40px">${s.cities.map((c) => `<a class="tile" href="${c.url}"><b>${esc(c.city)}</b><span>${c.rankings.length} ranking${c.rankings.length > 1 ? "s" : ""}</span></a>`).join("")}</div>
  ${cards(list)}
</div></section>
${band}`;
  return layout({ title: `Best Local Contractors in ${s.state} (${YEAR}) | ${site.name}`, description: `Blue Collar Rankings for ${s.state}: ${list.map((r) => `${r.tradePlural.toLowerCase()} in ${r.city}`).join(", ")}.`, canonical: s.url, body, jsonld: [crumbsLd(trail)] });
}

function cityPage(c) {
  const trail = [["Home", "/"], ["Rankings", "/rankings/"], [c.state, `/rankings/${c.stateSlug}/`], [c.city, c.url]];
  const body = `
<section class="hero hero-sub"><div class="wrap">
  ${crumbsHtml(trail)}
  <span class="eyebrow">${YEAR} Rankings · ${esc(c.city)}, ${c.stateAbbr}</span>
  <h1>Best of ${esc(c.city)}</h1>
  <p class="lede">${c.rankings.length === 1 ? "Our ranking" : `Our ${words[c.rankings.length]} rankings`} for ${esc(c.city)}: ${listJoin(c.rankings.map((r) => r.tradePlural.toLowerCase()))}. Each one names a top-rated pick and the businesses that earned a Best in ${esc(c.city)} badge.</p>
</div></section>
<section class="section"><div class="wrap">
  ${cards(c.rankings)}
  <div class="cat-list" style="margin-top:48px">${c.rankings.map((r) => `<div class="cat"><h3><a href="${r.url}">${esc(r.tradePlural)}</a></h3><p><span class="pill-1">#1</span> <b>${esc(r.winner)}</b></p><p>Also ranked: ${esc(r.contenders.join(", "))}.</p></div>`).join("")}</div>
</div></section>
${band}`;
  return layout({ title: `Best Contractors in ${c.city}, ${c.stateAbbr} (${YEAR}) | ${site.name}`, description: `Top-rated ${c.rankings.map((r) => r.tradePlural.toLowerCase()).join(", ")} in ${c.city}, ${c.state}, ranked by Blue Collar Rankings.`, canonical: c.url, body, jsonld: [crumbsLd(trail)] });
}

function embedBlock(id, heading, text, png, alt, url) {
  const code = `<a href="${site.url}${url}" target="_blank" rel="noopener"><img src="${site.url}${png}" alt="${esc(alt)}" width="200" height="200"></a>`;
  return `<div class="embed">
  <div>
    <h3>${heading}</h3>
    <p>${text}</p>
    <pre id="${id}">${esc(code)}</pre>
    <button class="btn btn-outline btn-sm" data-copy="${id}" type="button">Copy embed code</button>
  </div>
  <div class="preview"><img src="${png}" alt="${esc(alt)}" width="200" height="200"><a href="${png}" download>Download PNG</a></div>
</div>`;
}

function rankingPage(r) {
  const trail = [["Home", "/"], ["Rankings", "/rankings/"], [r.state, `/rankings/${r.stateSlug}/`], [r.city, `/rankings/${r.stateSlug}/${r.citySlug}/`], [r.tradePlural, r.url]];
  const w = r.w;
  const summaryFor = (name) => {
    const b = biz[name] || {};
    return (b.summaries && b.summaries[r.slug]) || b.summary || "";
  };
  const field = r.contenders.map((name) => {
    const b = biz[name] || {};
    const loc = b.city ? `<p class="muted" style="font-size:.88rem">${esc(b.city)}</p>` : "";
    const site_ = b.website ? `<div class="site">${naked(b.website)}</div>` : "";
    return `<li id="${slugify(name)}">
      <div class="mini">${areaBadge({ id: `m-${slugify(name)}`, area: r.city, trade: r.badgeTrade, year: YEAR, title: `Best in ${r.city} badge` })}</div>
      <div><h3>${esc(name)}</h3>${loc}<p>${esc(summaryFor(name))}</p>${site_}</div>
    </li>`;
  }).join("\n");

  const links = [];
  if (w.website) links.push(["Website", naked(w.website)]);
  if (w.servicePage && w.servicePage[r.slug]) links.push(["Service page", naked(w.servicePage[r.slug])]);
  if (w.gbp) links.push([w.gbpIsSearch ? "Google Maps" : "Google Business Profile", naked(w.gbp)]);
  if (w.rating && w.reviews) links.push(["Google rating", `${w.rating.toFixed(1)} stars from ${w.reviews} reviews${w.ratingAsOf ? ` (as of ${esc(w.ratingAsOf)})` : ""}`]);
  if (w.address) links.push(["Address", esc(w.address)]);
  if (w.phone) links.push(["Phone", `<a href="${telHref(w.phone)}">${esc(w.phone)}</a>`]);

  const contendersWord = words[r.contenders.length] || r.contenders.length;
  const ytUrl = `https://www.youtube.com/watch?v=${r.videoId}`;

  const ld = [
    crumbsLd(trail),
    { "@context": "https://schema.org", "@type": "VideoObject", name: r.title + ` (${YEAR})`, description: r.hook + " " + r.intro, thumbnailUrl: `https://i.ytimg.com/vi/${r.videoId}/hqdefault.jpg`, uploadDate: r.published, embedUrl: `https://www.youtube.com/embed/${r.videoId}`, contentUrl: ytUrl },
    {
      "@context": "https://schema.org", "@type": "ItemList", name: `${r.title} (${YEAR})`, itemListOrder: "https://schema.org/ItemListOrderAscending",
      itemListElement: [r.winner, ...r.contenders].map((name, i) => {
        const b = biz[name] || {};
        const item = { "@type": "LocalBusiness", name };
        if (b.website) item.url = b.website;
        if (b.phone) item.telephone = b.phone;
        if (b.address) item.address = b.address;
        if (i === 0 && b.gbp) item.hasMap = b.gbp;
        return { "@type": "ListItem", position: i + 1, item };
      }),
    },
  ];

  const body = `
<section class="hero rank-hero">
  <div class="wrap">
    <div>
      ${crumbsHtml(trail)}
      <span class="eyebrow">${YEAR} Ranking · ${esc(r.area)}</span>
      <h1>${esc(r.title)}</h1>
      <p class="winner-line">#1 Top-rated pick: <b>${esc(r.winner)}</b></p>
      <p class="meta">Published ${fmtDate(r.published)} · Ratings as of ${esc(r.asOf)} · <a href="${ytUrl}" rel="noopener" target="_blank">Watch on YouTube</a></p>
      <div class="actions" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-primary" href="#top-pick">See the #1 pick</a><a class="btn btn-ghost" href="#video">Watch the video</a></div>
    </div>
    <div class="hero-badge">${topBadge({ id: "hero", area: r.area, trade: r.badgeTrade, year: YEAR, title: r.topTitle })}</div>
  </div>
</section>

<section class="section">
  <div class="wrap layout">
    <article class="prose">
      <p style="font-size:1.2rem;color:var(--navy);font-weight:500">${esc(r.hook)}</p>
      <p>${esc(r.intro)} The ${contendersWord} contenders are listed alphabetically, just like in the video, and our top-rated pick gets its own write-up below.</p>
      ${r.method ? `<p>${esc(r.method)}</p>` : ""}
      <p>If you're a homeowner in ${esc(listJoin(r.areas))}, this is a starting point before you request quotes.</p>

      <div class="video" id="video"><iframe src="https://www.youtube-nocookie.com/embed/${r.videoId}?rel=0" title="${esc(r.title)} | Blue Collar Rankings" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
      <p class="chapters">Jump to: ${r.chapters.map(([t, l]) => `<a href="${ytUrl}&amp;t=${toSec(t)}s" rel="noopener" target="_blank">${t} ${esc(l)}</a>`).join(" · ")}</p>

      <section class="top-pick" id="top-pick">
        <div class="tp-head">
          ${topBadge({ id: "tp", area: r.area, trade: r.badgeTrade, year: YEAR, title: r.topTitle })}
          <div><span class="tp-label">#1 Top-rated pick · ${esc(r.tradePlural)} · ${esc(r.area)}</span><h2>${esc(r.winner)}</h2></div>
        </div>
        ${r.winnerWhy.map((p) => `<p>${esc(p)}</p>`).join("\n        ")}
        <ul class="links">
          ${links.map(([k, v]) => `<li><span class="lk">${k}</span><span>${v}</span></li>`).join("\n          ")}
        </ul>
      </section>

      <h2>The rest of the field</h2>
      <p>Listed alphabetically, as in the video. Every company here made the cut and earned a <b>Best in ${esc(r.city)}</b> badge for ${esc(r.tradePlural.toLowerCase())}.</p>
      <ul class="field">
${field}
      </ul>

      <div class="tips">
        <h2>Before you hire</h2>
        <ul>${r.tips.map((t) => `<li>${esc(t)}</li>`).join("")}</ul>
        <p style="margin:12px 0 0">Compare at least two or three companies. The right fit is usually the one that explains the job, the schedule and the price clearly before work starts.</p>
      </div>

      <h2 id="badges">Display the badges</h2>
      <p>Businesses in this ranking may display their badge on their website, social profiles and printed materials. Copy the embed code, or download the PNG.</p>
      ${embedBlock("code-top", "#1 Top Ranked", `For ${esc(r.winner)} only.`, r.topPng, r.topTitle, r.url)}
      ${embedBlock("code-area", `Best in ${esc(r.city)}`, `For every business in this ranking, including ${esc(r.winner)}.`, r.areaPng, r.areaTitle, r.url)}
    </article>

    <aside class="facts" aria-label="Ranking facts">
      <dl>
        <div class="row"><dt>Trade</dt><dd>${esc(r.tradePlural)}</dd></div>
        <div class="row"><dt>City</dt><dd><a href="/rankings/${r.stateSlug}/${r.citySlug}/">${esc(r.city)}</a></dd></div>
        <div class="row"><dt>State</dt><dd><a href="/rankings/${r.stateSlug}/">${esc(r.state)}</a></dd></div>
        <div class="row"><dt>Ranked</dt><dd>${r.count} companies</dd></div>
        <div class="row"><dt>#1 Pick</dt><dd><a href="#top-pick">${esc(r.winner)}</a></dd></div>
        <div class="row"><dt>Published</dt><dd>${fmtDate(r.published)}</dd></div>
      </dl>
      <div class="cta"><a class="btn btn-primary" href="${ytUrl}" rel="noopener" target="_blank">Watch on YouTube</a></div>
    </aside>
  </div>
</section>
${band}`;

  return layout({
    title: `${r.title} (${YEAR}) | ${site.name}`,
    description: `We ranked ${r.count} ${r.tradePlural.toLowerCase()} in ${r.area}. Our #1 top-rated pick: ${r.winner}. Watch the video and read about every company that made the list.`,
    canonical: r.url,
    body,
    ogImage: `https://i.ytimg.com/vi/${r.videoId}/hqdefault.jpg`,
    jsonld: ld,
  });
}

function badgesPage() {
  const trail = [["Home", "/"], ["Badges", "/badges/"]];
  const rows = rankings.map((r) => `<div class="cat"><h3><a href="${r.url}#badges">${esc(r.tradePlural)} · ${esc(r.area)}</a></h3>
    <p><span class="pill-1">#1</span> <b>${esc(r.winner)}</b> (Top Ranked + Best in ${esc(r.city)})</p>
    <p>Best in ${esc(r.city)}: ${esc(r.contenders.join(", "))}</p></div>`).join("");
  const body = `
<section class="hero hero-sub"><div class="wrap">
  ${crumbsHtml(trail)}
  <span class="eyebrow">Recognition</span>
  <h1>The Blue Collar Rankings badges</h1>
  <p class="lede">Two seals, both earned on a public ranking. Nobody pays to be ranked, and nobody pays to win.</p>
</div></section>
<section class="section"><div class="wrap">
  ${badgeDuo}
  <div class="prose" style="max-width:760px;margin-top:48px">
    <h2>Who can display them</h2>
    <p><b>#1 Top Ranked</b> goes to one business per ranking: the top-rated pick revealed at the end of the video. Each badge names the trade, the city and the year it was earned.</p>
    <p><b>Best in Area</b> goes to every business that made a ranking, the winner included. Out of every company doing that job in town, these are the ones worth a call.</p>
    <p>Badge embed codes and PNG downloads are on each ranking page. A badge links back to the ranking that earned it, so customers can see the full breakdown.</p>
  </div>
</div></section>
<section class="section section-alt"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">${YEAR}</span><h2>Badge holders</h2></div></div>
  <div class="cat-list">${rows}</div>
</div></section>
${band}`;
  return layout({ title: `Badges: #1 Top Ranked and Best in Area | ${site.name}`, description: "The #1 Top Ranked and Best in Area badges from Blue Collar Rankings, who has earned them, and how to display them.", canonical: "/badges/", body, active: "/badges/", jsonld: [crumbsLd(trail)] });
}

function simplePage({ slug, eyebrow, h1, lede, content, title, description }) {
  const trail = [["Home", "/"], [h1, `/${slug}/`]];
  const body = `
<section class="hero hero-sub"><div class="wrap">
  ${crumbsHtml(trail)}
  <span class="eyebrow">${eyebrow}</span>
  <h1>${esc(h1)}</h1>
  <p class="lede">${lede}</p>
</div></section>
<section class="section page"><div class="wrap">${content}</div></section>
${band}`;
  return layout({ title, description, canonical: `/${slug}/`, body, active: `/${slug}/`, jsonld: [crumbsLd(trail)] });
}

function notFound() {
  return layout({
    title: `Page not found | ${site.name}`, description: "That page doesn't exist.", canonical: "/404.html",
    body: `<section class="hero hero-sub"><div class="wrap"><span class="eyebrow">404</span><h1>Wrong address</h1><p class="lede">That page isn't here. The rankings are, though.</p><div class="actions"><a class="btn btn-primary" href="/rankings/">Browse the rankings</a><a class="btn btn-ghost" href="/">Home</a></div></div></section>`,
  });
}

// ---------- build ----------
fs.rmSync(OUT, { recursive: true, force: true });
copyDir(path.join(ROOT, "static"), OUT);

write("index.html", homePage());
write("rankings/index.html", rankingsIndex());
for (const s of states) write(`rankings/${s.stateSlug}/index.html`, statePage(s));
for (const c of cities) write(`rankings/${c.stateSlug}/${c.citySlug}/index.html`, cityPage(c));
for (const r of rankings) write(`rankings/${r.stateSlug}/${r.citySlug}/${r.slug}/index.html`, rankingPage(r));
write("badges/index.html", badgesPage());
write("methodology/index.html", simplePage({
  slug: "methodology", eyebrow: "Methodology", h1: "How we rank",
  lede: "No pay-to-play. No random reviews. Just the legwork a homeowner doesn't have time to do.",
  title: `How We Rank Local Contractors | ${site.name}`,
  description: "How Blue Collar Rankings builds each ranking: one trade in one town, companies described from public sources, and a top-rated pick with the reasons written out.",
  content: `${steps}<div class="prose" style="margin-top:44px">
    <h2>What we look at</h2>
    <ul>
      <li><b>Quality.</b> What the company actually does, in its own words, and whether it does the specific job the ranking is about.</li>
      <li><b>Reliability.</b> Availability, response, after-hours policies, and whether they fix the cause or just the symptom.</li>
      <li><b>Value.</b> Upfront estimates, written quotes, and whether the price on the estimate holds.</li>
      <li><b>Real performance.</b> Star ratings weighed together with how many reviews back them up, so a perfect score from five reviews doesn't outrank a near-perfect score from hundreds.</li>
    </ul>
    <h2>What we don't do</h2>
    <p>Businesses don't pay to be included and don't pay to win. Rankings are editorial opinion based on public information as of the date shown on each ranking, and they're a starting point. Always confirm licensing and insurance and get quotes in writing before you hire.</p>
    <h2>The badges</h2>
    <p>The top-rated pick in each ranking earns the <b>#1 Top Ranked</b> badge. Every business in the ranking earns a <b>Best in Area</b> badge. <a href="/badges/">See the badges</a>.</p>
  </div>`,
}));
write("about/index.html", simplePage({
  slug: "about", eyebrow: "About", h1: "About Blue Collar Rankings",
  lede: "We help homeowners find the right local pro for the job, from an emergency water leak to a full remodel.",
  title: `About | ${site.name}`,
  description: "Blue Collar Rankings researches, compares and ranks local blue-collar businesses so homeowners can hire with confidence.",
  content: `<div class="prose">
    <p>Blue Collar Rankings researches, compares and ranks blue-collar businesses in your area, so you can confidently choose the right plumber, electrician, roofer, HVAC tech, remodeler and more.</p>
    <p>No more guessing or relying on random reviews. We break down the options on quality, reliability, value and real performance, so you can hire with confidence. Whether you need someone right now or you're planning a bigger project, we do the legwork and show you the local pros worth calling.</p>
    <p>Every ranking starts as a short video on our <a href="${site.youtube}" rel="noopener" target="_blank">YouTube channel</a>. This site is the written record: the full field, the reasons our top pick won, and direct links to the business so you can call them.</p>
    <h2>Run a local trade business?</h2>
    <p>If your business made one of our rankings, your badge is on your ranking page, ready to embed. Rankings aren't for sale, but we're always looking for the next town and trade to cover. Let us know in the comments on any of our videos.</p>
  </div>`,
}));
write("404.html", notFound());

// sitemap + robots + headers
const urls = ["/", "/rankings/", ...states.map((s) => s.url), ...cities.map((c) => c.url), ...rankings.map((r) => r.url), "/badges/", "/methodology/", "/about/"];
const lastmod = rankings[0].published;
write("sitemap.xml", `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `  <url><loc>${site.url}${u}</loc><lastmod>${lastmod}</lastmod></url>`).join("\n")}\n</urlset>\n`);
write("robots.txt", `User-agent: *\nAllow: /\n\nSitemap: ${site.url}/sitemap.xml\n`);
write("_headers", `/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n/img/*\n  Cache-Control: public, max-age=604800\n/badges/*\n  Cache-Control: public, max-age=86400\n  Access-Control-Allow-Origin: *\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n`);

// badge sources for the PNG renderer
const badgeJobs = rankings.flatMap((r) => [
  { out: r.topPng, svg: topBadge({ id: "x", area: r.area, trade: r.badgeTrade, year: YEAR, title: r.topTitle }) },
  { out: r.areaPng, svg: areaBadge({ id: "x", area: r.city, trade: r.badgeTrade, year: YEAR, title: r.areaTitle }) },
]);
fs.writeFileSync(path.join(ROOT, "scripts/.badge-jobs.json"), JSON.stringify(badgeJobs));

console.log(`Built ${urls.length} pages, ${badgeJobs.length} badge sources -> public/`);
