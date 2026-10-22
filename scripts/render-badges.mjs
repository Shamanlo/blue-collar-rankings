// Renders every badge SVG to a 2x PNG in static/badges/ (run after build.mjs, then build again).
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = require("/opt/node22/lib/node_modules/playwright")); }

const jobs = JSON.parse(fs.readFileSync(path.join(ROOT, "scripts/.badge-jobs.json"), "utf8"));
const font = "file://" + path.join(ROOT, "static/fonts/oswald-latin.woff2");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 240, height: 240 }, deviceScaleFactor: 2 });
for (const job of jobs) {
  const out = path.join(ROOT, "static", job.out);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  await page.setContent(`<style>@font-face{font-family:Oswald;font-weight:500 700;src:url(${font})}html,body{margin:0;background:transparent}svg{width:240px;height:240px}</style>${job.svg}`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: 240, height: 240 } });
}
await browser.close();
console.log(`Rendered ${jobs.length} badges`);
