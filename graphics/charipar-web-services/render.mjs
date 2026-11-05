// Renders each <section class="slide"> in a slides.html to a PNG next to it.
// Usage: node graphics/charipar-web-services/render.mjs graphics/charipar-web-services/furnace-repair-near-me
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = require("/opt/node22/lib/node_modules/playwright")); }

const dir = path.resolve(process.argv[2] || ".");
const names = { s1: "01-hook", s2: "02-top-3", s3: "03-the-math", s4: "04-lifetime-value", s5: "05-the-fix", s6: "06-offer", single: "single-post-square" };

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 1 });
await page.goto("file://" + path.join(dir, "slides.html"));
await page.evaluate(() => document.fonts.ready);
for (const el of await page.$$("section.slide")) {
  const id = await el.getAttribute("id");
  const out = path.join(dir, `${names[id] || id}.png`);
  await el.screenshot({ path: out });
  console.log("wrote", out);
}
await browser.close();
