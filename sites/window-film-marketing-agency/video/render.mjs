// Renders reel.html to video with Playwright + ffmpeg.
//   node video/render.mjs out.mp4 [--workers 3] [--fps 30]   full render (silent video)
//   node video/render.mjs --stills dir 0.5,3,9.2              PNG stills at given times
//   node video/render.mjs --cues cues.json                    sound cue list for audio.py
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const DIR = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = require("/opt/node22/lib/node_modules/playwright")); }

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const FPS = +opt("--fps", 30);
const WORKERS = +opt("--workers", 3);

const TYPES = { ".html": "text/html", ".woff2": "font/woff2", ".js": "text/javascript" };
const server = http.createServer((req, res) => {
  const file = path.join(DIR, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!file.startsWith(DIR) || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const URL_ = `http://127.0.0.1:${server.address().port}/reel.html`;

const browser = await chromium.launch();
async function openPage() {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => { console.error("page error:", e.message); process.exitCode = 1; });
  await page.goto(URL_, { waitUntil: "load" });
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.fonts].map((f) => f.load())); });
  return page;
}

try {
  if (args.includes("--cues")) {
    const page = await openPage();
    const cues = await page.evaluate(() => window.CUES);
    fs.writeFileSync(opt("--cues"), JSON.stringify(cues, null, 1));
    console.log(`Wrote ${cues.length} cues`);
  } else if (args.includes("--stills")) {
    const dir = opt("--stills"); fs.mkdirSync(dir, { recursive: true });
    const times = args[args.indexOf("--stills") + 2].split(",").map(Number);
    const page = await openPage();
    for (const t of times) {
      await page.evaluate((t) => window.render(t), t);
      await page.screenshot({ path: path.join(dir, `t${t.toFixed(2).padStart(5, "0")}.png`) });
    }
    console.log(`Wrote ${times.length} stills to ${dir}`);
  } else {
    const out = path.resolve(args[0]);
    const duration = await (await openPage()).evaluate(() => window.DURATION);
    const total = Math.round(duration * FPS);
    const per = Math.ceil(total / WORKERS);
    const tmp = fs.mkdtempSync(path.join(path.dirname(out), ".segs-"));
    const started = Date.now();
    let done = 0;
    await Promise.all(Array.from({ length: WORKERS }, async (_, w) => {
      const from = w * per, to = Math.min(total, from + per);
      if (from >= to) return;
      const page = await openPage();
      const seg = path.join(tmp, `seg${w}.mp4`);
      const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
        "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "15",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", String(FPS), seg], { stdio: ["pipe", "inherit", "inherit"] });
      const closed = new Promise((r, j) => ff.on("close", (c) => (c === 0 ? r() : j(new Error("ffmpeg exited " + c)))));
      for (let f = from; f < to; f++) {
        await page.evaluate((t) => window.render(t), f / FPS);
        const buf = await page.screenshot({ type: "jpeg", quality: 96 });
        if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
        if (++done % 60 === 0) console.log(`${done}/${total} frames (${((Date.now() - started) / 1000).toFixed(0)}s)`);
      }
      ff.stdin.end();
      await closed;
    }));
    const list = path.join(tmp, "list.txt");
    fs.writeFileSync(list, Array.from({ length: WORKERS }, (_, w) => `file 'seg${w}.mp4'`).filter((_, w) => w * per < total).join("\n"));
    await new Promise((r, j) => spawn("ffmpeg", ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", list, "-c", "copy", "-movflags", "+faststart", out], { stdio: "inherit" }).on("close", (c) => (c === 0 ? r() : j(new Error("concat failed")))));
    fs.rmSync(tmp, { recursive: true, force: true });
    console.log(`Rendered ${total} frames to ${out} in ${((Date.now() - started) / 1000).toFixed(0)}s`);
  }
} finally {
  await browser.close();
  server.close();
}
