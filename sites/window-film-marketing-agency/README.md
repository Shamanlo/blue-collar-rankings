# windowfilmmarketingagency.com

Static site for Window Film Marketing Agency: marketing, AI search (AEO) and web design for window film companies.
Layout follows iowaaeo.com (hero, interactive "who gets recommended" demo, services, process, who-we-serve grid,
comparison table, FAQ, lead form). Service vocabulary follows real window film installers (security and safety film,
anti-graffiti film, solar film, frosted privacy glass, skylight tinting, home window tinting).

## Pages

- `/` home
- `/services/` + 6 marketing pages (AI search, local SEO, Google Business Profile, video editing, social media management, reviews)
- `/web-design/` + 6 web design pages (custom sites, redesign, service-area pages, galleries, estimate forms, hosting)
- `/specialties/` + 7 film specialty pages (residential, commercial, security, anti-graffiti, decorative, solar/skylight, auto/PPF)
- `/about/`, `/contact/`, `/privacy/`, `404.html`, `sitemap.xml`, `robots.txt`, `llms.txt`

## Edit content

All copy is in `scripts/content.mjs`. Styles: `static/css/site.css`. Behavior: `static/js/site.js`.

**Lead form:** set `site.web3formsKey` in `scripts/content.mjs` to a free key from https://web3forms.com
(sign up with the inbox that should receive leads). Until then the form opens the visitor's email app
addressed to `site.email`.

## Homepage reel

`video/` holds the 38-second 9:16 reel shown on the homepage. It is code, not a timeline file:

- `video/reel.html` is the animation. Every frame is `window.render(t)`; edit copy, timing and layout there
  and preview by opening it in a browser and calling `render(12.5)` in the console.
- `video/render.mjs` renders it with Playwright and ffmpeg (`--stills dir 1,5,9` for test frames,
  `--cues cues.json` for the sound cue list, or `out.mp4` for the full silent video).
- `video/audio.py cues.json outdir/` synthesizes the music and sound effects on those cues (numpy + scipy).

```sh
node video/render.mjs --cues /tmp/cues.json
node video/render.mjs /tmp/reel-video.mp4 --workers 3
python3 video/audio.py /tmp/cues.json /tmp/audio
ffmpeg -i /tmp/reel-video.mp4 -i /tmp/audio/mix.wav -map 0:v -map 1:a -c:v libx264 -crf 19 -c:a aac -b:a 192k -t 38 -movflags +faststart reel.mp4
```

The site serves a 720p copy at `static/video/reel.mp4` with `static/video/reel-poster.jpg`.

## Build

```sh
npm run build    # writes public/
npm run images   # re-renders favicons and og.png into static/img/ (needs Playwright + Chromium)
npm run serve    # preview public/ locally
```

## Deploy

Every push to `main` runs `.github/workflows/deploy.yml`, which builds the site and deploys `public/` to the
`window-film-marketing-agency` Cloudflare Pages project. It needs a `CLOUDFLARE_API_TOKEN` repository secret
with Pages:Edit, Zone:Read and DNS:Edit (plus Zone:Edit if you want the workflow to add the domain to Cloudflare
for you; the log then prints the nameservers to set at Namecheap). Once the zone is active, the same workflow
attaches windowfilmmarketingagency.com and www, and points DNS at Pages. `functions/_middleware.js` redirects
www and *.pages.dev to the apex domain.
