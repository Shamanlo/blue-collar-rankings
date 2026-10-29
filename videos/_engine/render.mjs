// Render a Local Vibe Check video from {project}/script.json + {project}/out/timings.json.
//   node _engine/render.mjs <project> landscape|reel [--still t1,t2] [--workers n]
// Builds out/{format}.html, captures every frame with Playwright, encodes with ffmpeg,
// then muxes out/{format}-mix.wav (from audio.py) into out/{name}[-reel].mp4 if it exists.
import { createRequire } from "node:module";
import { spawn, spawnSync } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const ENGINE = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;
const SIZES = { landscape: [1920, 1080], reel: [1080, 1920] };

const args = process.argv.slice(2);
const PROJECT = path.resolve(args[0]);
const OUT = path.join(PROJECT, "out");
const format = args[1] || "landscape";
const still = args.includes("--still") ? args[args.indexOf("--still") + 1] : null;
const workers = args.includes("--workers") ? +args[args.indexOf("--workers") + 1] : 4;
const [W, H] = SIZES[format];

const spec = JSON.parse(readFileSync(path.join(PROJECT, "script.json"), "utf8"));
const timings = JSON.parse(readFileSync(path.join(OUT, "timings.json"), "utf8"))[format];
const scenes = spec[format].map((s, i) => ({ ...s, ...timings[i] }));
const total = scenes.reduce((a, s) => a + s.dur, 0);

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const rel = (p) => path.relative(OUT, p).split(path.sep).join("/");
const img = (f) => rel(path.join(PROJECT, "assets", f));
const engineAsset = (f) => rel(path.join(ENGINE, "assets", f));
const money = (n) => "$" + n.toLocaleString("en-US");
const kfmt = (n) => (n >= 1000 ? "$" + n / 1000 + "M" : "$" + n + "K");
const a = (cls, d, extra = "") => `class="a ${cls}" style="--d:${d}${extra ? ";" + extra : ""}"`;
const cueAttr = (c) => (c ? ` data-cue="${esc(c)}"` : "");
const firstWord = (s) => String(s).split(/[\s(]/).filter(Boolean)[0];

// Re-attach punctuation from the script to the spoken words, for caption chunking.
function punctuate(words, say) {
  let pos = 0;
  return words.map(([t, w]) => {
    const i = say.indexOf(w, pos);
    if (i < 0) return { t, w, end: "" };
    pos = i + w.length;
    const m = say.slice(pos).match(/^[.,?!:;"”]+/);
    return { t, w, end: m ? m[0] : "" };
  });
}

function chunks(words) {
  const out = [];
  let cur = [];
  for (const w of words) {
    cur.push(w);
    if (cur.length >= (format === "reel" ? 3 : 4) || /[.,?!:;]/.test(w.end) || w.w.length > 12) { out.push(cur); cur = []; }
  }
  if (cur.length) out.push(cur);
  return out;
}

const pinSvg = engineAsset("pin.svg");
const photo = (s, dir = "left", d = 0.1, extra = "") =>
  `<div ${a(`${dir} photo`, d)}><img class="kb" src="${img(s.image)}" style="object-position:${s.imgPos || "50% 50%"}${s.zoomFrom ? `;transform-origin:${s.zoomFrom}` : ""}${s.fit ? `;object-fit:contain;background:${s.fit}` : ""}">${extra}</div>`;

const ic = (d) => `<svg viewBox="0 0 48 48" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
const icons = {
  pin: ic(`<path d="M24 43s-13-12.5-13-23a13 13 0 0 1 26 0c0 10.5-13 23-13 23z"/><circle cx="24" cy="20" r="5"/>`),
  star: ic(`<path d="M24 6l5.4 11.4 12.4 1.6-9.1 8.6 2.3 12.3L24 34l-11 5.9 2.3-12.3-9.1-8.6 12.4-1.6z"/>`),
  page: ic(`<rect x="8" y="8" width="32" height="32" rx="4"/><path d="M8 16h32M14 24h20M14 30h14"/>`),
  code: ic(`<path d="M17 14L7 24l10 10M31 14l10 10-10 10M27 10l-6 28"/>`),
  mega: ic(`<path d="M8 20v8h6l14 8V12l-14 8H8zM34 18a8 8 0 0 1 0 12M14 28l3 10h5l-2-9"/>`),
  drop: ic(`<path d="M24 6s-12 13.5-12 22a12 12 0 0 0 24 0C36 19.5 24 6 24 6z"/><path d="M18 30a6 6 0 0 0 6 6"/>`),
  flame: ic(`<path d="M24 42c-8 0-13-5.5-13-12.5C11 20 20 15 19 6c7 4 12 10 12 17 2-2 3-4.5 3-7 3 3.5 4 7.5 4 11.5C38 36.5 32 42 24 42z"/>`),
  roof: ic(`<path d="M5 24L24 9l19 15M11 20v19h26V20M20 39V28h8v11"/>`),
  bolt: ic(`<path d="M27 4L10 27h12l-2 17 18-24H26z"/>`),
  clock: ic(`<circle cx="24" cy="24" r="17"/><path d="M24 14v11l7 4"/>`),
  map: ic(`<path d="M6 12l12-5 12 5 12-5v29l-12 5-12-5-12 5z"/><path d="M18 7v29M30 12v29"/>`),
  shield: ic(`<path d="M24 5l16 6v11c0 10-7 17.5-16 21-9-3.5-16-11-16-21V11z"/><path d="M17 24l5 5 9-10"/>`),
  search: ic(`<circle cx="21" cy="21" r="12"/><path d="M30 30l11 11"/>`),
  chart: ic(`<path d="M7 41h34M12 34V24M20 34V16M28 34V21M36 34V10"/>`),
  wave: `<svg viewBox="0 0 120 80" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"><path d="M8 30c10-10 20-10 30 0s20 10 30 0 20-10 30 0 16 8 16 8"/><path d="M8 54c10-10 20-10 30 0s20 10 30 0 20-10 30 0 16 8 16 8"/></svg>`,
};

const build = {
  title: (s) => `
    <div class="col">
      <div ${a("up kicker", 0.15)}>${esc(s.kicker)}</div>
      <div class="h1"${s.titlePx ? ` style="font-size:${s.titlePx}px"` : ""}>${s.title.map((l, i) => `<div ${a("left", 0.3 + i * 0.25)}>${esc(l)}</div>`).join("")}</div>
      <div ${a("wipe bar-accent", 0.9)}></div>
      <div class="center"><span ${a("pop year", 1.2)}>${esc(s.year)}</span></div>
      <div class="chips">${s.chips.map((c, i) => `<span ${a("pop chip", 1.6 + i * 0.12)}>${esc(c)}</span>`).join("")}</div>
    </div>
    <div class="photowrap">${photo(s, "right", 0.2)}<img class="a pop pinbig" style="--d:1" src="${pinSvg}"></div>`,

  list: (s) => `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    <div ${a("wipe bar-accent", 0.4, "width:420px;margin:22px 0 0")}></div>
    <div class="grid2">${s.items.map((it, i) => `<div class="a up item" data-cue="${esc(firstWord(it))}" style="--d:${0.6 + i * 0.3}"><span class="n">${i + 1}</span>${esc(it)}</div>`).join("")}</div>
    <div class="a fade note"${cueAttr(s.noteCue)} style="--d:4">${esc(s.note)}</div>`,

  bars: (s) => `
    ${photo(s)}
    <div class="col">
      <div ${a("up h2", 0.15)}>${esc(s.title)}</div>
      <div ${a("pop range", 0.45)}>${esc(s.range)}</div>
      <div class="rows">${s.rows.map(([name, v], i) => {
        const d = 0.7 + i * 0.14;
        const best = i === 0 ? " best" : "";
        if (typeof v !== "number") {
          const msg = v === "call" ? "Call for price" : "Doesn't offer";
          return `<div class="row none"><div ${a("left name", d)}>${esc(name)}</div><div class="track"><span ${a("fade missing", d + 0.3)}>${msg}</span></div><div class="val"></div></div>`;
        }
        const pct = Math.max(6, (v / s.max) * 100);
        return `<div class="row${best}"><div ${a("left name", d)}>${esc(name)}</div>
          <div class="track"><div ${a("grow fill", d, `width:${pct}%`)}></div>${best ? `<span class="a pop lowest"${cueAttr(spec.featuredCue)} style="left:${pct}%;--d:${d + 0.9}">LOWEST</span>` : ""}</div>
          <div class="val" data-count="${v}" data-cd="${d}">${money(v)}</div></div>`;
      }).join("")}</div>
    </div>`,

  mini: (s) => `
    ${photo(s)}
    <div class="col">
      <div ${a("up h2", 0.15, "font-size:70px")}>${esc(s.title)}</div>
      <div class="groups">${s.groups.map((g, i) => `
        <div class="a up group"${cueAttr(g.cue)} style="--d:${0.6 + i * 0.5}">
          <div class="gname">${esc(g.name)}</div>
          <div class="span"><span class="orange">${esc(g.low)}</span> <span style="color:#93a0b5">–</span> ${esc(g.high)}</div>
          <div class="gsub">Low: ${esc(g.lowAt)} · High: ${esc(g.highAt)}</div>
        </div>`).join("")}</div>
    </div>`,

  deposit: (s) => build.stats({ ...s, tiles: s.items.map(([n, v, sub]) => ({ v, n, s: sub, cue: firstWord(n) })) }),

  stats: (s) => `
    <div ${a("up h2", 0.1, "text-align:center")}>${esc(s.title)}</div>
    <div class="tiles${s.tiles.length === 3 ? " three" : ""}">${s.tiles.map((t, i) => `
      <div class="a pop tile${i === 0 ? " best" : ""}"${cueAttr(t.cue)} style="--d:${0.5 + i * 0.3}">
        <div class="tv"${s.tvPx ? ` style="font-size:${s.tvPx}px"` : ""}>${esc(t.v)}</div><div class="tn">${esc(t.n)}</div><div class="ts">${esc(t.s)}</div></div>`).join("")}</div>
    ${s.note ? `<div class="a fade note center"${cueAttr(s.noteCue)} style="--d:4">${esc(s.note)}</div>` : ""}`,

  table: (s) => {
    const t = spec.table;
    return `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    <table class="a fade" style="--d:.35">
      <tr><th>${esc(t.corner || "")}</th>${t.cols.map((c, i) => `<th class="${i === 0 ? "ivo" : ""}">${esc(c)}</th>`).join("")}</tr>
      ${t.rows.map((r, ri) => `<tr class="a fade" style="--d:${0.5 + ri * 0.1}">${r.map((c, i) => `<td class="${i === 1 ? "ivo" : ""}${c === "—" || c === "n/a" ? " dash" : ""}">${esc(c)}</td>`).join("")}</tr>`).join("")}
    </table>
    <div class="a pop callout"${cueAttr(s.calloutCue)} style="--d:5">${s.callout}</div>`;
  },

  define: (s) => `
    <div class="col">
      <div ${a("up kicker", 0.2)}>${esc(s.sub)}</div>
      <div ${a("up h2", 0.1, "font-size:110px")}>${esc(s.title)}</div>
      <div ${a("wipe bar-accent", 0.6, "width:520px")}></div>
      <div ${a("up desc", 1)}>${esc(s.lead)}</div>
      <div class="feats">${s.features.map((f, i) => `<div class="a pop feat"${cueAttr(f.cue)} style="--d:${1.5 + i * 0.4}"><i></i>${esc(f.t)}</div>`).join("")}</div>
      <div class="aka a up"${cueAttr(s.akaCue)} style="--d:4"><span>Also called</span>${s.aka.map((c) => `<span class="chip">${esc(c)}</span>`).join("")}</div>
    </div>
    ${photo(s, "right", 0.2)}`,

  // Floating price ranges on a shared axis.
  ranges: (s) => {
    const max = s.max;
    const ticks = s.ticks;
    return `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    ${s.sub ? `<div ${a("up subline", 0.3)}>${esc(s.sub)}</div>` : ""}
    <div class="rangebox">
      <div class="axis">${ticks.map((t) => `<span style="left:${(t / max) * 100}%">${t ? kfmt(t) : "$0"}${t === max ? "+" : ""}</span>`).join("")}</div>
      ${s.rows.map((r, i) => {
        const l = (r.lo / max) * 100, w = ((r.hi - r.lo) / max) * 100;
        return `<div class="rrow"${cueAttr(r.cue)} data-cuegroup>
          <div class="a left rname" style="--d:${0.6 + i * 0.3}">${esc(r.name)}<small>${esc(r.note || "")}</small></div>
          <div class="rtrack">${ticks.map((t) => `<i style="left:${(t / max) * 100}%"></i>`).join("")}
            <div class="a grow rfill c${i}${r.hi / max > 0.75 ? " inside" : ""}" style="left:${l}%;width:${w}%;--d:${0.6 + i * 0.3}"><b>${kfmt(r.lo)} – ${kfmt(r.hi)}${r.plus ? "+" : ""}</b></div>
          </div></div>`;
      }).join("")}
    </div>`;
  },

  // One ADU type: photo + big price range + bullets.
  price: (s) => `
    ${photo(s)}
    <div class="col">
      <div ${a("up kicker", 0.1)}>${esc(s.kicker || "")}</div>
      <div ${a("up h2", 0.2)}>${esc(s.name)}</div>
      <div class="bigprice a pop" style="--d:${s.priceAt ?? 0.8}"${cueAttr(s.priceCue)}>
        <span data-count="${s.lo}" data-fmt="k" data-cd="${s.priceAt ?? 0.8}">${kfmt(s.lo)}</span> – <span data-count="${s.hi}" data-fmt="k" data-cd="${(s.priceAt ?? 0.8) + 0.2}">${kfmt(s.hi)}</span>${s.plus ? "+" : ""}</div>
      <div ${a("up desc", 0.5)}>${esc(s.desc)}</div>
      <ul class="points">${s.bullets.map((p, i) => `<li class="a left"${cueAttr(p.cue)} data-at="${p.cue ? "" : 0.25 + (i * 0.55) / s.bullets.length}" style="--d:2"><i></i>${esc(p.t || p)}</li>`).join("")}</ul>
    </div>`,

  factors: (s) => `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    <div class="fgrid"${s.cols ? ` style="grid-template-columns:repeat(${s.cols},1fr)"` : ""}>${s.cards.map((c, i) => `
      <div class="a pop fcard"${cueAttr(c.cue)} style="--d:${0.6 + i * 0.4}">
        <div class="fi">${c.image ? `<img src="${img(c.image)}" style="object-position:${c.imgPos || "50% 50%"}">` : `<div class="fic">${icons[c.icon] || ""}</div>`}<span class="fn">${i + 1}</span></div>
        <div class="fb"><div class="ft">${esc(c.name)}</div><div class="fd">${esc(c.desc)}</div></div>
      </div>`).join("")}</div>`,

  steps: (s) => `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    ${s.sub ? `<div ${a("up subline", 0.3)}>${esc(s.sub)}</div>` : ""}
    <div class="sgrid">${s.steps.map((st, i) => `
      <div class="a pop step"${cueAttr(st.cue)} style="--d:${0.6 + i * 0.3}">
        <img src="${img(st.image)}" style="object-position:${st.imgPos || "50% 50%"}">${s.plain ? "" : `<span class="sn">${String(i + 1).padStart(2, "0")}</span>`}${st.name ? `<span class="st">${esc(st.name)}</span>` : ""}</div>`).join("")}</div>`,

  // An AI-assistant chat: the customer's question, the answer, and who it names.
  chat: (s) => `
    <div class="chatwin a up" style="--d:.1">
      <div class="chathead"><span class="dot"></span><span class="dot"></span><span class="dot"></span><b>${esc(s.app || "AI assistant")}</b></div>
      <div class="chatbody">
        <div class="bub user a type"${cueAttr(s.askCue)} style="--d:.5">${esc(s.ask)}</div>
        <div class="bub ai a up"${cueAttr(s.answerCue)} style="--d:3">${esc(s.answer)}
          ${s.picks.map((p, i) => `<div class="pick a left" data-at="${(s.pickAt || 0.55) + i * 0.04}" style="--d:4"><span class="pn">${i + 1}</span><span>${esc(p.name)}</span><small>${esc(p.note)}</small></div>`).join("")}
        </div>
        <div class="missing2 a pop"${cueAttr(s.missCue)} data-at="${s.missCue ? "" : 0.85}" style="--d:6"><b>Your business?</b> ${esc(s.miss || "Not mentioned")}</div>
      </div>
    </div>
    ${s.side ? `<div class="col chatside">${s.side.map((t, i) => `<div class="a up sideitem"${cueAttr(t.cue)} style="--d:${1 + i}">${esc(t.t)}</div>`).join("")}</div>` : ""}`,

  // Two-column comparison, e.g. SEO vs AEO.
  versus: (s) => `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    <div class="vs">
      <div class="vrow vhead a fade" style="--d:.3"><span></span><span>${esc(s.left)}</span><span>${esc(s.right)}</span></div>
      ${s.rows.map((r, i) => `<div class="vrow a up"${cueAttr(r.cue)} data-at="${r.cue ? "" : 0.12 + i * 0.13}" style="--d:1"><span>${esc(r.label)}</span><span>${esc(r.a)}</span><span>${esc(r.b)}</span></div>`).join("")}
    </div>
    ${s.note ? `<div class="a fade note center"${cueAttr(s.noteCue)} style="--d:6">${esc(s.note)}</div>` : ""}`,

  reviews: (s) => `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    ${s.sub ? `<div ${a("up subline", 0.3)}>${esc(s.sub)}</div>` : ""}
    <div class="rgrid">${s.cards.map((c, i) => `
      <div class="a up rcard"${cueAttr(c.cue)} style="--d:${0.6 + i * 0.5}">
        <div class="rstars">★★★★★</div>
        <div class="rtext">“${esc(c.text)}”</div>
        <div class="rname2">${esc(c.name)}</div><div class="rmeta">${esc(c.meta)}</div>
      </div>`).join("")}</div>`,

  quote: (s) => `
    ${photo(s)}
    <div class="col">
      <div ${a("pop stars", 0.2)}>★★★★★</div>
      <blockquote ${a("up", 0.5)}>“${esc(s.text)}”</blockquote>
      <div ${a("up qauthor", 0.9)}>${esc(s.author)}</div>
      <div ${a("up qmeta", 1.1)}>${esc(s.meta)}</div>
    </div>`,

  winner: (s) => `
    <div class="col">
      <div ${a("pop stamp", 0.2)}><img src="${pinSvg}">${esc(s.stamp || "Best option")}</div>
      <div class="a up wname" data-cue="${esc(s.nameCue || firstWord(s.name))}" style="--d:1">${esc(s.name)}</div>
      <div class="a up where" data-cue="${esc(s.nameCue || firstWord(s.name))}" style="--d:1.2">${esc(s.where)}</div>
      <ul class="points">${s.points.map((p, i) => `<li class="a left" data-at="${0.3 + (i * 0.6) / s.points.length}" style="--d:2"><i></i>${esc(p)}</li>`).join("")}</ul>
    </div>
    ${photo(s, "right", 0.3, s.logo ? `<div class="a up ivologo" style="--d:1.2;background:${s.logoBg || "#111"}"><img src="${img(s.logo)}"></div>` : "")}`,

  hunts: (s) => `
    <div ${a("up h2", 0.1, `font-size:${format === "reel" ? 84 : 72}px`)}>${esc(s.title)}</div>
    <div class="cards">${s.cards.map((c, i) => `
      <div class="a pop card" data-cue="${esc(c.cue)}" style="--d:${0.6 + i * 0.4}">
        <div class="ci"><img src="${img(c.image)}" style="object-position:${c.imgPos || "50% 40%"}"></div>
        <div class="cb"><div class="cn">${esc(c.name)}</div><div class="cs">${esc(c.sub)}</div></div>
        <div class="cp">${esc(c.price)}</div>
      </div>`).join("")}</div>`,

  cta: (s) => `
    ${photo(s)}
    <div class="col">
      <div ${a("up contact", 0.3)}>
        ${s.logo ? `<img class="clogo" src="${img(s.logo)}">` : ""}
        <div class="cname">${esc(s.name)}</div>
        <div class="a pop phone" data-cue="${esc(s.phoneCue || firstWord(s.phone))}" style="--d:1">${esc(s.phone)}</div>
        <div class="cline">${esc(s.address)}</div>
        <div class="cline">${esc(s.hours)}</div>
        <div class="a up url"${cueAttr(s.urlCue)} style="--d:2">${esc(s.url).replace("\n", "<br>")}</div>
      </div>
      <div class="a up tip" style="--d:.6"><img src="${pinSvg}">${esc(s.tip)}</div>
    </div>`,
};

const sourceKinds = new Set(spec.sourceKinds || ["bars", "mini", "deposit", "table", "list"]);

function html() {
  const sceneHtml = scenes.map((s) => {
    const words = punctuate(s.words, s.say);
    const src = s.source ?? sourceKinds.has(s.kind);
    return `<section class="scene ${s.kind}" data-start="${s.start}" data-dur="${s.dur}" data-words="${esc(JSON.stringify(words))}" data-label="${esc(s.label)}" data-source="${src ? 1 : 0}">${build[s.kind](s)}</section>`;
  }).join("\n");
  const caps = scenes.flatMap((s) => chunks(punctuate(s.words, s.say)).map((c) => ({ t0: s.start + c[0].t - 0.05, words: c.map((w) => [s.start + w.t, w.w]), sceneEnd: s.start + s.dur })));
  const wave = `<svg viewBox="0 0 1200 300" preserveAspectRatio="none">
    <path d="M0 120 C 200 60, 380 200, 640 170 S 1000 90, 1200 150 L1200 300 L0 300Z" fill="#ffd3a1" opacity=".55"/>
    <path d="M0 170 C 160 120, 330 250, 560 240 S 760 260, 820 300 L0 300Z" fill="#7fd6cc" opacity=".55"/>
    <path d="M520 300 C 760 230, 960 160, 1200 120 L1200 300Z" fill="#ffb562" opacity=".5"/>
    <path d="M0 230 C 150 200, 300 270, 470 300 L0 300Z" fill="#2cb6bd" opacity=".45"/></svg>`;
  return `<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="${rel(path.join(ENGINE, "scenes.css"))}">
  <style>:root{--w:${W}px;--h:${H}px}</style></head>
  <body class="${format}"><div class="stage">
    <div class="wave">${wave}</div>
    <div class="dots tr drift"></div>
    <div class="header"><div class="brand"><img src="${pinSvg}"><div><b>LOCAL VIBE CHECK</b><span>${esc(spec.header)}</span></div></div><div class="label" id="label"></div></div>
    ${sceneHtml}
    <div class="caption"><span class="box" id="cap"></span></div>
    <div class="source" id="source">${esc(spec.source)}</div>
  </div>
  <script>
  const CAPS = ${JSON.stringify(caps)};
  const scenes = [...document.querySelectorAll('.scene')];
  const fmt = (n, k) => k === 'k' ? (n >= 1000 ? '$' + (n / 1000).toFixed(n % 1000 ? 2 : 0) + 'M' : '$' + Math.round(n) + 'K') : '$' + Math.round(n).toLocaleString('en-US');
  for (const sc of scenes) {
    const words = JSON.parse(sc.dataset.words);
    const dur = +sc.dataset.dur;
    let ptr = 0;
    const norm = s => s.toLowerCase().replace(/[^a-z0-9$,()]/g, '');
    for (const el of sc.querySelectorAll('[data-cue],[data-at]')) {
      if (el.dataset.at) { el.style.setProperty('--d', (+el.dataset.at * dur).toFixed(3)); continue; }
      if (!el.dataset.cue) continue;
      const cue = norm(el.dataset.cue);
      let i = words.findIndex((w, k) => k >= ptr && norm(w.w).startsWith(cue));
      if (i < 0) i = words.findIndex(w => norm(w.w).startsWith(cue));
      if (i < 0) continue;
      const d = Math.max(0, words[i].t - 0.15).toFixed(3);
      ptr = i;
      // A cued group passes its time to every animated child.
      if (el.hasAttribute('data-cuegroup')) el.querySelectorAll('.a').forEach(c => c.style.setProperty('--d', d));
      else el.style.setProperty('--d', d);
      el.querySelectorAll('[data-cd]').forEach(c => c.dataset.cd = d);
    }
    sc._anims = sc.getAnimations({ subtree: true });
    sc._anims.forEach(a => a.pause());
    sc._counts = [...sc.querySelectorAll('[data-count]')];
  }
  const bgAnims = [...document.querySelectorAll('.drift')].flatMap(e => e.getAnimations());
  bgAnims.forEach(a => a.pause());
  window.renderAt = (t) => {
    let active = scenes[0];
    scenes.forEach((sc, i) => {
      const st = +sc.dataset.start, du = +sc.dataset.dur, lt = t - st;
      const vis = lt >= 0 && lt < du + 0.35;
      if (lt >= 0 && lt < du) active = sc;
      const op = !vis ? 0 : Math.min(1, lt / 0.35);
      sc.style.opacity = op;
      sc.style.zIndex = i + 1;
      sc.style.transform = vis ? 'scale(' + (1.02 - 0.02 * Math.min(1, lt / 0.5)) + ')' : '';
      if (!vis) return;
      sc._anims.forEach(a => a.currentTime = lt * 1000);
      sc._counts.forEach(el => {
        const p = Math.min(1, Math.max(0, (lt - +el.dataset.cd) / 0.9));
        const e = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(+el.dataset.count * e, el.dataset.fmt);
      });
    });
    bgAnims.forEach(a => a.currentTime = t * 1000);
    document.getElementById('label').textContent = active.dataset.label;
    document.getElementById('source').style.opacity = active.dataset.source === '1' ? .85 : 0;
    const cap = document.getElementById('cap');
    let c = null;
    for (let i = 0; i < CAPS.length; i++) {
      const k = CAPS[i], next = CAPS[i + 1];
      const last = k.words[k.words.length - 1][0];
      const end = Math.min(next ? next.t0 : 1e9, last + 0.9, k.sceneEnd);
      if (t >= k.t0 && t < end) { c = k; break; }
    }
    if (!c) { cap.style.visibility = 'hidden'; return; }
    cap.style.visibility = 'visible';
    let cur = -1;
    c.words.forEach((w, i) => { if (t >= w[0] - 0.02) cur = i; });
    cap.innerHTML = c.words.map((w, i) => i === cur ? '<em>' + w[1].replace(/</g, '&lt;') + '</em>' : w[1].replace(/</g, '&lt;')).join(' ');
  };
  window.ready = document.fonts.ready.then(() => Promise.all([...document.images].map(i => i.decode().catch(() => {}))));
  </script></body></html>`;
}

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  await page.goto("file://" + path.join(OUT, `${format}.html`));
  await page.evaluate(() => window.ready);
  return page;
}

function encoder(file) {
  const ff = spawn("ffmpeg", ["-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", String(FPS), file], { stdio: ["pipe", "inherit", "inherit"] });
  const done = new Promise((res, rej) => ff.on("close", (c) => (c ? rej(new Error("ffmpeg " + c)) : res())));
  return { ff, done };
}

async function renderRange(browser, f0, f1, file) {
  const page = await openPage(browser);
  const { ff, done } = encoder(file);
  for (let f = f0; f < f1; f++) {
    await page.evaluate((t) => window.renderAt(t), f / FPS);
    const buf = await page.screenshot({ type: "jpeg", quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    if ((f - f0) % 300 === 0) console.log(`  ${file.split("/").pop()} ${f - f0}/${f1 - f0}`);
  }
  ff.stdin.end();
  await done;
  await page.close();
}

writeFileSync(path.join(OUT, `${format}.html`), html());
const browser = await chromium.launch();
if (still) {
  const page = await openPage(browser);
  for (const t of still.split(",")) {
    await page.evaluate((t) => window.renderAt(t), +t);
    await page.screenshot({ path: path.join(OUT, `still-${format}-${t}.jpg`), type: "jpeg", quality: 85 });
  }
} else {
  const frames = Math.ceil(total * FPS);
  const seg = path.join(OUT, `seg-${format}`);
  rmSync(seg, { recursive: true, force: true });
  mkdirSync(seg, { recursive: true });
  const per = Math.ceil(frames / workers);
  const parts = [];
  for (let i = 0; i < workers; i++) parts.push([i * per, Math.min(frames, (i + 1) * per), path.join(seg, `${i}.mp4`)]);
  console.log(`${format}: ${frames} frames, ${total.toFixed(1)}s`);
  await Promise.all(parts.map(([a, b, f]) => renderRange(browser, a, b, f)));
  writeFileSync(path.join(seg, "list.txt"), parts.map((p) => `file '${p[2]}'`).join("\n"));
  const mix = path.join(OUT, `${format}-mix.wav`);
  if (existsSync(mix)) {
    const name = path.basename(PROJECT) + (format === "reel" ? "-reel" : "") + ".mp4";
    const r = spawnSync("ffmpeg", ["-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", path.join(seg, "list.txt"), "-i", mix,
      "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", path.join(OUT, name)], { stdio: "inherit" });
    if (r.status) throw new Error("mux failed");
    console.log(`wrote out/${name}`);
  } else console.log("video frames done (run audio.py, then re-run to mux)");
}
await browser.close();
