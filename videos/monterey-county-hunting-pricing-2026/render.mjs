// Render the Local Vibe Check pricing video from script.json + out/timings.json.
//   node render.mjs landscape|reel [--still t] [--workers n]
// Builds out/{format}.html, captures every frame with Playwright, encodes with ffmpeg.
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "out");
const FPS = 30;
const SIZES = { landscape: [1920, 1080], reel: [1080, 1920] };

const args = process.argv.slice(2);
const format = args[0] || "landscape";
const still = args.includes("--still") ? args[args.indexOf("--still") + 1] : null;
const workers = args.includes("--workers") ? +args[args.indexOf("--workers") + 1] : 4;
const [W, H] = SIZES[format];

const spec = JSON.parse(readFileSync(path.join(HERE, "script.json"), "utf8"));
const timings = JSON.parse(readFileSync(path.join(OUT, "timings.json"), "utf8"))[format];
const scenes = spec[format].map((s, i) => ({ ...s, ...timings[i] }));
const total = scenes.reduce((a, s) => a + s.dur, 0);

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const img = (f) => `../assets/${f}`;
const money = (n) => "$" + n.toLocaleString("en-US");
const a = (cls, d, extra = "") => `class="a ${cls}" style="--d:${d}${extra ? ";" + extra : ""}"`;

