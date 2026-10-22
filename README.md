# bluecollarrankings.com

Static site for Blue Collar Rankings: one page per YouTube ranking video, with the embedded video,
a write-up of every business that ranked, and two badges:

- **#1 Top Ranked**: the top-rated pick in each ranking
- **Best in {Area}**: every business that made a ranking

## Edit content

- `data/rankings.json`: one entry per video (title, city, intro copy, #1 pick and why, contenders, tips, chapters)
- `data/businesses.json`: one entry per business (website, Google Business Profile, address, phone, write-up).
  Use `summaries.{ranking-slug}` when a business appears in more than one ranking with different copy.

## Build

```sh
npm run build    # writes public/
npm run badges   # also re-renders badge PNGs into static/badges/ (needs Playwright + Chromium)
npm run serve    # preview public/ locally
```

Run `npm run badges` after adding a ranking so its PNG badges exist. `public/` is what gets deployed.

## Deploy

Every push to `main` runs `.github/workflows/deploy.yml`, which builds the site and deploys `public/`
to the `blue-collar-rankings` Cloudflare Pages project (https://blue-collar-rankings.pages.dev).
It needs a `CLOUDFLARE_API_TOKEN` repository secret with Pages:Edit (plus Zone:Read and DNS:Edit
to connect the domain). Once bluecollarrankings.com is added to Cloudflare, the same workflow
attaches it and points DNS at Pages.

## Add a new video

1. Add an entry to `data/rankings.json` (copy an existing one; `videoId` is the YouTube ID).
2. Add any new businesses to `data/businesses.json`.
3. Save the video thumbnail as `static/img/thumbs/{videoId}.jpg`.
4. `npm run badges`, commit, push.
