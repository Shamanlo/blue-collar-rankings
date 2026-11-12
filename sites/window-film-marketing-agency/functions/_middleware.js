// Send visitors on the *.pages.dev address or www. to the same page on windowfilmmarketingagency.com,
// and fill [data-yt-feed] placeholders with the latest YouTube uploads (see _youtube.js).
import { getVideos, renderFeed } from "./_youtube.js";

const CANONICAL = "windowfilmmarketingagency.com";

export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  if (url.hostname.endsWith(".pages.dev") || url.hostname === "www." + CANONICAL) {
    url.hostname = CANONICAL;
    url.protocol = "https:";
    url.port = "";
    return Response.redirect(url.toString(), 301);
  }
  // The agency does not offer Google Ads; send the retired page to the services list.
  if (url.pathname.startsWith("/services/google-ads")) {
    return Response.redirect(new URL("/services/", url).toString(), 301);
  }
  const res = await next();
  if (request.method !== "GET" || !(res.headers.get("content-type") || "").includes("text/html")) return res;
  let videos = null;
  return new HTMLRewriter()
    .on("[data-yt-feed]", {
      async element(el) {
        videos ??= await getVideos();
        const html = renderFeed(videos, { mode: el.getAttribute("data-yt-feed") });
        if (html) el.setInnerContent(html, { html: true });  // otherwise the static fallback stays
      },
    })
    .transform(res);
}
