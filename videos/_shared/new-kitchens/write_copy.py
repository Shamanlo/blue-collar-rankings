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


# Each city's opening, from the local paragraph on its own pricing page (rewritten in third person).
OPENING = {
    "Beverly Hills": "Beverly Hills kitchens are often large, and remodel quotes here regularly run well into six figures. So what does a kitchen remodel actually cost in Beverly Hills in 2026? This guide uses real published prices, from a condo kitchen refresh south of Wilshire to a fully custom kitchen in the Flats or Trousdale Estates.",
    "Calabasas": "Thinking about remodeling your kitchen in Calabasas? A lot of homes in The Oaks and Calabasas Hills were built in the 1980s and '90s with builder-grade kitchens, and most of them don't need to be gutted to the studs. Here's what a Calabasas kitchen remodel costs in 2026, with real published prices.",
    "Culver City": "Culver City's bungalows and post-war homes in Sunkist Park, Carlson Park and Fox Hills tend to have compact kitchens, and a smaller footprint means fewer cabinets and less countertop. Here's what a kitchen remodel costs in Culver City in 2026.",
    "Los Angeles": "Kitchen remodel quotes in Los Angeles vary as widely as the kitchens themselves, from a 1920s Spanish-style duplex in Los Feliz to a mid-century ranch in Sherman Oaks. This 2026 pricing guide puts real, published numbers on it.",
    "Malibu": "Remodeling a kitchen in Malibu means planning for salt air and humidity. From Point Dume to Big Rock, here's what a Malibu kitchen remodel costs in 2026, with cabinets, hardware and finishes made for the coast built into the price.",
    "Pacific Palisades": "Whether you're rebuilding after the January 2025 fire or updating a home in The Highlands or Huntington Palisades that came through it, you deserve a straight answer on cost before you commit. Here's what a kitchen remodel costs in Pacific Palisades in 2026.",
    "Santa Clarita": "Most homes in Valencia, Saugus, Newhall and Canyon Country were built between the 1970s and 2000s with practical, standard kitchen layouts, and keeping that layout while upgrading everything else is the fastest way to a new kitchen. Here's what a Santa Clarita kitchen remodel costs in 2026.",
    "Santa Monica": "From Ocean Park cottages and Sunset Park bungalows to larger family homes North of Montana, Santa Monica kitchens come in every size. Here's a clear 2026 starting number for every kind of kitchen remodel, before you book a single appointment.",
    "Thousand Oaks": "Many homes in Thousand Oaks and Newbury Park are 1960s to 1980s ranch and tract houses with solid bones and dated kitchens. Here's what it costs to update one in 2026, and why most Conejo Valley kitchen projects don't need a single wall moved.",
    "Westlake": "Westlake Village homes around the lake and in Three Springs often have kitchens from the 1970s and '80s, while North Ranch homes tend to be larger. Here's what a Westlake kitchen remodel costs in 2026, from a cabinet-and-counter refresh to a full custom kitchen.",
}
# Rotating wording so the ten descriptions don't read as copies of each other.
STYLE = [
    {"tiers": "2026 kitchen remodel prices in {city}:", "compare": "How {city} prices compare (other remodelers' own published prices, Oct 2026):",
     "shout": "🛠️ Need a kitchen remodel in {city}? Give {co} a shout."},
    {"tiers": "What a {city} kitchen remodel costs in 2026:", "compare": "Side by side with other {city}-area remodelers (prices from their own websites, Oct 2026):",
     "shout": "🛠️ Ready to start your {city} kitchen? Give {co} a shout for a free written quote."},
    {"tiers": "The three {city} price tiers (2026):", "compare": "{city} price comparison (published prices, Oct 2026):",
     "shout": "🛠️ Planning a kitchen remodel? Give {co} a shout."},
]


