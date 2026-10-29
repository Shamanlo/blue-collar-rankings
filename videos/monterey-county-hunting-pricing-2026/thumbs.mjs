// Render YouTube (1280x720) and Reel/Shorts (1080x1920) thumbnails to out/.
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "out");

const css = `
@font-face { font-family: "Anton"; src: url("../assets/anton.woff2"); }
@font-face { font-family: "Poppins"; font-weight: 800; src: url("../assets/poppins-800.woff2"); }
@font-face { font-family: "Poppins"; font-weight: 700; src: url("../assets/poppins-700.woff2"); }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: var(--w); height: var(--h); overflow: hidden; font-family: "Poppins", sans-serif; color: #0b2545;
  background: radial-gradient(90% 80% at 0% 0%, #cdeee8 0%, rgba(205,238,232,0) 55%),
              radial-gradient(90% 80% at 100% 100%, #ffd7a8 0%, rgba(255,215,168,0) 60%),
              linear-gradient(115deg, #f2fbf8, #fbf8ef 50%, #fff0dc); position: relative; }
.wave { position: absolute; left: 0; right: 0; bottom: 0; height: 22%; }
.wave svg { width: 100%; height: 100%; display: block; }
.dots { position: absolute; background-image: radial-gradient(currentColor 3.4px, transparent 3.8px); background-size: 22px 22px; opacity: .6; }
.brand { position: absolute; display: flex; align-items: center; gap: 12px; }
.brand img { height: 64px; }
.brand b { font: 400 36px/1 "Anton"; letter-spacing: .02em; }
.photo { position: absolute; border: 10px solid #fff; border-radius: 34px; overflow: hidden; box-shadow: 0 24px 60px rgba(11,37,69,.3); }
.photo img { width: 100%; height: 100%; object-fit: cover; display: block; }
.big { font: 400 1px/0.92 "Anton"; text-transform: uppercase; }
.tag { display: inline-block; font: 400 1px/1 "Anton"; text-transform: uppercase; color: #fff; border-radius: 18px; }
.grad { height: 12px; border-radius: 12px; background: linear-gradient(90deg, #19b3b8, #7fc9b0 45%, #ff8e0a); }
.pin { position: absolute; filter: drop-shadow(0 16px 22px rgba(11,37,69,.35)); }
.stamp { position: absolute; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 50%;
  background: #0b2545; color: #fff; text-align: center; box-shadow: 0 16px 40px rgba(11,37,69,.35); border: 6px solid #fff; }
`;

const wave = `<div class="wave"><svg viewBox="0 0 1200 300" preserveAspectRatio="none">
  <path d="M0 120 C 200 60, 380 200, 640 170 S 1000 90, 1200 150 L1200 300 L0 300Z" fill="#ffd3a1" opacity=".6"/>
  <path d="M0 170 C 160 120, 330 250, 560 240 S 760 260, 820 300 L0 300Z" fill="#7fd6cc" opacity=".6"/>
  <path d="M520 300 C 760 230, 960 160, 1200 120 L1200 300Z" fill="#ffb562" opacity=".55"/>
  <path d="M0 230 C 150 200, 300 270, 470 300 L0 300Z" fill="#2cb6bd" opacity=".5"/></svg></div>`;

const landscape = `
<div class="dots" style="color:#ff8e0a;right:24px;top:24px;width:130px;height:90px"></div>
${wave}
<div class="photo" style="right:44px;top:70px;width:560px;height:590px;transform:rotate(2.5deg)"><img src="../assets/trophy-boar-tusks-monterey-county.jpg" style="object-position:50% 45%"></div>
<div class="stamp" style="right:470px;top:40px;width:190px;height:190px;transform:rotate(-8deg)">
  <div style="font:400 64px/1 Anton">6</div><div style="font:800 21px/1.1 Poppins;letter-spacing:.06em">OUTFITTERS<br>COMPARED</div></div>
<img class="pin" src="../assets/pin.svg" style="right:540px;bottom:40px;height:150px">
<div class="brand" style="left:44px;top:34px"><img src="../assets/pin.svg"><b>LOCAL VIBE CHECK</b></div>
<div style="position:absolute;left:44px;top:120px;width:680px">
  <div class="big" style="font-size:156px">Hunting<br>Prices</div>
  <div class="big" style="font-size:66px;color:#19b3b8;margin-top:10px">Monterey County, CA</div>
  <div class="grad" style="width:600px;margin:20px 0 22px"></div>
  <span class="tag" style="font-size:66px;background:#ff8e0a;padding:12px 24px 16px;box-shadow:0 12px 30px rgba(247,123,0,.4)">$550 – $12,500</span>
  <span class="tag" style="font-size:66px;background:#0b2545;padding:12px 22px 16px;margin-left:10px">2026</span>
</div>`;

const reel = `
<div class="dots" style="color:#19b3b8;left:40px;top:200px;width:160px;height:110px"></div>
<div class="dots" style="color:#ff8e0a;right:40px;top:200px;width:160px;height:110px"></div>
${wave}
<div class="brand" style="left:0;right:0;top:110px;justify-content:center"><img src="../assets/pin.svg" style="height:86px"><b style="font-size:52px">LOCAL VIBE CHECK</b></div>
<div style="position:absolute;left:0;right:0;top:300px;text-align:center">
  <div class="big" style="font-size:250px">Hunting<br>Prices</div>
  <div class="big" style="font-size:86px;color:#19b3b8;margin-top:18px">Monterey County, CA</div>
  <div class="grad" style="width:760px;margin:30px auto"></div>
  <span class="tag" style="font-size:104px;background:#ff8e0a;padding:16px 36px 22px;box-shadow:0 14px 34px rgba(247,123,0,.4)">$550 – $12,500</span>
</div>
<div class="photo" style="left:110px;top:1200px;width:860px;height:560px;transform:rotate(-2deg)"><img src="../assets/trophy-boar-tusks-monterey-county.jpg" style="object-position:50% 80%"></div>
<div class="stamp" style="right:50px;top:1110px;width:230px;height:230px;transform:rotate(8deg)">
  <div style="font:400 84px/1 Anton">2026</div><div style="font:800 24px/1.1 Poppins;letter-spacing:.06em">PRICE<br>GUIDE</div></div>
<img class="pin" src="../assets/pin.svg" style="left:50px;top:1640px;height:200px">`;

const browser = await chromium.launch();
for (const [name, w, h, body] of [["thumbnail-youtube", 1280, 720, landscape], ["thumbnail-reel", 1080, 1920, reel]]) {
  const file = path.join(OUT, `${name}.html`);
  writeFileSync(file, `<!doctype html><html><head><meta charset="utf-8"><style>:root{--w:${w}px;--h:${h}px}${css}</style></head><body>${body}</body></html>`);
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.goto("file://" + file);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(OUT, `${name}.jpg`), type: "jpeg", quality: 92 });
  await page.screenshot({ path: path.join(OUT, `${name}.png`) });
  await page.close();
}
await browser.close();
console.log("thumbnails done");
