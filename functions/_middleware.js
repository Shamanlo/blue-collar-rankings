// Send visitors on the *.pages.dev address or www. to the same page on bluecollarrankings.com.
const CANONICAL = "bluecollarrankings.com";

export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  if (url.hostname.endsWith(".pages.dev") || url.hostname === "www." + CANONICAL) {
    url.hostname = CANONICAL;
    url.protocol = "https:";
    url.port = "";
    return Response.redirect(url.toString(), 301);
  }
  return next();
}
