#!/usr/bin/env python3
"""Uploads the videos in videos/ to YouTube when their publish_at time has come.

    python3 publish.py --check        validate every videos/<slug>/meta.json (no network)
    python3 publish.py                upload everything that is due and not on the channel yet
    python3 publish.py --now <slug>   upload one video right away, ignoring publish_at

Needs YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN (see authorize.py). Standard library only.
A video counts as posted when a video on the channel carries the tag "wfma-<slug>", so re-running is
always safe: nothing is uploaded twice.
"""
import datetime as dt
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = os.environ.get("YT_API_BASE", "https://www.googleapis.com")
TOKEN_URL = os.environ.get("YT_TOKEN_URL", "https://oauth2.googleapis.com/token")
CHUNK = 8 * 1024 * 1024
MIN_GAP_HOURS = float(os.environ.get("MIN_GAP_HOURS", 20))  # keeps posts about a day apart even if a run is late
REQUIRED = ("title", "description", "file", "publish_at")


def now():
    return dt.datetime.now(dt.timezone.utc)


def parse_time(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---------- videos ----------
def load_videos():
    out = []
    for meta_path in sorted(glob.glob(os.path.join(HERE, "videos", "*", "meta.json"))):
        d = os.path.dirname(meta_path)
        m = json.load(open(meta_path))
        m["slug"] = os.path.basename(d)
        m["dir"] = d
        out.append(m)
    return sorted(out, key=lambda m: m.get("publish_at", ""))


def probe(path):
    if not shutil.which("ffprobe"):
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True)
    if r.returncode:
        return None
    j = json.loads(r.stdout)
    s = j["streams"][0]
    return s["width"], s["height"], float(j["format"]["duration"])


def check(m):
    """List of problems with one video's metadata and files."""
    errs = [f"missing {k}" for k in REQUIRED if not m.get(k)]
    if errs:
        return errs
    if len(m["title"]) > 100:
        errs.append(f"title is {len(m['title'])} characters (max 100)")
    if len(m["description"].encode()) > 5000:
        errs.append("description is over 5000 bytes")
    for k in ("title", "description"):
        if "<" in m[k] or ">" in m[k]:
            errs.append(f"{k} contains < or >, which YouTube rejects")
    tags = m.get("tags", []) + [f"wfma-{m['slug']}"]
    if sum(len(t) + (2 if " " in t else 0) for t in tags) + len(tags) - 1 > 500:
        errs.append("tags are over YouTube's 500 character limit")
    if m.get("privacy", "public") not in ("public", "unlisted", "private"):
        errs.append("privacy must be public, unlisted or private")
    try:
        parse_time(m["publish_at"])
    except ValueError:
        errs.append("publish_at is not an ISO time like 2026-11-17T17:00:00Z")
    video = os.path.join(m["dir"], m["file"])
    if not os.path.exists(video):
        errs.append(f"video file {m['file']} not found")
    elif os.path.getsize(video) < 1024 * 1024:
        errs.append(f"{m['file']} is under 1 MB: is it a Git LFS pointer? Run git lfs pull")
    else:
        p = probe(video)
        if p and m.get("short"):
            w, h, dur = p
            if h <= w or dur > 180:
                errs.append(f"marked as a Short but is {w}x{h}, {dur:.0f} s (Shorts are vertical and up to 3 minutes)")
    if m.get("thumbnail"):
        thumb = os.path.join(m["dir"], m["thumbnail"])
        if not os.path.exists(thumb):
            errs.append(f"thumbnail {m['thumbnail']} not found")
        elif os.path.getsize(thumb) > 2 * 1024 * 1024:
            errs.append("thumbnail is over YouTube's 2 MB limit")
    return errs


# ---------- YouTube API ----------
def request(method, url, token=None, body=None, headers=None, raw=False, ok=(200, 201)):
    h = dict(headers or {})
    if token:
        h["Authorization"] = "Bearer " + token
    data = body
    if isinstance(body, (dict, list)):
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json; charset=UTF-8"
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, r.headers, (r.read() if raw else json.loads(r.read() or b"{}"))
    except urllib.error.HTTPError as e:
        payload = e.read()
        if e.code in ok:
            return e.code, e.headers, payload
        raise RuntimeError(f"{method} {url.split('?')[0]} failed ({e.code}): {payload[:600].decode(errors='replace')}") from None


