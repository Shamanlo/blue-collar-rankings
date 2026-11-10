#!/usr/bin/env python3
"""Writes channel/videos/<slug>/meta.json for the explainer videos, one post per day.

    python3 video/queue_explainers.py <build root> <first date YYYY-MM-DD> [--copy <out dir>] [--thumbs <dir>]

Each explainer becomes two posts: the 16:9 video (with chapters from <root>/<slug>/chapters.json)
and its Short the next day. --copy puts <out>/<slug>-wide.mp4 / -reel.mp4 in place as video.mp4, and
--thumbs copies <dir>/<slug>.png as the long video's thumbnail.
"""
import datetime as dt
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from explainers import VIDEOS  # noqa: E402

ROOT = os.path.abspath(sys.argv[1])
day = dt.date.fromisoformat(sys.argv[2])
opt = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
CHANNEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "channel", "videos")
POST_TIME = "17:00:00Z"  # 11am Central
FOOT = """
Free marketing audit: https://windowfilmmarketingagency.com
Email: info@windowfilmmarketingagency.com

Window Film Marketing Agency: local SEO, AI search, web design, video editing and social media, built only for window film companies. Proud to be based in the USA & serving USA companies."""
NOTES = {
    "google-maps-top-3": "Business names in the map examples are illustrations.",
    "ai-search": "AI answers shown are illustrations, not real results.",
}
USES_MD = {"hire-an-agency", "google-maps-top-3", "ai-search", "website-breakdown"}

def youtube_chapters(slug, v):
    """Chapters from the long video's plan: consecutive scenes grouped until each chapter is at least
    10 s (YouTube's minimum), named after the first named scene in the group. Needs 3 or more."""
    plan = json.load(open(os.path.join(ROOT, slug, "plan-wide.json")))
    scenes = [s for s in v["scenes"] if s.get("vo")]
    marks = [(seg["t0"], "Intro" if sc["kind"] == "hook" else "Free audit" if sc["kind"] == "outro" else sc.get("chapter"))
             for seg, sc in zip(plan["segments"], scenes)]
    end = plan["duration"]
    groups = []
    for t, name in marks:
        if groups and (t - groups[-1][0] < 10 or not name):
            if groups[-1][1] == "Intro" and name:
                groups[-1][1] = name  # an intro group takes the first real topic's name
            continue
        groups.append([t, name or "Intro"])
    if len(groups) > 1 and end - groups[-1][0] < 10:
        groups.pop()
    if len(groups) < 3:
        return []
    return [(f"{int(t // 60)}:{int(t % 60):02d}", name) for t, name in groups]


for slug, v in VIDEOS.items():
    yt = v["youtube"]
    chapters = youtube_chapters(slug, v)
    credit = "\nScreens and photos: MD Window Films, a Los Angeles window film installer whose website we built: https://www.mdwindowfilms.com" if slug in USES_MD else ""
    note = f"\n{NOTES[slug]}" if slug in NOTES else ""
    long_desc = yt["intro"] + "\n\n" + ("\n".join(f"{t} {name}" for t, name in chapters) + "\n" if chapters else "") + credit + note + "\n" + FOOT + "\n\n#windowfilm #windowtinting #contractormarketing"
    short_desc = yt["intro"].split(". ")[0].rstrip(".") + "." + credit + note + "\n" + FOOT + "\n\n#windowfilm #windowtinting #shorts"
    posts = [(slug, {"title": yt["title"], "description": long_desc, "tags": yt["tags"], "short": False, "thumbnail": "thumbnail.png"}, "wide"),
             (slug + "-short", {"title": yt["short_title"], "description": short_desc, "tags": yt["tags"][:6], "short": True}, "reel")]
    for name, meta, fmt in posts:
        d = os.path.join(CHANNEL, f"2026-11-{name}")
        os.makedirs(d, exist_ok=True)
        meta.update({"file": "video.mp4", "privacy": "public", "category_id": 27, "publish_at": f"{day.isoformat()}T{POST_TIME}"})
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=2, ensure_ascii=False)
        if opt("--copy"):
            shutil.copy(os.path.join(opt("--copy"), f"{slug}-{fmt}.mp4"), os.path.join(d, "video.mp4"))
        if opt("--thumbs") and fmt == "wide":
            shutil.copy(os.path.join(opt("--thumbs"), f"{slug}.png"), os.path.join(d, "thumbnail.png"))
        print(f"{day}  2026-11-{name}: {meta['title']}")
        day += dt.timedelta(days=1)
