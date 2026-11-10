# Window Film Marketing Agency: YouTube publishing

This folder is the root of a GitLab project. Each video lives in `videos/<slug>/`:

```
videos/2026-11-5-videos/
  meta.json        title, description, tags, publish_at, privacy, short, thumbnail
  video.mp4        stored with Git LFS
  thumbnail.png    optional, 1280x720, under 2 MB (not used by Shorts)
```

Pushing to the default branch, or the hourly pipeline schedule, runs `publish.py`. It uploads every video
whose `publish_at` time has passed and that isn't on the channel yet. Videos are matched by a hidden
`wfma-<slug>` tag, so nothing is ever uploaded twice. To post a video, add its folder and push.

## meta.json

| field | |
|---|---|
| `title` | up to 100 characters, no `<` or `>` |
| `description` | up to 5000 bytes. Chapters: lines like `0:00 Intro`, starting at 0:00, at least 3, each 10 s or longer |
| `tags` | list of strings |
| `publish_at` | UTC time, e.g. `2026-11-17T17:00:00Z` (11am Central) |
| `privacy` | `public` (default), `unlisted` or `private` |
| `short` | `true` for vertical videos up to 3 minutes; YouTube posts them as Shorts |
| `thumbnail` | file name in the folder; needs a phone-verified channel |
| `category_id` | YouTube category, default 22 (People & Blogs); 27 is Education |

`python3 publish.py --check` validates everything without uploading. `python3 publish.py --now <slug>` posts one video immediately.

## One-time setup

1. **GitLab**: create the project, push this folder (`git lfs install` first), then add a pipeline
   schedule under Build > Pipeline schedules: every hour, `0 * * * *`.
2. **Google Cloud**: create a project, enable **YouTube Data API v3**, configure the OAuth consent screen
   (External; add the channel's Google account as a test user), and create an OAuth client of type
   **Desktop app**.
3. **Authorize the channel**:
   ```sh
   YT_CLIENT_ID=... YT_CLIENT_SECRET=... python3 authorize.py
   # open the link, choose the channel, click Allow, copy the address of the page it lands on
   YT_CLIENT_ID=... YT_CLIENT_SECRET=... GITLAB_TOKEN=... GITLAB_PROJECT=group/project python3 authorize.py '<address>'
   ```
   This saves `YT_CLIENT_ID`, `YT_CLIENT_SECRET` and `YT_REFRESH_TOKEN` as masked CI/CD variables.
   Google will warn that the app isn't verified: it's your own app, so click **Advanced → Go to (app name)**.
4. **Channel**: verify it by phone at youtube.com/verify so custom thumbnails work.

## Limits

- **Private until audited.** YouTube makes every upload from an unaudited API project private. Until the
  project passes YouTube's API compliance audit (free; apply in the Google Cloud console under YouTube
  Data API v3 > Quotas, or via the YouTube API Services audit form), flip each video to Public in YouTube
  Studio after it posts. Set `privacy` to `public` either way; it applies once the audit is approved.
- **Testing mode expires logins.** While the OAuth consent screen is in "Testing", refresh tokens expire
  after 7 days. Publish the consent screen to "In production" so the login lasts.
- **Quota.** Each upload costs about 1,700 of the default 10,000 daily quota units: about 5 uploads a day.
