// Render reel.html frame by frame and mux with the voiceover + music bed.
// Usage:
//   node render_reel.mjs <audio_dir> <out.mp4>              full video (30 fps)
//   node render_reel.mjs <audio_dir> --stills 1.2,5,9 <dir>  PNG stills at the given times (for checking)
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = require("/opt/node22/lib/node_modules/playwright")); }

const [audioDir, a2, a3, a4] = process.argv.slice(2);
const tl = JSON.parse(fs.readFileSync(path.join(here, "timeline.json"), "utf8"));
const reviewsPath = path.join(here, "reviews.json");
const reviews = fs.existsSync(reviewsPath) ? JSON.parse(fs.readFileSync(reviewsPath, "utf8")) : [];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto("file://" + path.join(here, "reel.html"));
await page.evaluate(() => document.fonts.ready);
await page.evaluate(([t, r]) => window.init(t, r), [tl, reviews]);

if (a2 === "--stills") {
  fs.mkdirSync(a4, { recursive: true });
  for (const s of a3.split(",")) {
    await page.evaluate(t => window.setTime(t), Number(s));
    await page.screenshot({ path: path.join(a4, `t${s}.png`) });
  }
  await browser.close();
  process.exit(0);
}

const FPS = 30, N = Math.ceil(tl.duration * FPS);
const out = a2;
const ff = spawn("ffmpeg", ["-y", "-hide_banner", "-loglevel", "error",
  "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
  "-i", path.join(audioDir, "voice.wav"), "-i", path.join(audioDir, "music.wav"),
  "-filter_complex",
  // voice: light compression + loudness; music: quiet under voice, a bit louder in the outro
  `[1:a]aresample=48000,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,volume=1.0,apad[v];` +
  `[2:a]volume='if(lt(t,${tl.voiceEnd}),0.07,0.16)':eval=frame[m];` +
  `[v][m]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,atrim=0:${tl.duration}[a]`,
  "-map", "0:v", "-map", "[a]",
  "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
  "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", out], { stdio: ["pipe", "inherit", "inherit"] });

for (let i = 0; i < N; i++) {
  await page.evaluate(t => window.setTime(t), i / FPS);
  const buf = await page.screenshot({ type: "jpeg", quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  if (i % 150 === 0) console.log(`frame ${i}/${N}`);
}
ff.stdin.end();
await new Promise(r => ff.on("close", r));
await browser.close();
console.log("wrote", out);
