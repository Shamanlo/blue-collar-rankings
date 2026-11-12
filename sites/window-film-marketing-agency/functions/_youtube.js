// Latest uploads from the agency's YouTube channel, for pages with a [data-yt-feed] placeholder.
// _middleware.js fills those placeholders on every request from the channel's public RSS feed,
// cached at the edge for 15 minutes, so new Shorts and videos show up without a redeploy.

export const CHANNEL_ID = "UC0kmCxaiRMF3jaOBiEQQ_Aw"; // youtube.com/@WindowFilmMarketingAgency
const FEED = (id) => `https://www.youtube.com/feeds/videos.xml?channel_id=${id}`;
const CACHE_SECONDS = 900;

const decode = (s) => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'");
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const tag = (xml, name) => { const m = xml.match(new RegExp(`<${name}[^>]*>([\\s\\S]*?)</${name}>`)); return m ? decode(m[1].trim()) : ""; };
const attr = (xml, name, a) => { const m = xml.match(new RegExp(`<${name}[^>]*\\s${a}="([^"]*)"`)); return m ? decode(m[1]) : ""; };

/** Parses YouTube's channel feed into [{id, title, description, published, short, url, thumb, views}]. */
export function parseFeed(xml) {
  return [...xml.matchAll(/<entry>([\s\S]*?)<\/entry>/g)].map(([, e]) => {
    const id = tag(e, "yt:videoId");
    const url = attr(e, 'link rel="alternate"', "href") || `https://www.youtube.com/watch?v=${id}`;
    return {
      id,
      title: tag(e, "title"),
      description: tag(e, "media:description"),
      published: tag(e, "published"),
      short: url.includes("/shorts/"),
      url,
      thumb: attr(e, "media:thumbnail", "url") || `https://i.ytimg.com/vi/${id}/hqdefault.jpg`,
      views: Number(attr(e, "media:statistics", "views")) || 0,
    };
  }).filter((v) => /^[\w-]{11}$/.test(v.id));
}

export async function getVideos(channelId = CHANNEL_ID) {
  try {
    const r = await fetch(FEED(channelId), { cf: { cacheTtl: CACHE_SECONDS, cacheEverything: true } });
    return r.ok ? parseFeed(await r.text()) : [];
  } catch {
    return [];
  }
}

// Titles often end in hashtags (#windowfilm #shorts): keep them on YouTube, not on the site.
const cleanTitle = (t) => t.replace(/(\s+#[\w-]+)+\s*$/g, "").trim() || t;
const PLAY = '<svg width="34" height="34" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z" fill="currentColor"/></svg>';

function card(v) {
  const title = cleanTitle(v.title);
  const date = v.published ? new Date(v.published).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" }) : "";
  const poster = v.short ? `https://i.ytimg.com/vi/${v.id}/oar2.jpg` : `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`;
  const box = v.short ? "phone" : "ytw";
  return `<article class="yt-item${v.short ? " is-short" : ""}">
  <div class="${box}" data-yt="${v.id}" data-title="${esc(title)}">
    <img src="${poster}" onerror="this.onerror=null;this.src='${esc(v.thumb)}'" alt="${esc(title)}" loading="lazy" width="${v.short ? 540 : 480}" height="${v.short ? 960 : 360}">
    <button class="reel-play" type="button" aria-label="Play: ${esc(title)}">${PLAY}</button>
    <span class="reel-sound">${v.short ? "YouTube Short" : "YouTube"}</span>
  </div>
  <h3><a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(title)}</a></h3>
  <p class="yt-meta">${esc(date)}${v.views ? ` · ${v.views.toLocaleString("en-US")} views` : ""}</p>
</article>`;
}

/** HTML for a placeholder: mode "home" shows the newest few, "all" shows every upload in the feed. */
export function renderFeed(videos, { mode = "all", channelUrl = "https://www.youtube.com/@WindowFilmMarketingAgency" } = {}) {
  if (!videos.length) return null;
  const list = mode === "home" ? videos.slice(0, 4) : videos;
  const shorts = list.filter((v) => v.short), longs = list.filter((v) => !v.short);
  const ld = {
    "@context": "https://schema.org", "@type": "ItemList",
    itemListElement: list.map((v, i) => ({
      "@type": "ListItem", position: i + 1,
      item: { "@type": "VideoObject", name: cleanTitle(v.title), description: (v.description || cleanTitle(v.title)).slice(0, 500),
              thumbnailUrl: `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`, uploadDate: v.published,
              embedUrl: `https://www.youtube.com/embed/${v.id}`, url: v.url },
    })),
  };
  return (longs.length ? `<div class="yt-grid yt-long">${longs.map(card).join("")}</div>` : "") +
    (shorts.length ? `<div class="yt-grid yt-shorts">${shorts.map(card).join("")}</div>` : "") +
    `<p class="yt-more"><a class="btn btn-ghost" href="${channelUrl}" target="_blank" rel="noopener">See every video on YouTube</a></p>` +
    `<script type="application/ld+json">${JSON.stringify(ld).replace(/</g, "\\u003c")}</script>`;
}
