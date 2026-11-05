const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1000, height: 1000 }, deviceScaleFactor: 3 });
  await p.goto("file://" + __dirname + "/podcast-cover.html"); await p.waitForTimeout(500);
  await p.screenshot({ path: __dirname + "/local-vibe-check-podcast-cover.png" });
  await b.close();
})();