def money(s):
    return int(s.replace("$", "").replace(",", "").split()[0])


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def main():
    for n, proj in enumerate(sorted(VIDEOS.glob("new-kitchens-*-2026"))):
        spec = json.loads((proj / "script.json").read_text())
        timings = json.loads((proj / "out" / "timings.json").read_text())
        city, co, url = spec["landscape"][0]["kicker"].replace(", California", ""), spec["company"], spec["pageUrl"]
        email = spec["landscape"][-1]["address"]
        most = spec["reel"][2]["tiles"][0]["v"]
        dur = {f: mmss(sum(s["dur"] for s in timings[f])) for f in ("landscape", "reel")}
        chapters = "\n".join(f"{mmss(s['start'])} {CHAPTERS[s['id']].format(city=city, co=co)}" for s in timings["landscape"])
        compare = "\n".join(f"• {who}: {theirs} (New Kitchens: {ours}, {diff} to start)" for who, theirs, ours, diff in spec["table"]["rows"])
        tag = city.replace(" ", "")
        st = {k: v.format(city=city, co=co) for k, v in STYLE[n % len(STYLE)].items()}
        hoods = spec["landscape"][9]["where"].split(" · ", 1)[1]
        who, theirs, ours, diff = max(spec["table"]["rows"], key=lambda r: money(r[3]))
        who, scope = who.split(" · ")
        scope = scope.replace(" (", ", ").replace(")", "")
        gap = f"Biggest gap: {who} · {scope}: {theirs}, against {ours} for the matching New Kitchens tier ({diff} to start)."
        hood_tags = " ".join("#" + "".join(w[0].upper() + w[1:] for w in h.replace("'", "").split()) for h in hoods.split(", ")[:2])
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

{OPENING[city]}

In this video: the three price tiers and what each includes, how {city} prices compare with other local remodelers, permit costs, what moves your budget, and optional upgrades.

🔗 {city} kitchen remodeling pricing comparison:
{url}

{st['tiers']}
• Entry-level remodel: $25,000 – $35,000 (keep your layout; refaced or stock cabinets; laminate or quartz counters; new lighting, backsplash, paint & flooring)
• Mid-range remodel (most popular): $40,000 – $70,000 (semi-custom cabinets; quartz, granite or butcher block; updated layout; plumbing or electrical relocations)
• High-end remodel: $75,000 – $120,000+ (layout redesign; custom cabinetry; full-slab quartz or granite; commercial-grade appliances; custom island)

{st['compare']}
{compare}
{gap}

Typical permit costs (2026): $500 – $1,500
• Minor remodel, no layout changes: $400 – $700
• Wall removal, electrical or plumbing upgrades: $800 – $1,200
• Major structural changes or additions: $1,200 – $1,500+

What moves your price: layout changes, cabinets, countertops, and appliances. Two kitchens the same size can come in $30,000 apart.

Optional upgrades that add cost: panel-ready appliances, radiant heated floors, skylights or bigger windows, pot fillers and beverage stations, smart lighting, and walk-in pantries or custom storage.

{st['shout']}
Serving {city}, including {hoods}.
Prices published up front · free in-home assessment & written, line-item quote · one team for design, permits, demo & install · licensed & insured
🌐 {url}
✉️ {email}
🕗 Mon–Sat, 8 AM – 6 PM

Chapters:
{chapters}

Prices are 2026 ranges from the {co} pricing page and are ballpark only. Comparison prices are as published on each company's own website. Get a written quote for your kitchen.

Local Vibe Check: price guides, places and trusted local businesses. Subscribe for more local price guides.

#{tag} {hood_tags} #KitchenRemodel #KitchenRemodeling #HomeRenovation #KitchenDesign #RemodelCost

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

Voice: Microsoft neural TTS (en-US-AndrewNeural) via edge-tts.

- `youtube.md`: titles, description, chapters, tags and the reel caption
- `out/{name}.mp4`: main video, 1920x1080, {dur['landscape']}
- `out/{name}-reel.mp4`: Reel/Short, 1080x1920, {dur['reel']}
- `out/thumbnail-youtube.jpg` (1280x720), `out/thumbnail-reel.jpg` (1080x1920)

Rebuild with the shared engine: see `../README.md`, or `bash _shared/new-kitchens/render_all.sh` for all cities.
""")
        print(name, dur)


if __name__ == "__main__":
    main()
