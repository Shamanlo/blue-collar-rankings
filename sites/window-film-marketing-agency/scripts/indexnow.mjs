// Tells Bing (and other IndexNow engines, which feed ChatGPT search and Copilot) about every page
// in public/sitemap.xml. Run after a deploy: node scripts/indexnow.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { site } from "./content.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const key = fs.readdirSync(path.join(ROOT, "static")).find((f) => /^[0-9a-f]{32}\.txt$/.test(f))?.slice(0, 32);
if (!key) throw new Error("No IndexNow key file (static/<32 hex>.txt)");
const urlList = [...fs.readFileSync(path.join(ROOT, "public/sitemap.xml"), "utf8").matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
const res = await fetch("https://api.indexnow.org/indexnow", {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=utf-8" },
  body: JSON.stringify({ host: site.domain, key, keyLocation: `${site.url}/${key}.txt`, urlList }),
});
console.log(`IndexNow: ${res.status} ${res.statusText} for ${urlList.length} URLs`);
if (res.status >= 400) process.exitCode = 1;
