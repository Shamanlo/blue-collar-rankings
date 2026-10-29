// Renders favicons and the social share image into static/img/ with Playwright.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = require("/opt/node22/lib/node_modules/playwright")); }

const mark = fs.readFileSync(path.join(ROOT, "static/favicon.svg"), "utf8");
const out = path.join(ROOT, "static/img");
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch();

for (const [name, size] of [["favicon-32.png", 32], ["apple-touch-icon.png", 180], ["icon-512.png", 512]]) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  await page.setContent(`<style>html,body{margin:0;background:transparent}svg{width:${size}px;height:${size}px;display:block}</style>${mark}`);
  await page.screenshot({ path: path.join(out, name), omitBackground: true });
  await page.close();
}

const og = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await og.setContent(`<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=DM+Mono:wght@500&display=swap" rel="stylesheet">
<style>html,body{margin:0}body{width:1200px;height:630px;background:#0C1B2A;color:#fff;font-family:"Bricolage Grotesque",sans-serif;display:flex;flex-direction:column;justify-content:center;padding:0 80px;box-sizing:border-box;position:relative;overflow:hidden}
.m{display:flex;align-items:center;gap:18px;font:500 22px "DM Mono",monospace;letter-spacing:.14em;text-transform:uppercase;color:#8FD3E8}.m svg{width:64px;height:64px}
h1{font-size:84px;line-height:1;letter-spacing:-.035em;margin:36px 0 0;max-width:900px}h1 span{background:#FFB21E;color:#0B1622;padding:0 .12em;border-radius:6px}
p{font:500 24px "DM Mono",monospace;color:#A9B8C6;margin-top:36px;letter-spacing:.04em}
.g{position:absolute;right:-60px;top:60px;display:grid;grid-template-columns:1fr 1fr;gap:14px;transform:rotate(-8deg);opacity:.25}.g i{width:150px;height:150px;border-radius:18px;background:linear-gradient(160deg,#BFE7F4,#3E7690)}</style>
<div class="g"><i></i><i></i><i></i><i></i></div>
<div class="m">${mark}windowfilmmarketingagency.com</div>
<h1>Marketing &amp; web design for <span>window film</span> companies</h1>
<p>Local SEO · AI search · Websites · Google Ads</p>`);
await og.evaluate(() => document.fonts.ready);
await og.screenshot({ path: path.join(out, "og.png") });
await browser.close();
console.log("Rendered favicons and og.png");
