// Renders brand/youtube.html to YouTube channel art: avatar (800x800) and banner (2560x1440).
//   node brand/render.mjs outdir
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

const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!file.startsWith(ROOT) || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": file.endsWith(".html") ? "text/html" : file.endsWith(".woff2") ? "font/woff2" : "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 2560, height: 2400 } });
await page.goto(`http://127.0.0.1:${server.address().port}/brand/youtube.html`);
await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.fonts].map((f) => f.load())); });
await (await page.$("#avatar")).screenshot({ path: path.join(OUT, "youtube-profile-800.png") });
await (await page.$("#banner")).screenshot({ path: path.join(OUT, "youtube-banner-2560x1440.png") });
await page.evaluate(() => { document.getElementById("guide").style.display = "block"; });
await (await page.$("#banner")).screenshot({ path: path.join(OUT, "banner-with-safe-areas.png") });
await browser.close();
server.close();
console.log("Wrote channel art to " + OUT);
