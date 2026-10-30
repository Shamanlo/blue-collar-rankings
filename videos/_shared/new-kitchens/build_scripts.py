"""Build one video project per "New Kitchens of {City}" kitchen remodeling pricing page.

    python3 videos/_shared/new-kitchens/build_scripts.py

Fetches each pricing-comparison page, pulls the city, company, neighborhoods, price tiers,
permit costs and the published-price comparison table, and writes
videos/new-kitchens-{city}-2026/script.json (plus .gitignore). Prices are read by the voice
spelled out ("speak"), while captions show the figures ("say").
"""
import html
import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEOS = HERE.parent.parent
URLS = [
    "https://kitchenremodelingbeverlyhills.com/beverly-hills-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelingcalabasas.com/calabasas-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelingculvercity.com/culver-city-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelinglosangeles.org/los-angeles-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelingmalibu.com/malibu-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelingpacificpalisades.com/pacific-palisades-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelingsantaclarita.org/santa-clarita-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelingsantamonica.com/santa-monica-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelingthousandoaks.com/thousand-oaks-kitchen-remodeling-pricing-comparison",
    "https://kitchenremodelingwestlake.com/westlake-kitchen-remodeling-pricing-comparison",
]

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def w99(n):
    return ONES[n] if n < 20 else TENS[n // 10] + ("" if n % 10 == 0 else "-" + ONES[n % 10])


def w999(n):
    h, r = divmod(n, 100)
    return " ".join(([ONES[h] + " hundred"] if h else []) + ([w99(r)] if r else []))


def words(n):
    if 1000 <= n < 10000 and n % 100 == 0 and n % 1000:
        return w99(n // 100) + " hundred"
    t, r = divmod(n, 1000)
    return " ".join(([w999(t) + " thousand"] if t else []) + ([w999(r)] if r else []))


def spell(text):
    """$45,000 -> forty-five thousand dollars, for the voice."""
    return re.sub(r"\$(\d{1,3}(?:,\d{3})*)", lambda m: words(int(m.group(1).replace(",", ""))) + " dollars", text)


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment)).strip()


