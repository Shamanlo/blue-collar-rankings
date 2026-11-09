"""Writes youtube.md and README.md for each ADU Builder Pros video (run after tts.py, for chapter times).

    python3 videos/_shared/adu-builders/write_copy.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_scripts import CITIES, VIDEOS, TYPE, build, money  # noqa: E402

TITLES = [
    "{city} ADU Cost (2026): Pricing Guide for Every Type of ADU",
    "How Much Does an ADU Cost in {city}? (2026 Pricing Guide)",
    "{city} ADU Prices 2026: Junior ADU vs. Garage Conversion vs. Detached",
]
ALTS = [
    ["How Much Does It Cost to Build an ADU in {city}? (2026)", "{city} ADU Builder Pricing Guide (2026)"],
    ["{city} ADU Cost 2026: What Each Type of ADU Really Costs", "ADU Prices in {city}, CA (2026): Garage Conversions to Backyard Homes"],
    ["What an ADU Costs in {city} (2026)", "{city} ADU Pricing Guide 2026: Costs, Rules & Builders"],
]
REEL_TITLES = [
    "What an ADU Costs in {city} (2026) 🏡 #shorts",
    "{city} ADU Prices in 60 Seconds (2026) 🏠 #shorts",
    "How Much Is an ADU in {city}? (2026) 🔨 #shorts",
]
REEL_OPEN = [
    "Thinking about an ADU in {city}? 2026 prices 👇",
    "What does an ADU cost in {city}? Here's the 2026 breakdown 👇",
    "Backyard home, garage conversion or junior ADU? {city} prices for 2026 👇",
]
TAGS = {
    "santaclarita": "valencia adu, saugus adu, canyon country adu, stevenson ranch adu, scv adu",
    "thousandoaks": "newbury park adu, dos vientos adu, conejo valley adu, ventura county adu",
    "calabasas": "hidden hills adu, calabasas highlands, mont calabasas, las virgenes adu",
    "westlakevillage": "north ranch adu, lake sherwood adu, conejo valley adu, westlake adu",
    "beverlyhills": "beverly hills guest house, 90210 adu, trousdale estates, beverly crest adu",
    "malibu": "malibu coastal adu, point dume adu, malibu fire rebuild adu, topanga adu",
    "santamonica": "ocean park adu, sunset park adu, north of montana adu, westside adu",
    "pacificpalisades": "palisades fire rebuild adu, palisades highlands adu, lawndale adu, westside adu",
    "culvercity": "culver city pre-approved adu, carlson park adu, blair hills adu, westside adu",
    "agourahills": "old agoura adu, oak park adu, las virgenes adu, conejo valley adu",
}
HASH = {
    "santaclarita": "#SantaClarita #Valencia #Saugus #SCV",
    "thousandoaks": "#ThousandOaks #NewburyPark #ConejoValley",
    "calabasas": "#Calabasas #HiddenHills #LasVirgenes",
    "westlakevillage": "#WestlakeVillage #NorthRanch #ConejoValley",
    "beverlyhills": "#BeverlyHills #90210 #GuestHouse",
    "malibu": "#Malibu #PointDume #MalibuRebuild",
    "santamonica": "#SantaMonica #OceanPark #Westside",
    "pacificpalisades": "#PacificPalisades #PalisadesRebuild #Westside",
    "culvercity": "#CulverCity #Westside #LosAngeles",
    "agourahills": "#AgouraHills #OldAgoura #ConejoValley",
}


def ts(sec):
    s = int(sec)
    return f"{s // 60}:{s % 60:02d}"


def k(v):
    return money(v)


def main():
    for i, c in enumerate(CITIES):
        slug, spec, pr = build(c, i)
        d = VIDEOS / slug
        city = c["city"]
        co = f"{city} ADU Builder Pros"
        domain = f"adubuilders{c['key']}.pro"
        url = f"https://{domain}/"
        tm = json.loads((d / "out" / "timings.json").read_text())
        land = {s["id"]: s for s in tm["landscape"]}
        dur = sum(s["dur"] for s in tm["landscape"])
        rdur = sum(s["dur"] for s in tm["reel"])
        by_id = {s["id"]: s for s in spec["landscape"]}
        chap_label = {
            "hook": f"What does an ADU cost in {city}?",
            "ranges": "2026 ADU price ranges",
            "drivers": f"What drives ADU cost in {city}",
            "rules": f"{city} ADU rules to know",
            "faq": "Common questions, answered",
            "pick": f"Need an ADU builder? {co}",
            "work": "Inside a finished ADU",
            "cta": "Get a free consultation",
        }
        for n in (1, 2, 3):
            s = by_id[f"f{n}"]
            chap_label[f"f{n}"] = f"{s['label']}: {s['name']}"
        chapters = "\n".join(f"{ts(s['start'])} {chap_label[s['id']]}" for s in tm["landscape"])
        feats = "\n".join(
            f"• {f[1]}: {f[2]} ({k(pr[f[0]][0])} – {k(pr[f[0]][1])}+). {f[5]}" for f in c["feats"])
        price_lines = "\n".join(
            f"• {TYPE[t][0]} ({TYPE[t][1].lower()}): {k(pr[t][0])} – {k(pr[t][1])}+" for t in ("jadu", "garage", "attached", "detached"))
        drivers = ", ".join(f"{d_[0].lower()} ({d_[1][0].lower() + d_[1][1:]})" for d_ in c["drivers"])
        faq = "\n".join(f"• {q} {a}." for q, a, _ in c["faq"])
        rules = by_id["rules"]["say"].replace("A few rules to know. ", "")
        title = TITLES[i % 3].format(city=city)
        alts = "\n".join(f"- {a.format(city=city)}" for a in ALTS[i % 3])
        hood_str = ", ".join(c["hoods"][:3])
        md = f"""# Local Vibe Check: ADU Pricing Guide, {city} (2026)

