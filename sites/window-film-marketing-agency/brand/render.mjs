// Renders the brand pages in this folder to PNGs: every element with data-out="<file>.png".
//   node brand/render.mjs outdir
// youtube.html: profile picture (800x800) and banner (2560x1440, plus a safe-area guide copy).
// thumbnails.html: 1280x720 YouTube thumbnails.
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUT = path.resolve(process.argv[2] || "brand-out");
fs.mkdirSync(OUT, { recursive: true });
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = require("/opt/node22/lib/node_modules/playwright")); }

const TYPES = { ".html": "text/html", ".woff2": "font/woff2" };
const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!file.startsWith(ROOT) || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 2560, height: 2400 } });
for (const name of ["youtube.html", "thumbnails.html"]) {
  await page.goto(`http://127.0.0.1:${server.address().port}/brand/${name}`);
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.fonts].map((f) => f.load())); });
  for (const el of await page.$$("[data-out]")) {
    const file = await el.getAttribute("data-out");
    await el.screenshot({ path: path.join(OUT, file) });
    console.log("wrote", file);
  }
  if (await page.$("#guide")) {
    await page.evaluate(() => { document.getElementById("guide").style.display = "block"; });
    await (await page.$("#banner")).screenshot({ path: path.join(OUT, "banner-with-safe-areas.png") });
  }
}
await browser.close();
server.close();