def access_token():
    for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
        if not os.environ.get(k):
            sys.exit(f"{k} is not set. Run authorize.py once and store the values as CI/CD variables.")
    body = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                   "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    try:
        _, _, j = request("POST", TOKEN_URL, body=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    except RuntimeError as err:
        sys.exit(f"YouTube login failed: {err}\nThe refresh token may have been revoked or expired. Run authorize.py again.")
    return j["access_token"]


def posted_slugs(token):
    """Slugs already on the channel, read from the wfma-<slug> tag on every upload."""
    _, _, ch = request("GET", f"{API}/youtube/v3/channels?part=contentDetails,snippet&mine=true", token)
    if not ch.get("items"):
        sys.exit("This Google account has no YouTube channel.")
    print("Channel:", ch["items"][0]["snippet"]["title"])
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], ""
    while True:
        _, _, pl = request("GET", f"{API}/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={uploads}{page}", token)
        ids += [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
        if not pl.get("nextPageToken"):
            break
        page = "&pageToken=" + pl["nextPageToken"]
    found = {}
    for i in range(0, len(ids), 50):
        _, _, vs = request("GET", f"{API}/youtube/v3/videos?part=snippet&id={','.join(ids[i:i + 50])}", token)
        for v in vs.get("items", []):
            for t in v["snippet"].get("tags", []):
                if t.startswith("wfma-"):
                    found[t[5:]] = (v["id"], parse_time(v["snippet"].get("publishedAt", "1970-01-01T00:00:00Z")))
    return found


def upload(token, m):
    video = os.path.join(m["dir"], m["file"])
    size = os.path.getsize(video)
    status = {"privacyStatus": m.get("privacy", "public"), "selfDeclaredMadeForKids": False, "embeddable": True}
    if "contains_synthetic_media" in m:
        status["containsSyntheticMedia"] = bool(m["contains_synthetic_media"])
    meta = {"snippet": {"title": m["title"], "description": m["description"], "tags": m.get("tags", []) + [f"wfma-{m['slug']}"],
                        "categoryId": str(m.get("category_id", 22)), "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": status}
    _, hdr, _ = request("POST", f"{API}/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", token, body=meta,
                        headers={"X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    session = hdr["Location"]
    sent, tries = 0, 0
    with open(video, "rb") as f:
        while True:
            f.seek(sent)
            chunk = f.read(CHUNK)
            end = sent + len(chunk) - 1
            try:
                code, h, body = request("PUT", session, token, body=chunk, raw=True, ok=(308,),
                                        headers={"Content-Type": "video/mp4", "Content-Range": f"bytes {sent}-{end}/{size}"})
            except (RuntimeError, OSError) as err:
                tries += 1
                if tries > 6 or "failed (4" in str(err):
                    raise
                print(f"  upload interrupted ({err}); resuming in {2 ** tries} s")
                time.sleep(2 ** tries)
                code, h, body = request("PUT", session, token, body=b"", raw=True, ok=(308,), headers={"Content-Range": f"bytes */{size}"})
            if code == 308:  # incomplete: continue after the last byte YouTube confirms
                rng = h.get("Range")
                sent = int(rng.split("-")[1]) + 1 if rng else 0
                print(f"  {sent * 100 // size}%")
                continue
            vid = json.loads(body)["id"]
            print(f"  uploaded: https://youtu.be/{vid}")
            break
    if m.get("thumbnail"):
        thumb = os.path.join(m["dir"], m["thumbnail"])
        ctype = "image/png" if thumb.endswith(".png") else "image/jpeg"
        try:
            request("POST", f"{API}/upload/youtube/v3/thumbnails/set?videoId={vid}", token, body=open(thumb, "rb").read(), headers={"Content-Type": ctype})
            print("  thumbnail set")
        except RuntimeError as err:  # usually: channel not phone-verified yet. The video itself is fine.
            print(f"  thumbnail not set: {err}")
    return vid


def main():
    args = sys.argv[1:]
    videos = load_videos()
    problems = {m["slug"]: check(m) for m in videos}
    for slug, errs in problems.items():
        print(("FAIL " if errs else "ok   ") + slug + "".join(f"\n       - {e}" for e in errs))
    if any(problems.values()):
        sys.exit(1)
    if "--check" in args:
        print(f"{len(videos)} videos ready")
        return
    only = args[args.index("--now") + 1] if "--now" in args else None
    due = [m for m in videos if m["slug"] == only] if only else [m for m in videos if parse_time(m["publish_at"]) <= now()]
    if only and not due:
        sys.exit(f"no video called {only}")
    token = access_token()
    done = posted_slugs(token)
    for m in videos:
        if m["slug"] in done:
            print(f"posted  {m['slug']}: https://youtu.be/{done[m['slug']][0]}")
        elif m not in due:
            print(f"waiting {m['slug']}: posts at {m['publish_at']}")
    todo = [m for m in due if m["slug"] not in done]
    if not todo:
        return
    if not only:  # one video per run, and not within MIN_GAP_HOURS of the last post
        last = max((p for _, p in done.values()), default=None)
        if last and (now() - last).total_seconds() < MIN_GAP_HOURS * 3600:
            nxt = last + dt.timedelta(hours=MIN_GAP_HOURS)
            print(f"spacing: last post was {last:%b %d %H:%M} UTC; next one goes out after {nxt:%b %d %H:%M} UTC")
            return
        todo = todo[:1]
    for m in todo:
        print(f"posting {m['slug']}: {m['title']}")
        upload(token, m)


if __name__ == "__main__":
    main()