def parse(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8")
    city = re.search(r"<title>(.+?) Kitchen Remodeling Pricing Comparison", raw).group(1).strip()
    company = f"New Kitchens of {city}"
    assert company in raw, company
    serving = re.search(r"Proudly serving " + re.escape(city) + r" &amp; (.+?)\.\s*<", raw) or re.search(r"Proudly serving " + re.escape(city) + r" & (.+?)\.\s*<", raw)
    hoods = html.unescape(serving.group(1)).strip()
    most = re.search(r"by as much as \$([\d,]+)", raw).group(1)
    email = re.search(r"info@[\w.-]+", raw).group(0)
    table = re.search(r'<table class="compare-table">.*?<tbody>(.*?)</tbody>', raw, re.S).group(1)
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", table, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        who = text_of(re.search(r"<b>(.*?)</b>", tds[0], re.S).group(1))
        scope = text_of(re.search(r"<small>(.*?)</small>", tds[0], re.S).group(1))
        theirs = text_of(re.sub(r"<small>.*?</small>", "", tds[1], flags=re.S))
        ours = text_of(tds[2])
        diff = text_of(re.search(r'<span class="save">(.*?)</span>', tds[3], re.S).group(1))
        rows.append([f"{who} · {scope}", theirs, ours, diff])
    tiers = re.findall(r"\$(\d{2},\d{3})–\$(\d{2,3},\d{3})(\+?)", raw)
    assert ("25,000", "35,000", "") in tiers and ("40,000", "70,000", "") in tiers and ("75,000", "120,000", "+") in tiers, city
    assert "Permit fees typically run $500–$1,500" in html.unescape(re.sub(r"</?b>", "", raw)), city
    return {"city": city, "company": company, "hoods": hoods, "most": most, "email": email,
            "url": url, "domain": url.split("/")[2], "rows": rows}


def scenes(c):
    city, co, most = c["city"], c["company"], c["most"]
    page = c["url"].replace("https://", "")
    domain, path_ = page.split("/", 1)
    hoods = c["hoods"].replace(" & ", ", ")
    landscape = [
        {"id": "hook", "kind": "title", "label": "2026 Price Guide",
         "image": "kitchen-01.jpg", "imgPos": "45% 50%",
         "kicker": f"{city}, California", "titlePx": 128,
         "title": ["Kitchen Remodel", "Pricing Guide"], "year": "2026",
         "chips": ["Entry-level", "Mid-range", "High-end", "Permits", "Upgrades"],
         "say": f"How much does a kitchen remodel cost in {city} in 2026? Most remodelers won't give you a number until they've been in your house for an hour. Here's the pricing guide, with real published prices."},
        {"id": "ranges", "kind": "ranges", "label": "2026 Price Tiers",
         "title": f"What a {city} kitchen remodel costs", "sub": "2026 ranges · most projects land in one of three",
         "max": 125, "ticks": [0, 40, 80, 120],
         "rows": [
             {"name": "Entry-level", "note": "Quick refresh", "lo": 25, "hi": 35, "cue": "entry-level"},
             {"name": "Mid-range", "note": "Most popular", "lo": 40, "hi": 70, "cue": "mid-range"},
             {"name": "High-end", "note": "Custom, chef-grade", "lo": 75, "hi": 120, "plus": True, "cue": "high-end"}],
         "say": f"Most {city} kitchen projects land in one of three ranges. An entry-level remodel starts at about $25,000 to $35,000. A mid-range remodel, the most popular, typically runs $40,000 to $70,000. And a high-end remodel runs $75,000 to $120,000 and up."},
        {"id": "entry", "kind": "price", "label": "Tier 1 of 3",
         "image": "kitchen-11.jpg", "kicker": "Tier 1 of 3", "name": "Entry-level remodel",
         "lo": 25, "hi": 35, "priceCue": "$25,000",
         "desc": "Quick refreshes, rentals & first-time buyers.",
         "bullets": [{"t": "Keep the existing layout & appliances", "cue": "keep"}, {"t": "Cabinet refacing or new stock cabinets", "cue": "refacing"},
                     {"t": "Laminate or quartz countertops", "cue": "laminate"}, {"t": "New lighting, backsplash, paint & flooring", "cue": "lighting"}],
         "say": "An entry-level remodel, at $25,000 to $35,000, is for quick refreshes, rentals, and first-time buyers. You keep the existing layout and appliances, with cabinet refacing or new stock cabinets, laminate or quartz countertops, and new lighting, backsplash, paint, and flooring."},
        {"id": "mid", "kind": "price", "label": "Tier 2 of 3",
         "image": "kitchen-08.jpg", "kicker": "Tier 2 of 3 · Most popular", "name": "Mid-range remodel",
         "lo": 40, "hi": 70, "priceCue": "$40,000",
         "desc": f"The full upgrade most {city} families choose.",
         "bullets": [{"t": "New semi-custom cabinets", "cue": "semi-custom"}, {"t": "Quartz, granite or butcher block counters", "cue": "quartz"},
                     {"t": "Updated layout, sink, faucet & tile backsplash", "cue": "updated"}, {"t": "Plumbing or electrical relocations", "cue": "plumbing"}],
         "say": f"A mid-range remodel, $40,000 to $70,000, is the full upgrade most {city} families choose: new semi-custom cabinets, quartz, granite, or butcher block counters, an updated layout with a new sink, faucet, and tile backsplash, and plumbing or electrical relocations."},
        {"id": "high", "kind": "price", "label": "Tier 3 of 3",
         "image": "kitchen-03.jpg", "kicker": "Tier 3 of 3", "name": "High-end remodel",
         "lo": 75, "hi": 120, "plus": True, "priceCue": "$75,000",
         "desc": "Custom, chef-grade kitchens.",
         "bullets": [{"t": "Layout redesign & wall reconfiguration", "cue": "layout"}, {"t": "Custom cabinetry with built-in organizers", "cue": "custom"},
                     {"t": "Full-slab quartz or granite", "cue": "full-slab"}, {"t": "Commercial-grade appliances & custom island", "cue": "commercial-grade"}],
         "say": "A high-end remodel, $75,000 to $120,000 and up, is a custom, chef-grade kitchen: a layout redesign and wall reconfiguration, custom cabinetry with built-in organizers, full-slab quartz or granite, commercial-grade appliances, and a custom island or built-in seating."},
        {"id": "compare", "kind": "table", "label": "Price Comparison",
         "title": f"How {city} prices compare",
         "callout": f"Up to <b>${most} less</b> to start", "calloutCue": f"${most}",
         "say": f"How do those prices compare? {co} lined up the prices other {city}-area remodelers publish on their own websites for the same scope of work. Their starting price came in lower every time, by as much as ${most}."},
        {"id": "permits", "kind": "stats", "label": "Permit Costs", "source": True,
         "title": "Typical permit costs (2026)", "tvPx": 80,
         "tiles": [{"v": "$400–$700", "n": "Minor remodel", "s": "No layout changes", "cue": "minor"},
                   {"v": "$800–$1,200", "n": "Walls, plumbing, electrical", "s": "Wall removal or system upgrades", "cue": "removing"},
                   {"v": "$1,200–$1,500+", "n": "Major remodel", "s": "Structural changes or additions", "cue": "major"}],
         "note": "Set by the city and based on your project's valuation. Shown as its own line on your quote.", "noteCue": "set",
         "say": "Budget for permits too. They typically run $500 to $1,500. A minor remodel with no layout changes, about $400 to $700. Removing walls or upgrading plumbing or electrical, about $800 to $1,200. And major structural changes, $1,200 to $1,500 and up. The fee is set by the city, based on your project's value."},
        {"id": "drivers", "kind": "factors", "label": "What Drives the Price", "cols": 4,
         "title": "What moves your price",
         "cards": [{"name": "Layout changes", "desc": "Keeping the sink, range & fridge in place saves the most", "image": "kitchen-04.jpg", "cue": "layout"},
                   {"name": "Cabinets", "desc": "Refacing or stock vs. semi-custom or custom", "image": "kitchen-09.jpg", "cue": "cabinets"},
                   {"name": "Countertops", "desc": "Laminate & quartz vs. full slab or waterfall", "image": "kitchen-02.jpg", "cue": "countertops"},
                   {"name": "Appliances", "desc": "Reusing saves thousands; commercial ranges need venting", "image": "kitchen-10.jpg", "imgPos": "60% 50%", "cue": "appliances"}],
         "say": "Two kitchens the same size can come in $30,000 apart. What makes the difference? Layout changes: keeping your sink, range, and fridge where they are is the single biggest way to save. Then cabinets, countertops, and appliances, where reusing what you have saves thousands."},
        {"id": "upgrades", "kind": "list", "label": "Optional Upgrades",
         "title": "Upgrades that add cost",
         "items": ["Panel-ready or built-in appliances", "Radiant heated floors", "Skylights or enlarged windows", "Pot fillers, second sinks & beverage stations", "Smart & under-cabinet lighting", "Walk-in pantries & custom storage"],
         "note": "None are required for a beautiful kitchen. Price them separately and decide.",
         "say": "Optional upgrades add to the total: panel-ready appliances, radiant heated floors, skylights or bigger windows, pot fillers and beverage stations, smart lighting, and walk-in pantries or custom storage. None of them are required for a beautiful kitchen."},
        {"id": "shout", "kind": "winner", "label": "Need a Kitchen Remodel?",
         "image": "kitchen-05.jpg",
         "stamp": "Give them a shout", "name": co, "nameCue": "New",
         "where": f"Serving {city} · {hoods}",
         "logo": "new-kitchens-icon.png", "logoBg": "#1c1c1c",
         "points": ["Prices published up front", "Free in-home assessment & written quote", "Line-item quotes: cabinets, counters, labor & permits", "One team for design, permits, demo & install", "Licensed & insured"],
         "say": f"Need a kitchen remodel in {city}? Give {co} a shout. They publish their prices up front, give you a free in-home assessment and a written, line-item quote, and one team handles design, permits, demolition, and installation."},
        {"id": "gallery", "kind": "steps", "label": "Kitchen Gallery", "plain": True, "hold": 1.5,
         "title": "Kitchens from their gallery", "sub": co,
         "steps": [{"image": f"kitchen-{i:02d}.jpg"} for i in (1, 6, 9, 3, 8, 5, 11, 2, 12, 7)],
         "say": "Here are a few kitchens from their gallery."},
        {"id": "cta", "kind": "cta", "label": "Free Written Quote",
         "image": "kitchen-07.jpg",
         "logo": "new-kitchens-icon.png",
         "name": co, "phone": "Free written quote", "phoneCue": "free",
         "address": c["email"], "hours": "Mon–Sat · 8 AM – 6 PM · Licensed & insured",
         "url": f"{domain}/\n{path_}", "urlCue": "link",
         "tip": "Get your quote, then compare it line by line.",
         "say": f"Need a kitchen remodel? Give {co} a shout for a free written quote, at the link in the description. This has been Local Vibe Check."},
    ]
    reel = [
        {"id": "r-hook", "kind": "title", "label": "2026 Price Guide",
         "image": "kitchen-01.jpg", "imgPos": "45% 50%",
         "kicker": f"{city}, CA", "title": ["Kitchen", "Prices"], "year": "2026",
         "chips": ["Entry", "Mid-range", "High-end"],
         "say": f"What does a kitchen remodel cost in {city} in 2026?"},
        {"id": "r-ranges", "kind": "ranges", "label": "2026 Price Tiers",
         "title": "Kitchen remodel prices", "sub": f"{city} · 2026", "max": 125, "ticks": [0, 60, 120],
         "rows": [
             {"name": "Entry-level", "note": "Quick refresh", "lo": 25, "hi": 35, "cue": "entry-level"},
             {"name": "Mid-range", "note": "Most popular", "lo": 40, "hi": 70, "cue": "mid-range"},
             {"name": "High-end", "note": "Custom", "lo": 75, "hi": 120, "plus": True, "cue": "high-end"}],
         "say": "Entry-level: $25,000 to $35,000. Mid-range, the most popular: $40,000 to $70,000. High-end: $75,000 to $120,000 and up."},
        {"id": "r-compare", "kind": "stats", "label": "Price Comparison",
         "title": "Vs. other local remodelers",
         "tiles": [{"v": f"${most}", "n": "less to start", "s": f"vs. prices other {city} remodelers publish", "cue": f"${most}"}],
         "say": f"{co} compared their prices with what other local remodelers publish, and came in lower every time, by as much as ${most}."},
        {"id": "r-shout", "kind": "winner", "label": "Need a Kitchen Remodel?",
         "image": "kitchen-05.jpg",
         "stamp": "Give them a shout", "name": co, "nameCue": "New",
         "where": f"Serving {city}",
         "logo": "new-kitchens-icon.png", "logoBg": "#1c1c1c",
         "points": ["Prices published up front", "Free written quote", "Licensed & insured"],
         "say": f"Need a kitchen remodel? Give {co} a shout."},
        {"id": "r-cta", "kind": "cta", "label": "Free Written Quote",
         "image": "kitchen-07.jpg", "logo": "new-kitchens-icon.png",
         "name": co, "phone": "Free quote", "phoneCue": "free",
         "address": c["email"], "hours": "Mon–Sat · 8 AM – 6 PM",
         "url": "Link in description", "urlCue": "link",
         "tip": "Follow Local Vibe Check for more local price guides.",
         "say": "Get a free written quote at the link in the description. Follow for more."},
    ]
    for s in landscape + reel:
        if re.search(r"\$\d", s["say"]):
            s["speak"] = spell(s["say"])
    return landscape, reel


# A different photo, headline word, price tag and badge for each city's thumbnails.
THUMB = {
    "Beverly Hills": ("kitchen-03.jpg", "50% 50%", "Prices", "$25K – $120K+", "save"),
    "Calabasas": ("kitchen-06.jpg", "45% 50%", "Remodel", "From $25K", "tiers"),
    "Culver City": ("kitchen-11.jpg", "40% 50%", "Costs", "$25K – $120K+", "save"),
    "Los Angeles": ("kitchen-09.jpg", "30% 50%", "Prices", "From $25K", "guide"),
    "Malibu": ("kitchen-05.jpg", "50% 50%", "Remodel", "$25K – $120K+", "save"),
    "Pacific Palisades": ("kitchen-07.jpg", "50% 50%", "Costs", "From $25K", "save"),
    "Santa Clarita": ("kitchen-10.jpg", "45% 50%", "Prices", "From $25K", "tiers"),
    "Santa Monica": ("kitchen-08.jpg", "40% 50%", "Remodel", "$25K – $120K+", "save"),
    "Thousand Oaks": ("kitchen-04.jpg", "50% 50%", "Costs", "$25K – $120K+", "tiers"),
    "Westlake": ("kitchen-12.jpg", "40% 50%", "Prices", "From $25K", "guide"),
}


def thumbs(c):
    image, pos, word, tag, badge = THUMB[c["city"]]
    k = f"${int(c['most'].replace(',', '')) // 1000}K"
    stamp = {"save": [k, ["LESS TO", "START"]], "tiers": ["3", ["PRICE", "TIERS"]], "guide": ["2026", ["PRICE", "GUIDE"]]}[badge]
    long_ = len(c["city"]) >= 14
    return {"image": image, "landscapePos": pos, "reelPos": pos,
            "lines": ["Kitchen", word], "sub": f"{c['city']}, CA", "tag": tag, "year": "2026",
            "subPx": 54 if long_ else 66, "reelSubPx": 70 if long_ else 86,
            "stamp": stamp, "reelStamp": stamp if badge != "tiers" else ["2026", ["PRICE", "GUIDE"]]}


def main():
    for url in URLS:
        c = parse(url)
        slug = c["city"].lower().replace(" ", "-")
        proj = VIDEOS / f"new-kitchens-{slug}-2026"
        (proj / "out").mkdir(parents=True, exist_ok=True)
        landscape, reel = scenes(c)
        spec = {
            # Microsoft neural voice: Gemini's free tier caps TTS at 100 requests a day.
            "voice": "en-US-AndrewNeural", "rate": "+6%",
            "assetsDir": "../_shared/new-kitchens",
            "header": f"{c['city']}, CA · Kitchen Remodel Prices · 2026",
            "source": f"Prices from {c['domain']}, Oct 2026. Comparison prices as published on each company's own website. Ballpark only.",
            "sourceKinds": ["ranges", "price", "table"],
            "company": c["company"], "pageUrl": c["url"],
            "table": {"corner": "Published by", "highlight": 1,
                      "cols": ["Their published price", "New Kitchens", "Difference"], "rows": c["rows"]},
            "thumbs": thumbs(c),
            "landscape": landscape, "reel": reel,
        }
        (proj / "script.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
        (proj / ".gitignore").write_text("# Keep only the deliverables and timings from out/\nout/*\n!out/timings.json\n"
                                         f"!out/{proj.name}.mp4\n!out/{proj.name}-reel.mp4\n!out/thumbnail-youtube.jpg\n!out/thumbnail-reel.jpg\n")
        print(f"{proj.name}: {len(c['rows'])} comparison rows, up to ${c['most']} less, serving {c['hoods']}")


if __name__ == "__main__":
    main()
