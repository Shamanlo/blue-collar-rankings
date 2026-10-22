// SVG award seals. Two kinds:
//   top  - "#1 Top Ranked" seal for the top-rated business in a ranking
//   area - "Best in <Area>" seal for every business that made a ranking
// Both are drawn on a 240x240 canvas and use the Oswald font when available.

const NAVY = "#012456";
const NAVY_DARK = "#00163a";
const ORANGE = "#fc5800";
const FONT = "Oswald, 'Arial Narrow', Impact, sans-serif";

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// Rough Oswald uppercase advance width (em) used to keep long labels inside the seal.
const fit = (text, base, maxWidth, em = 0.5) => Math.min(base, maxWidth / (String(text).length * em));

const arcs = (id, r) => `
    <path id="${id}-top" d="M ${120 - r} 120 A ${r} ${r} 0 0 1 ${120 + r} 120" fill="none"/>
    <path id="${id}-bot" d="M ${120 - r} 120 A ${r} ${r} 0 0 0 ${120 + r} 120" fill="none"/>`;

const stars = (cx, cy, color) => {
  const star = (x, y, s) => {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const rr = i % 2 ? s * 0.45 : s;
      const a = (Math.PI / 5) * i - Math.PI / 2;
      pts.push(`${(x + rr * Math.cos(a)).toFixed(1)},${(y + rr * Math.sin(a)).toFixed(1)}`);
    }
    return `<polygon points="${pts.join(" ")}" fill="${color}"/>`;
  };
  return star(cx - 98, cy, 5) + star(cx + 98, cy, 5);
};

const bars = (x, y, scale, c1, c2) => {
  const hs = [10, 14, 18, 22, 26];
  return hs
    .map((h, i) => `<rect x="${x + i * 7 * scale}" y="${y - h * scale}" width="${5 * scale}" height="${h * scale}" fill="${i === 2 || i === 4 ? c2 : c1}"/>`)
    .join("");
};

export function topBadge({ id = "tb", area, trade, year, title }) {
  const areaU = area.toUpperCase();
  const tradeU = trade.toUpperCase();
  const areaSize = fit(areaU, 15, 112, 0.56);
  const tradeSize = fit(tradeU, 12.5, 200, 0.5);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" role="img" aria-label="${esc(title)}" class="badge-svg">
  <title>${esc(title)}</title>
  <defs>${arcs(id, 93)}
    <radialGradient id="${id}-g" cx="50%" cy="38%" r="70%"><stop offset="0" stop-color="#0d3c80"/><stop offset="1" stop-color="${NAVY_DARK}"/></radialGradient>
  </defs>
  <circle cx="120" cy="120" r="119" fill="${ORANGE}"/>
  <circle cx="120" cy="120" r="111" fill="${NAVY}"/>
  <circle cx="120" cy="120" r="80" fill="url(#${id}-g)" stroke="${ORANGE}" stroke-width="3"/>
  <circle cx="120" cy="120" r="74" fill="none" stroke="#ffffff" stroke-opacity=".25" stroke-width="1" stroke-dasharray="2 4"/>
  <g font-family="${FONT}" font-weight="600" fill="#ffffff" letter-spacing="2.4">
    <text font-size="15.5"><textPath href="#${id}-top" startOffset="50%" text-anchor="middle">BLUE COLLAR RANKINGS</textPath></text>
    <text font-size="${tradeSize.toFixed(1)}" letter-spacing="1.6"><textPath href="#${id}-bot" startOffset="50%" text-anchor="middle" dominant-baseline="hanging">${esc(tradeU)}</textPath></text>
  </g>
  ${stars(120, 120, ORANGE)}
  <g transform="translate(103 76)">${bars(0, 0, 0.75, "#ffffff", ORANGE)}</g>
  <text x="120" y="133" text-anchor="middle" font-family="${FONT}" font-weight="700" font-size="58" fill="${ORANGE}">#1</text>
  <text x="120" y="151" text-anchor="middle" font-family="${FONT}" font-weight="600" font-size="13.5" letter-spacing="2.4" fill="#ffffff">TOP RANKED · ${esc(year)}</text>
  <path d="M 56 158 L 184 158 L 177 170 L 184 182 L 56 182 L 63 170 Z" fill="${ORANGE}"/>
  <text x="120" y="175.5" text-anchor="middle" font-family="${FONT}" font-weight="600" font-size="${areaSize.toFixed(1)}" letter-spacing="1.2" fill="#ffffff">${esc(areaU)}</text>
</svg>`;
}

export function areaBadge({ id = "ab", area, trade, year, title }) {
  const areaU = area.toUpperCase();
  const tradeU = trade.toUpperCase();
  const areaSize = fit(areaU, 30, 124, 0.5);
  const tradeSize = fit(tradeU, 12.5, 200, 0.5);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" role="img" aria-label="${esc(title)}" class="badge-svg">
  <title>${esc(title)}</title>
  <defs>${arcs(id, 93)}</defs>
  <circle cx="120" cy="120" r="119" fill="${NAVY}"/>
  <circle cx="120" cy="120" r="111" fill="${NAVY}" stroke="${ORANGE}" stroke-width="2"/>
  <circle cx="120" cy="120" r="80" fill="#ffffff" stroke="${ORANGE}" stroke-width="3"/>
  <circle cx="120" cy="120" r="73" fill="none" stroke="${NAVY}" stroke-opacity=".18" stroke-width="1" stroke-dasharray="2 4"/>
  <g font-family="${FONT}" font-weight="600" fill="#ffffff" letter-spacing="2.4">
    <text font-size="15.5"><textPath href="#${id}-top" startOffset="50%" text-anchor="middle">BLUE COLLAR RANKINGS</textPath></text>
    <text font-size="${tradeSize.toFixed(1)}" letter-spacing="1.6"><textPath href="#${id}-bot" startOffset="50%" text-anchor="middle" dominant-baseline="hanging">${esc(tradeU)}</textPath></text>
  </g>
  ${stars(120, 120, ORANGE)}
  <g transform="translate(103 78)">${bars(0, 0, 0.75, NAVY, ORANGE)}</g>
  <text x="120" y="102" text-anchor="middle" font-family="${FONT}" font-weight="600" font-size="15" letter-spacing="4" fill="${ORANGE}" dy="0">BEST IN</text>
  <text x="120" y="${(118 + areaSize * 0.42).toFixed(1)}" text-anchor="middle" font-family="${FONT}" font-weight="700" font-size="${areaSize.toFixed(1)}" fill="${NAVY}">${esc(areaU)}</text>
  <path d="M 64 156 L 176 156 L 170 167 L 176 178 L 64 178 L 70 167 Z" fill="${NAVY}"/>
  <text x="120" y="172.5" text-anchor="middle" font-family="${FONT}" font-weight="600" font-size="12.5" letter-spacing="2" fill="#ffffff">RANKED ${esc(year)}</text>
</svg>`;
}