## Main video (16:9)

File: `out/{slug}.mp4` ({ts(dur)})
Thumbnail: `out/thumbnail-youtube.jpg` (1280x720)

### Title

{title}

Shorter alternatives:
{alts}

### Description

How much does it cost to build an ADU in {city}, California in 2026? This pricing guide covers every type of accessory dwelling unit, from a junior ADU inside the house to a brand-new detached backyard home, with real examples from {hood_str}, what drives the price, the local rules, and the questions homeowners ask most.

🔗 {city} ADU builder:
{url}

2026 ADU prices in {city} (design, permits & construction):
{price_lines}

ADU examples around {city}:
{feats}

What drives ADU cost in {city}: {drivers}.

Rules to know: {rules}

Common questions:
{faq}

🔨 Need an ADU builder or contractor in {city}? Give {co} a shout.
Site review & design · permits & plan check · foundations, utilities & construction · garage conversions to brand-new backyard homes · reply within 24 hours
Serving {c['areas']}
🌐 Free consultation: {url}

Chapters:
{chapters}

Prices are estimated 2026 ballpark ranges: a Westside design/build ADU baseline (All Exclusive Construction's Santa Monica ADU guide) adjusted for {city} conditions. {co} doesn't publish prices; your cost depends on your lot, the ADU type, size and finishes. Get an on-site estimate.

Local Vibe Check: price guides, places and trusted local businesses. Subscribe for more local price guides.

{HASH[c['key']]} #ADU #AccessoryDwellingUnit #BackyardHome #GarageConversion

### Tags

{city.lower()} adu, adu builder {city.lower()}, adu cost {city.lower()}, how much does an adu cost, adu prices 2026, garage conversion cost, junior adu cost, detached adu cost, accessory dwelling unit {city.lower()}, adu contractor {city.lower()}, {TAGS[c['key']]}, {co.lower()}

## Reel / YouTube Short (9:16)

File: `out/{slug}-reel.mp4` ({ts(rdur)})
Cover: `out/thumbnail-reel.jpg` (1080x1920)

### Title

{REEL_TITLES[i % 3].format(city=city)}

### Caption

{REEL_OPEN[i % 3].format(city=city)}
🏠 Junior ADU: from {k(pr['jadu'][0])}
🚗 Garage conversion: from {k(pr['garage'][0])}
🧱 Attached ADU: from {k(pr['attached'][0])}
🏡 Detached ADU: {k(pr['detached'][0])} – {k(pr['detached'][1])}+

🔨 Need an ADU builder? Give {co} a shout.
Design · permits · construction · reply within 24 hours
🔗 {url}

#shorts {HASH[c['key']]} #ADU #BackyardHome
"""
        (d / "youtube.md").write_text(md)
        (d / "README.md").write_text(f"""# Local Vibe Check: ADU Pricing Guide, {city} (2026)

Generated by `../_shared/adu-builders/build_scripts.py` (script) and `write_copy.py` (this README and youtube.md).

Sources:
- Local details, neighborhoods, permits, rules and FAQs: {url}
- Price baseline: All Exclusive Construction's 2026 Santa Monica ADU guide (see `../santa-monica-adu-pricing-2026`), scaled by {c['mult']:.2f} for {city} and rounded to $5,000
- Photos: ADU project photos from the ADU Builder Pros sites (`../_shared/adu-builders/`)

Ends with "need an ADU builder or contractor? Give {co} a shout".

Voice: {"Google Gemini TTS (gemini-3.8-flash-tts, voice Charon)" if spec.get("tts") == "gemini" and json.loads((d / "script.json").read_text()).get("tts") == "gemini" else "Microsoft edge-tts (Gemini daily quota reached)"}, prices read spelled out.

- `youtube.md`: titles, description, chapters, tags and the reel caption
- `out/{slug}.mp4`: main video, 1920x1080, {ts(dur)}
- `out/{slug}-reel.mp4`: Reel/Short, 1080x1920, {ts(rdur)}
- `out/thumbnail-youtube.jpg` (1280x720), `out/thumbnail-reel.jpg` (1080x1920)

Rebuild with the shared engine: see `../README.md`.
""")
        print("wrote", slug, ts(dur), ts(rdur))


if __name__ == "__main__":
    main()
