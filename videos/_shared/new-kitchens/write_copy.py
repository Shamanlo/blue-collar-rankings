"""Write youtube.md and README.md for every New Kitchens city video (run after tts.py).

    python3 videos/_shared/new-kitchens/write_copy.py
"""
import json
from pathlib import Path

VIDEOS = Path(__file__).resolve().parent.parent.parent
CHAPTERS = {
    "hook": "What does a kitchen remodel cost in {city}?",
    "ranges": "2026 price tiers",
    "entry": "Entry-level remodel",
    "mid": "Mid-range remodel",
    "high": "High-end remodel",
    "compare": "How {city} prices compare",
    "permits": "Permit costs",
    "drivers": "What moves your price",
    "upgrades": "Upgrades that add cost",
    "shout": "Need a kitchen remodel? Give {co} a shout",
    "gallery": "Kitchens from their gallery",
    "cta": "Get a free written quote",
}


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def main():
    for proj in sorted(VIDEOS.glob("new-kitchens-*-2026")):
        spec = json.loads((proj / "script.json").read_text())
        timings = json.loads((proj / "out" / "timings.json").read_text())
        city, co, url = spec["landscape"][0]["kicker"].replace(", California", ""), spec["company"], spec["pageUrl"]
        email = spec["landscape"][-1]["address"]
        most = spec["reel"][2]["tiles"][0]["v"]
        dur = {f: mmss(sum(s["dur"] for s in timings[f])) for f in ("landscape", "reel")}
        chapters = "\n".join(f"{mmss(s['start'])} {CHAPTERS[s['id']].format(city=city, co=co)}" for s in timings["landscape"])
        compare = "\n".join(f"• {who}: {theirs} (New Kitchens: {ours}, {diff} to start)" for who, theirs, ours, diff in spec["table"]["rows"])
        tag = city.replace(" ", "")
        name = proj.name
        md = f"""# Local Vibe Check: Kitchen Remodeling Pricing Guide, {city} (2026)

## Main video (16:9)

File: `out/{name}.mp4` ({dur['landscape']})
Thumbnail: `out/thumbnail-youtube.jpg` (1280x720)

### Title

{city} Kitchen Remodel Cost (2026): Pricing Guide & Price Comparison

Shorter alternatives:
- How Much Does a Kitchen Remodel Cost in {city}? (2026)
- {city} Kitchen Remodeling Prices 2026: Entry-Level vs. Mid-Range vs. High-End

### Description

How much does a kitchen remodel cost in {city}, California in 2026? Most remodelers won't give you a number until they've been in your house for an hour. This pricing guide uses real published prices: the three price tiers, what each one includes, how they compare with other local remodelers, permit costs, and the choices that move your budget.

🔗 {city} kitchen remodeling pricing comparison:
{url}

2026 kitchen remodel prices in {city}:
• Entry-level remodel: $25,000 – $35,000 (keep your layout; refaced or stock cabinets; laminate or quartz counters; new lighting, backsplash, paint & flooring)
• Mid-range remodel (most popular): $40,000 – $70,000 (semi-custom cabinets; quartz, granite or butcher block; updated layout; plumbing or electrical relocations)
• High-end remodel: $75,000 – $120,000+ (layout redesign; custom cabinetry; full-slab quartz or granite; commercial-grade appliances; custom island)

How {city} prices compare (prices other remodelers publish on their own websites, Oct 2026):
{compare}
Up to {most} less to start.

Typical permit costs (2026): $500 – $1,500
• Minor remodel, no layout changes: $400 – $700
• Wall removal, electrical or plumbing upgrades: $800 – $1,200
• Major structural changes or additions: $1,200 – $1,500+

What moves your price: layout changes, cabinets, countertops, and appliances. Two kitchens the same size can come in $30,000 apart.

Optional upgrades that add cost: panel-ready appliances, radiant heated floors, skylights or bigger windows, pot fillers and beverage stations, smart lighting, and walk-in pantries or custom storage.

🛠️ Need a kitchen remodel in {city}? Give {co} a shout.
Prices published up front · free in-home assessment & written, line-item quote · one team for design, permits, demo & install · licensed & insured
🌐 {url}
✉️ {email}
🕗 Mon–Sat, 8 AM – 6 PM

Chapters:
{chapters}

Prices are 2026 ranges from {co}'s pricing page and are ballpark only. Comparison prices are as published on each company's own website. Get a written quote for your kitchen.

Local Vibe Check: price guides, places and trusted local businesses. Subscribe for more local price guides.

#{tag} #KitchenRemodel #KitchenRemodeling #HomeRenovation #LosAngelesHomes #KitchenDesign #RemodelCost

### Tags

{city.lower()} kitchen remodel, kitchen remodel cost {city.lower()}, {city.lower()} kitchen remodeling prices 2026, how much does a kitchen remodel cost, kitchen remodeling pricing guide, kitchen remodel price comparison, mid-range kitchen remodel cost, kitchen remodel permit cost, {city.lower()} kitchen remodeler, new kitchens of {city.lower()}

## Reel / YouTube Short (9:16)

File: `out/{name}-reel.mp4` ({dur['reel']})
Cover: `out/thumbnail-reel.jpg` (1080x1920)

### Title

What a Kitchen Remodel Costs in {city} (2026) 🍳 #shorts

### Caption

What does a kitchen remodel cost in {city} in 2026?
🔹 Entry-level: $25K – $35K
🔸 Mid-range (most popular): $40K – $70K
💎 High-end: $75K – $120K+
💰 Up to {most} less to start than other local remodelers' published prices

🛠️ Need a kitchen remodel? Give {co} a shout
🔗 {url}

#shorts #{tag} #KitchenRemodel #HomeRenovation #KitchenDesign
"""
        (proj / "youtube.md").write_text(md)
        (proj / "README.md").write_text(f"""# Kitchen Remodeling Pricing Guide, {city} (2026): Local Vibe Check

Pricing-guide video, Short/Reel and thumbnails for the Local Vibe Check YouTube channel, built from
{url}
(prices, tiers, comparison table and permit costs). Ends with "give {co} a shout" and the page URL.

Generated by `../_shared/new-kitchens/build_scripts.py` (script.json) and `write_copy.py` (this file
and youtube.md); photos are the site's gallery images in `../_shared/new-kitchens/`. The site lists no
real phone number, so the video points to the website and {email}.

Voice: Google Gemini TTS (`gemini-3.8-flash-tts`, voice Charon), prices read spelled out.

- `youtube.md`: titles, description, chapters, tags and the reel caption
- `out/{name}.mp4`: main video, 1920x1080, {dur['landscape']}
- `out/{name}-reel.mp4`: Reel/Short, 1080x1920, {dur['reel']}
- `out/thumbnail-youtube.jpg` (1280x720), `out/thumbnail-reel.jpg` (1080x1920)

Rebuild with the shared engine: see `../README.md`, or `bash _shared/new-kitchens/render_all.sh` for all cities.
""")
        print(name, dur)


if __name__ == "__main__":
    main()
