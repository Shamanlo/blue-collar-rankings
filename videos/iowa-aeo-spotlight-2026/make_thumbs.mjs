// Iowa AEO-branded thumbnails (the shared thumbs.mjs uses Local Vibe Check's own type and colors).
//   node videos/iowa-aeo-spotlight-2026/make_thumbs.mjs
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "out");
const A = (f) => "../assets/" + f;
const PIN = "../../_engine/assets/pin.svg";

const css = (w, h) => `
@import url("${A("fonts-local.css")}");
*{margin:0;padding:0;box-sizing:border-box}
body{width:${w}px;height:${h}px;overflow:hidden;font-family:"DM Sans",sans-serif;color:#0E0F0C;
 background:radial-gradient(60% 60% at 88% 8%,#d2efcb 0%,rgba(210,239,203,0) 70%),#F6F5F0;position:relative}
.hl{background:linear-gradient(transparent 50%,#34C73A 50%,#34C73A 84%,transparent 84%);padding:0 .06em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.lvc{display:flex;align-items:center;gap:12px;font:800 30px/1 "Bricolage Grotesque";letter-spacing:-.02em}
.lvc img{height:48px}
.head{font:800 1px/0.98 "Bricolage Grotesque";letter-spacing:-.045em}
.logo{display:block}
.pill{display:inline-block;font:500 1px/1 "DM Mono";letter-spacing:.14em;text-transform:uppercase;background:#0E0F0C;color:#fff;border-radius:999px}
.pill b{color:#34C73A;font-weight:500}
.card{position:absolute;border-radius:28px;overflow:hidden;border:8px solid #fff;box-shadow:0 2px 0 #E3E1D8,0 24px 60px rgba(14,15,12,.18);background:#fff}
.card img{width:100%;height:100%;object-fit:cover;object-position:50% 0;display:block}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{font:600 1px/1 "DM Sans";background:#fff;border:2px solid #E3E1D8;border-radius:999px}
.chip::before{content:"●";color:#34C73A;margin-right:8px}
`;

const youtube = `<!doctype html><html><head><meta charset="utf-8"><style>${css(1280, 720)}
.lvc{position:absolute;left:52px;top:44px}
.head{position:absolute;left:52px;top:128px;width:640px;font-size:92px}
.logo{position:absolute;left:52px;top:470px;height:92px}
.pill{position:absolute;left:52px;top:604px;font-size:20px;padding:14px 22px}
.card{left:720px;top:96px;width:520px;height:540px;transform:rotate(2.5deg)}
</style></head><body>
<div class="lvc"><img src="${PIN}">LOCAL VIBE CHECK</div>
<div class="head">Is AI recommending <span class="hl">your business?</span></div>
<img class="logo" src="${A("iowa-aeo-logo.png")}">
<div class="pill">Local spotlight · <b>2026</b></div>
<div class="card"><img src="${A("iowa-aeo-commercial.jpg")}"></div>
</body></html>`;

const reel = `<!doctype html><html><head><meta charset="utf-8"><style>${css(1080, 1920)}
.lvc{position:absolute;left:0;right:0;top:90px;justify-content:center;font-size:40px}
.lvc img{height:64px}
.head{position:absolute;left:60px;right:60px;top:210px;font-size:126px;text-align:center}
.logo{position:absolute;left:50%;transform:translateX(-50%);top:700px;height:130px}
.chips{position:absolute;left:60px;right:60px;top:880px;justify-content:center}
.chip{font-size:30px;padding:14px 22px}
.card{left:90px;top:1010px;width:900px;height:640px;transform:rotate(-2deg)}
.pill{position:absolute;left:50%;transform:translateX(-50%);top:1730px;font-size:28px;padding:18px 30px;white-space:nowrap}
</style></head><body>
<div class="lvc"><img src="${PIN}">LOCAL VIBE CHECK</div>
<div class="head">Is AI recommending <span class="hl">your business?</span></div>
<img class="logo" src="${A("iowa-aeo-logo.png")}">
<div class="chips"><span class="chip">ChatGPT</span><span class="chip">Gemini</span><span class="chip">Perplexity</span><span class="chip">Claude</span></div>
<div class="card"><img src="${A("iowa-aeo-commercial.jpg")}"></div>
<div class="pill">Local spotlight · <b>Iowa</b></div>
</body></html>`;

const browser = await chromium.launch();
for (const [name, html, w, h] of [["thumbnail-youtube", youtube, 1280, 720], ["thumbnail-reel", reel, 1080, 1920]]) {
  const file = path.join(OUT, name + ".html");
  writeFileSync(file, html);
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.goto("file://" + file);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(OUT, name + ".jpg"), type: "jpeg", quality: 92 });
  await page.close();
}
await browser.close();
console.log("thumbnails done");
