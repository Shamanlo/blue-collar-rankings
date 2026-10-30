// Send visitors on the *.pages.dev address or www. to the same page on windowfilmmarketingagency.com.
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
  return next();
}