// Re-attach punctuation from the script to the spoken words, for caption chunking.
function punctuate(words, say) {
  let pos = 0;
  return words.map(([t, w]) => {
    const i = say.indexOf(w, pos);
    if (i < 0) return { t, w, end: "" };
    pos = i + w.length;
    const m = say.slice(pos).match(/^[.,?!:;]+/);
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

const pinSvg = img("pin.svg");

const build = {
  title: (s) => `
    <div class="col">
      <div ${a("up kicker", 0.15)}>${esc(s.kicker)}</div>
      <div class="h1">${s.title.map((l, i) => `<div ${a("left", 0.3 + i * 0.25)}>${esc(l)}</div>`).join("")}</div>
      <div ${a("wipe bar-accent", 0.9)}></div>
      <div class="center"><span ${a("pop year", 1.2)}>${esc(s.year)}</span></div>
      <div class="chips">${s.chips.map((c, i) => `<span ${a("pop chip", 1.6 + i * 0.12)}>${esc(c)}</span>`).join("")}</div>
    </div>
    <div class="photowrap"><div ${a("right photo", 0.2)}><img class="kb" src="${img(s.image)}"></div><img class="a pop pinbig" style="--d:1" src="${pinSvg}"></div>`,

  list: (s) => `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    <div ${a("wipe bar-accent", 0.4, "width:420px;margin:22px 0 0")}></div>
    <div class="grid2">${s.items.map((it, i) => `<div class="a up item" data-cue="${esc(it.split(" ")[0])}" style="--d:${0.6 + i * 0.3}"><span class="n">${i + 1}</span>${esc(it)}</div>`).join("")}</div>
    <div class="a fade note" data-cue="Every" style="--d:4">${esc(s.note)}</div>`,

  bars: (s) => `
    <div ${a("left photo", 0.1)}><img class="kb" src="${img(s.image)}"></div>
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
          <div class="track"><div ${a("grow fill", d, `width:${pct}%`)}></div>${best ? `<span class="a pop lowest" data-cue="Indian" style="left:${pct}%;--d:${d + 0.9}">LOWEST</span>` : ""}</div>
          <div class="val" data-count="${v}" data-cd="${d}">${money(v)}</div></div>`;
      }).join("")}</div>
    </div>`,

  mini: (s) => `
    <div ${a("left photo", 0.1)}><img class="kb" src="${img(s.image)}"></div>
    <div class="col">
      <div ${a("up h2", 0.15, "font-size:70px")}>${esc(s.title)}</div>
      <div class="groups">${s.groups.map((g, i) => `
        <div class="a up group" data-cue="${["quail", "Coyote", "squirrel"][i]}" style="--d:${0.6 + i * 0.5}">
          <div class="gname">${esc(g.name)}</div>
          <div class="span"><span class="orange">${esc(g.low)}</span> <span style="color:#93a0b5">–</span> ${esc(g.high)}</div>
          <div class="gsub">Low: ${esc(g.lowAt)} · High: ${esc(g.highAt)}</div>
        </div>`).join("")}</div>
    </div>`,

  deposit: (s) => `
    <div ${a("up h2", 0.1, "text-align:center")}>${esc(s.title)}</div>
    <div class="tiles">${s.items.map(([n, v, sub], i) => `
      <div class="a pop tile${i === 0 ? " best" : ""}" data-cue="${esc(n.split(" ")[0])}" style="--d:${0.5 + i * 0.3}">
        <div class="tv">${esc(v)}</div><div class="tn">${esc(n)}</div><div class="ts">${esc(sub)}</div></div>`).join("")}</div>`,

  table: (s) => {
    const t = spec.table;
    return `
    <div ${a("up h2", 0.1)}>${esc(s.title)}</div>
    <table class="a fade" style="--d:.35">
      <tr><th>Hunt</th>${t.cols.map((c, i) => `<th class="${i === 0 ? "ivo" : ""}">${esc(c)}</th>`).join("")}</tr>
      ${t.rows.map((r, ri) => `<tr class="a fade" style="--d:${0.5 + ri * 0.1}">${r.map((c, i) => `<td class="${i === 1 ? "ivo" : ""}${c === "—" || c === "n/a" ? " dash" : ""}">${esc(c)}</td>`).join("")}</tr>`).join("")}
    </table>
    <div class="a pop callout" data-cue="9,500" style="--d:5">Up to <b>$9,500 more</b> for the same hunt</div>`;
  },

  winner: (s) => `
    <div class="col">
      <div ${a("pop stamp", 0.2)}><img src="${pinSvg}">Best option</div>
      <div class="a up wname" data-cue="Indian" style="--d:1">${esc(s.name)}</div>
      <div class="a up where" data-cue="Indian" style="--d:1.2">${esc(s.where)}</div>
      <ul class="points">${s.points.map((p, i) => `<li class="a left" data-at="${0.3 + (i * 0.6) / s.points.length}" style="--d:2"><i></i>${esc(p)}</li>`).join("")}</ul>
    </div>
    <div ${a("right photo", 0.3)}><img class="kb" src="${img(s.image)}"><div class="a up ivologo" style="--d:1.2"><img src="${img("ivo-logo.png")}"></div></div>`,

  hunts: (s) => `
    <div ${a("up h2", 0.1, `font-size:${format === "reel" ? 84 : 72}px`)}>${esc(s.title)}</div>
    <div class="cards">${s.cards.map((c, i) => `
      <div class="a pop card" data-cue="${esc(c.cue)}" style="--d:${0.6 + i * 0.4}">
        <div class="ci"><img src="${img(c.image)}" style="object-position:${c.imgPos || "50% 40%"}"></div>
        <div class="cb"><div class="cn">${esc(c.name)}</div><div class="cs">${esc(c.sub)}</div></div>
        <div class="cp">${esc(c.price)}</div>
      </div>`).join("")}</div>`,

  cta: (s) => `
    <div ${a("left photo", 0.1)}><img class="kb" src="${img(s.image)}"></div>
    <div class="col">
      <div ${a("up contact", 0.3)}>
        <div class="cname">${esc(s.name)}</div>
        <div class="a pop phone" data-cue="(669)" style="--d:1">${esc(s.phone)}</div>
        <div class="cline">${esc(s.address)}</div>
        <div class="cline">${esc(s.hours)}</div>
        <div class="a up url" data-cue="${format === "reel" ? "Full" : "see"}" style="--d:2">${esc(s.url).replace("\n", "<br>")}</div>
      </div>
      <div class="a up tip" style="--d:.6"><img src="${pinSvg}">${esc(s.tip)}</div>
    </div>`,
};

const priceScenes = new Set(["bars", "mini", "deposit", "table", "list"]);

function html() {
  const sceneHtml = scenes.map((s) => {
    const words = punctuate(s.words, s.say);
    return `<section class="scene ${s.kind}" data-start="${s.start}" data-dur="${s.dur}" data-words="${esc(JSON.stringify(words))}" data-label="${esc(s.label)}" data-source="${priceScenes.has(s.kind) ? 1 : 0}">${build[s.kind](s)}</section>`;
  }).join("\n");
  const caps = scenes.flatMap((s) => chunks(punctuate(s.words, s.say)).map((c) => ({ t0: s.start + c[0].t - 0.05, words: c.map((w) => [s.start + w.t, w.w]), sceneEnd: s.start + s.dur })));
  const wave = `<svg viewBox="0 0 1200 300" preserveAspectRatio="none">
    <path d="M0 120 C 200 60, 380 200, 640 170 S 1000 90, 1200 150 L1200 300 L0 300Z" fill="#ffd3a1" opacity=".55"/>
    <path d="M0 170 C 160 120, 330 250, 560 240 S 760 260, 820 300 L0 300Z" fill="#7fd6cc" opacity=".55"/>
    <path d="M520 300 C 760 230, 960 160, 1200 120 L1200 300Z" fill="#ffb562" opacity=".5"/>
    <path d="M0 230 C 150 200, 300 270, 470 300 L0 300Z" fill="#2cb6bd" opacity=".45"/></svg>`;
  return `<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="../scenes.css">
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
  const fmtMoney = n => '$' + Math.round(n).toLocaleString('en-US');
  for (const sc of scenes) {
    const words = JSON.parse(sc.dataset.words);
    const dur = +sc.dataset.dur;
    let ptr = 0;
    const norm = s => s.toLowerCase().replace(/[^a-z0-9$,()]/g, '');
    for (const el of sc.querySelectorAll('[data-cue],[data-at]')) {
      if (el.dataset.at) { el.style.setProperty('--d', (+el.dataset.at * dur).toFixed(3)); continue; }
      const cue = norm(el.dataset.cue);
      let i = words.findIndex((w, k) => k >= ptr && norm(w.w).startsWith(cue));
      if (i < 0) i = words.findIndex(w => norm(w.w).startsWith(cue));
      if (i >= 0) { el.style.setProperty('--d', Math.max(0, words[i].t - 0.15).toFixed(3)); ptr = i; }
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
        el.textContent = fmtMoney(+el.dataset.count * e);
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
  console.log("video frames done");
}
await browser.close();
