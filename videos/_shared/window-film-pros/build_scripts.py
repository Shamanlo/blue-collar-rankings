"""Builds the 14 "Window Film Pros" business-spotlight videos (script.json, youtube.md, README.md).

    python3 videos/_shared/window-film-pros/build_scripts.py          # write script.json files
    python3 videos/_shared/window-film-pros/build_scripts.py copy     # write youtube.md + README (after tts.py)

All facts come from each business's own site (content.json, parsed from windowfilm<city>.pro).
Scene order, wording, photos, thumbnail and voice rotate per city so no two videos match.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEOS = HERE.parent.parent
C = json.loads((HERE / "content.json").read_text())

ORDER = ["oakland", "sanfrancisco", "houston", "dfw", "nyc", "chicago", "seattle",
         "sandiego", "philly", "riverside", "phoenix", "miami", "atlanta", "dc"]
CITY = {"oakland": "Oakland", "sanfrancisco": "San Francisco", "houston": "Houston", "dfw": "Dallas-Fort Worth",
        "nyc": "New York City", "chicago": "Chicago", "seattle": "Seattle", "sandiego": "San Diego",
        "philly": "Philadelphia", "riverside": "Riverside", "phoenix": "Phoenix", "miami": "Miami",
        "atlanta": "Atlanta", "dc": "Washington, DC"}
SHORT = {"dfw": "DFW", "nyc": "NYC", "dc": "DC", "sanfrancisco": "SF"}
STATE = {"oakland": "CA", "sanfrancisco": "CA", "houston": "TX", "dfw": "TX", "nyc": "NY", "chicago": "IL",
         "seattle": "WA", "sandiego": "CA", "philly": "PA", "riverside": "CA", "phoenix": "AZ", "miami": "FL",
         "atlanta": "GA", "dc": "DC"}
SLUG = {"oakland": "oakland", "sanfrancisco": "san-francisco", "houston": "houston", "dfw": "dallas-fort-worth",
        "nyc": "new-york-city", "chicago": "chicago", "seattle": "seattle", "sandiego": "san-diego",
        "philly": "philadelphia", "riverside": "riverside", "phoenix": "phoenix", "miami": "miami",
        "atlanta": "atlanta", "dc": "washington-dc"}
VOICES = ["en-US-AndrewNeural", "en-US-BrianNeural", "en-US-ChristopherNeural", "en-US-GuyNeural"]

# Photo pool (w00..w21) split by subject.
RES = [3, 7, 13, 14, 15, 2, 9, 10]
COM = [6, 8, 11, 16, 17, 1, 5, 12, 0, 20, 21, 19, 18, 4]


def W(i):
    return next(f.name for f in HERE.glob(f"w{i:02d}-*.jpg"))


BRANDED = {4, 18, 19}  # another business's storefront signage: fine in the body, not on thumbnails or the opener


def own_photos(key, plain=False):
    """Pool ids that appear on this city's own site."""
    pool = json.loads((HERE / "pool.json").read_text())
    ids = [p["id"] for p in pool if key in p["cities"]]
    return [x for x in ids if x not in BRANDED] if plain else ids


def they(t):
    for a, b in [(r"\bWe'll\b", "They'll"), (r"\bwe'll\b", "they'll"), (r"\bWe're\b", "They're"), (r"\bwe're\b", "they're"),
                 (r"\bWe\b", "They"), (r"\bwe\b", "they"), (r"\bus\b", "them"), (r"\bOur\b", "Their"), (r"\bour\b", "their"),
                 (r"\bourselves\b", "themselves")]:
        t = re.sub(a, b, t)
    return t


def sentences(text, n):
    text = they(text)
    s = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"])", text.strip())
    return " ".join(s[:n])


def shorten(text, limit=74):
    t = _shorten(text, limit)
    if t.count("(") > t.count(")"):
        t = t[:t.rfind("(")].rstrip(" ,")
    return t


def trim_title(h, limit=64):
    if len(h) <= limit:
        return h
    return _trim(h, limit).removesuffix(" or").removesuffix(" and")


def _trim(h, limit):
    cuts = [m.start() for m in re.finditer(r",| Through | From | After | in | for | if | of the | on ", h) if 20 < m.start() <= limit]
    if cuts:
        return h[:cuts[-1]].rstrip(" ,:")
    h = h[:limit].rsplit(" ", 1)[0]
    while h.split()[-1].lower() in ("in", "and", "of", "for", "the", "on", "a", "to", "from", "with"):
        h = h.rsplit(" ", 1)[0]
    return h.rstrip(" ,:")


def _shorten(text, limit=74):
    t = sentences(text, 1).rstrip(".")
    if len(t) <= limit:
        return t
    for sep in (", so ", ", which ", " so ", ", ", " and ", " with ", " that "):
        cut = t.find(sep, 25)
        if 25 < cut <= limit:
            return t[:cut]
    return t[:limit].rsplit(" ", 1)[0]


def svc_name(name, place):
    n = re.sub(r"\s+in\s+.+$", "", name)
    n = n.replace("Window Tinting", "Tinting")
    n = re.sub(r"\s+(Window\s+)?Film$", "", n).strip()
    return n or name


def lower1(t):
    return t if t[:2].isupper() else t[0].lower() + t[1:]


def faq_name(q, city):
    for c in (city, city.split(",")[0], "DC", "NYC", "DFW", "Dallas-Fort Worth"):
        q = re.sub(rf" in {re.escape(c)}\?$", "?", q)
        q = re.sub(rf"\bmy {re.escape(c)} (?=[a-z])", "my ", q)
    return q if len(q) <= 84 else trim_title(q[:-1], 82) + "?"


def section(d, *words, skip=()):
    for s in d["sections"]:
        h = s[0]
        if any(w.lower() in h.lower() for w in words) and not any(x in h for x in skip):
            return s
    return None


BAD = ("Residential Window Film for", "Commercial Window Film for", "Service Areas", "Questions", "Email",
       "Send Your", "FAQs", "Neighborhoods and")


def local_sections(d):
    return [s for s in d["sections"] if not any(b in s[0] for b in BAD)]


def scenes(key, i):
    d = C[key]
    city = CITY[key]
    co = d["company"]
    domain = f"windowfilm{key}.pro"
    areas = d["areas"]
    rot = lambda lst, k: lst[k % len(lst):] + lst[:k % len(lst)]
    own = own_photos(key)
    res_pool = [p for p in rot(RES, i) if p in own] + [p for p in rot(RES, i * 2) if p not in own]
    com_pool = [p for p in rot(COM, i) if p in own] + [p for p in rot(COM, i * 3) if p not in own]
    loc = local_sections(d)
    weather = loc[0]
    rest = loc[1:]
    local_a = rest[(i) % len(rest)] if rest else weather
    local_b = rest[(i + 1) % len(rest)] if len(rest) > 1 else None

    res = [s for s in d["services"] if not s[0].startswith(("Office", "Storefront", "Commercial", "Anti-Graffiti", "Decorative & Frosted", "Solar Control", "Conference", "Low-E"))]
    com = [s for s in d["services"] if s not in res]
    res4 = rot(res, i)[:4]
    com4 = rot(com, i + 1)[:4]

    hook_titles = [["Window Film", f"in {SHORT.get(key, city)}"], [f"{SHORT.get(key, city)}", "Window Film Pros"],
                   ["Meet the", "Window Film Pros"], ["Local Spotlight:", "Window Film"]]
    hooks = [
        f"Local business spotlight: {co}. They install window film for homes and businesses across {city}, cutting heat, glare and UV on the glass you already have.",
        f"Is your {city} home or office too hot, too bright, or too exposed? Meet {co}, the local window film and window tinting installers.",
        f"Today on Local Vibe Check, we're spotlighting {co}, a window film installer working in neighborhoods from {areas[0]} to {areas[5]}.",
        f"Thinking about window tinting in {city}? Here's a look at {co}, what they install, and why window film makes sense here.",
    ]
    tp = hook_titles[i % 4]
    sc = {}
    plain = own_photos(key, True)
    sc["hook"] = {"id": "hook", "kind": "title", "label": "Local Business Spotlight", "image": W(plain[i % len(plain)]),
                  "kicker": f"{city} · Local business spotlight", "titlePx": 112 if max(len(x) for x in tp) > 14 else 128,
                  "title": tp, "year": "2026", "chips": rot(areas, i * 3)[:5], "say": hooks[i % 4]}
    sc["weather"] = {"id": "weather", "kind": "steps", "label": "Why Window Film Here", "plain": True,
                     "title": trim_title(weather[0]),
                     "sub": f"{city}, {STATE[key]}",
                     "steps": [{"image": W(p)} for p in (res_pool[1], com_pool[1], res_pool[2])],
                     "say": sentences(weather[1], 3)}
    st = {k: v for k, v in d["stats"]}
    sc["stats"] = {"id": "stats", "kind": "stats", "label": "What Film Blocks",
                   "title": "What window film can block",
                   "tiles": [{"v": st["UV rays"], "n": "UV rays", "s": "Slows fading of floors & furniture", "cue": "UV"},
                             {"v": st["Solar heat"], "n": "Solar heat", "s": "Cooler rooms near the glass", "cue": "solar"},
                             {"v": st["Glare"], "n": "Glare", "s": "Screens stay readable", "cue": "glare"}],
                   "note": "Typical upper ranges; your numbers depend on the film and the glass.", "noteCue": "typical",
                   "say": ["Window film blocks up to 99 percent of UV rays, up to 80 percent of solar heat, and up to 90 percent of glare. Your numbers depend on the film and the glass, and they spec that before install.",
                           "The numbers: up to 99 percent of UV, up to 80 percent of solar heat, and up to 90 percent of glare, depending on the film and your glass.",
                           "On the glass you already have, film can block up to 99 percent of UV rays, up to 80 percent of solar heat, and up to 90 percent of glare."][i % 3]}
    sc["res"] = {"id": "res", "kind": "factors", "label": "For Homes", "cols": 4,
                 "title": f"Home window film in {SHORT.get(key, city)}",
                 "cards": [{"name": svc_name(n, d["place"]), "desc": shorten(they(t)), "image": W(res_pool[(k + 3) % len(res_pool)]),
                            "cue": svc_name(n, d["place"]).split()[0].lower()} for k, (n, t) in enumerate(res4)],
                 "say": "For homes: " + " ".join(f"{svc_name(n, d['place'])}: {shorten(they(t), 200)}." for n, t in res4)}
    icons = ["page", "shield", "star", "chart", "bolt", "search", "pin", "clock"]
    sc["com"] = {"id": "com", "kind": "factors", "label": "For Businesses", "cols": 4,
                 "title": "Commercial window film",
                 "cards": [{"name": svc_name(n, d["place"]), "desc": shorten(they(t)), "icon": icons[(k + i) % len(icons)],
                            "cue": svc_name(n, d["place"]).split()[0].lower().rstrip("&")} for k, (n, t) in enumerate(com4)],
                 "say": "For businesses: " + " ".join(f"{svc_name(n, d['place'])}: {shorten(they(t), 200)}." for n, t in com4)}
    sc["local"] = {"id": "local", "kind": "steps", "label": "Local Know-How", "plain": True,
                   "title": trim_title(local_a[0]),
                   "sub": " · ".join(rot(areas, i + 2)[:3]),
                   "steps": [{"image": W(p)} for p in (com_pool[3], res_pool[4], com_pool[4])],
                   "say": sentences(local_a[1], 3)}
    steps = d["steps"]
    sc["process"] = {"id": "process", "kind": "stats", "label": "How It Works",
                     "title": "How an install works",
                     "tiles": [{"v": f"0{k + 1}", "n": ["Request a quote", "Film & glass check", "Install day", "Curing & care"][k],
                                "s": shorten(they(s[1]), 60), "cue": ["first", "then", "on", "finally"][k]} for k, s in enumerate(steps)],
                     "say": "Here's how an install works. " + " ".join(f"{['First', 'Then', 'On install day', 'Finally'][k]}, {lower1(shorten(they(s[1]), 150))}." for k, s in enumerate(steps))}
    faqs = rot(d["faqs"], i)[:4]
    fic = ["search", "clock", "shield", "page", "roof", "chart"]
    sc["faq"] = {"id": "faq", "kind": "factors", "label": "Common Questions", "cols": 4,
                 "title": "Common questions, answered",
                 "cards": [{"name": faq_name(q, city), "desc": shorten(they(a), 70), "icon": fic[(k + i) % len(fic)],
                            "cue": q.split()[0].lower()} for k, (q, a) in enumerate(faqs)],
                 "say": "Common questions: " + " ".join(f"{q} {sentences(a, 1)}" for q, a in faqs[:3])}
    sc["areas"] = {"id": "areas", "kind": "list", "label": "Service Areas",
                   "title": f"Where they work in {SHORT.get(key, city)}",
                   "items": rot(areas, i * 2)[:6],
                   "note": f"{len(areas)} neighborhoods & nearby cities served", "noteCue": str(len(areas)),
                   "say": f"They cover {city} neighborhoods including " + ", ".join(rot(areas, i * 2)[:5]) + f", and {rot(areas, i * 2)[5]}, {len(areas)} areas in all."}
    pts = [
        ["Residential & commercial window film", "Film matched to your glass & orientation", "Samples shown on your own windows", "After-hours installs for offices & shops", "Reply within 24 hours"],
        ["Heat, glare, UV & privacy film", "Security & anti-graffiti film", "Glass checked before anything is installed", "Quotes by online request", "Reply within 24 hours"],
        ["Homes, condos, offices & storefronts", "Most houses done in a day or less", "Honest advice on which windows need film", "Decorative & frosted glass film", "Reply within 24 hours"],
    ][i % 3]
    pick_say = [
        f"If you need window film or window tinting in {city}, give {co} a shout. They handle homes and businesses, and they match the film to your glass, not a catalog.",
        f"So if your {city} windows are too hot, too bright or too exposed, give {co} a shout for a quote.",
        f"Need window tinting in {city}? {co} is worth a call. They'll tell you which windows need film, and which should be left alone.",
    ][i % 3]
    sc["pick"] = {"id": "pick", "kind": "winner", "label": "Local Spotlight", "image": W(own[(i + 2) % len(own)] if own else com_pool[5]),
                  "stamp": "Local spotlight", "name": co, "nameCue": co.split()[0],
                  "where": " · ".join(rot(areas, i)[:4]), "logo": f"logo-{key}.png", "logoBg": "#fff",
                  "points": pts, "say": pick_say}
    sc["cta"] = {"id": "cta", "kind": "cta", "label": "Free Quote", "image": W(own[(i + 4) % len(own)] if own else res_pool[5]),
                 "logo": f"logo-{key}.png", "name": co, "phone": "Free Quote", "phoneCue": "free",
                 "address": "Homes · Offices · Storefronts", "hours": "Reply within 24 hours by phone or email",
                 "url": domain, "urlCue": "visit", "tip": "Send rough window sizes for a faster quote.",
                 "speak": f"For a free window film quote, visit window film {key if key not in ('nyc', 'dc', 'dfw') else ' '.join(key.upper())} dot pro. This has been Local Vibe Check.",
                 "say": f"For a free window film quote, visit {domain}. This has been Local Vibe Check."}

    orders = [
        ["hook", "weather", "stats", "res", "com", "local", "process", "faq", "areas", "pick", "cta"],
        ["hook", "stats", "com", "res", "weather", "local", "faq", "process", "areas", "pick", "cta"],
        ["hook", "local", "weather", "res", "stats", "com", "process", "areas", "faq", "pick", "cta"],
        ["hook", "weather", "res", "com", "stats", "faq", "local", "areas", "process", "pick", "cta"],
    ]
    land = [sc[k] for k in orders[i % 4]]
    reel = [
        {**sc["hook"], "id": "r-hook", "title": [f"{SHORT.get(key, city)}", "Window Film"], "chips": rot(areas, i)[:4],
         "say": [f"Too much sun in {city}? Here's a local fix.", f"Meet {co}.", f"Window tinting in {city}? Watch this."][i % 3]},
        {**sc["stats"], "id": "r-stats", "note": None, "say": "Window film can block up to 99 percent of UV, 80 percent of solar heat, and 90 percent of glare."},
        {**sc["pick"], "id": "r-pick", "points": pts[:3], "where": " · ".join(rot(areas, i)[:3]),
         "say": f"For homes and businesses across {city}, give {co} a shout."},
        {**sc["cta"], "id": "r-cta", "tip": "Follow Local Vibe Check for more.",
         "speak": sc["cta"]["speak"].replace(" This has been Local Vibe Check.", ""),
         "say": sc["cta"]["say"].replace(" This has been Local Vibe Check.", "")},
    ]
    reel[1].pop("note")
    reel[1].pop("noteCue", None)
    return land, reel


THUMB = {"atlanta": 10, "chicago": 15, "dfw": 7, "houston": 14, "miami": 5, "nyc": 17, "oakland": 11, "philly": 1,
         "phoenix": 6, "riverside": 9, "sandiego": 12, "sanfrancisco": 13, "seattle": 20, "dc": 21}  # one photo per city
STAMPS = [["99%", ["UV", "BLOCKED"]], ["80%", ["LESS", "HEAT"]], ["90%", ["LESS", "GLARE"]], ["LOCAL", ["SPOT", "LIGHT"]]]


def build(key, i):
    land, reel = scenes(key, i)
    own = own_photos(key, True)
    city = CITY[key]
    lines = [["Window Film", SHORT.get(key, city)], ["Window", "Tinting"], [SHORT.get(key, city), "Window Film"]][i % 3]
    big = 100 if max(len(x) for x in lines) <= 11 else 84
    return {
        "voice": VOICES[i % len(VOICES)], "rate": "+6%",
        "assetsDir": "../_shared/window-film-pros",
        "header": f"{city} · Local Business Spotlight · 2026",
        "source": f"Business details from windowfilm{key}.pro. Film figures are typical upper ranges.",
        "sourceKinds": ["stats"],
        "thumbs": {"image": W(THUMB[key]), "landscapePos": "50% 50%", "reelPos": "50% 50%",
                   "lines": lines, "sub": C[key]["company"], "tag": "Local Spotlight", "year": "2026",
                   "bigPx": big, "reelBigPx": int(big * 1.45), "subPx": 44, "reelSubPx": 60,
                   "stamp": STAMPS[i % 4], "reelStamp": STAMPS[(i + 1) % 4]},
        "landscape": land, "reel": reel,
    }


def slug(key):
    return f"window-film-{SLUG[key]}-spotlight-2026"


def write_scripts():
    for i, key in enumerate(ORDER):
        d = VIDEOS / slug(key)
        (d / "out").mkdir(parents=True, exist_ok=True)
        (d / "script.json").write_text(json.dumps(build(key, i), indent=1, ensure_ascii=False) + "\n")
        s = slug(key)
        (d / ".gitignore").write_text(f"# Keep only the deliverables and timings from out/\nout/*\n!out/timings.json\n!out/{s}.mp4\n!out/{s}-reel.mp4\n!out/thumbnail-youtube.jpg\n!out/thumbnail-reel.jpg\n")
        print("wrote", s, VOICES[i % len(VOICES)])


TITLES = [
    "{co}: Window Film & Window Tinting in {city} (Local Business Spotlight)",
    "Best Window Film in {city}? Meet {co} (2026)",
    "{city} Window Tinting for Homes & Businesses | {co} Spotlight",
    "Window Film in {city}: Heat, Glare & UV Control | {co}",
]
REEL_TITLES = ["{short} Window Film Pros: Local Spotlight 🪟 #shorts", "Too Much Sun in {city}? 🌞 #shorts",
               "Window Tinting in {city} (2026) 🏙️ #shorts", "Meet {co} 🪟 #shorts"]
TAGS = "window film {lc}, window tinting {lc}, home window tinting {lc}, commercial window film {lc}, {lc} window tint, heat control window film, uv window film, privacy window film, security window film, {co_lc}"


def ts(sec):
    s = int(sec)
    return f"{s // 60}:{s % 60:02d}"


def write_copy():
    for i, key in enumerate(ORDER):
        d = C[key]
        city, co = CITY[key], d["company"]
        url = f"https://windowfilm{key}.pro/"
        p = VIDEOS / slug(key)
        spec = json.loads((p / "script.json").read_text())
        tm = json.loads((p / "out" / "timings.json").read_text())
        by = {s["id"]: s for s in spec["landscape"]}
        label = {"hook": f"Meet {co}", "weather": by["weather"]["title"], "stats": "What window film can block",
                 "res": "Window film for homes", "com": "Commercial window film", "local": by["local"]["title"],
                 "process": "How an install works", "faq": "Common questions", "areas": "Service areas",
                 "pick": f"Give {co} a shout", "cta": "Get a free quote"}
        chapters = "\n".join(f"{ts(s['start'])} {label[s['id']]}" for s in tm["landscape"])
        res = "\n".join(f"• {c['name']}: {c['desc']}" for c in by["res"]["cards"])
        com = "\n".join(f"• {c['name']}: {c['desc']}" for c in by["com"]["cards"])
        faq = "\n".join(f"• {q} {sentences(a, 1)}" for q, a in d["faqs"][i % 7:][:3] + d["faqs"][:max(0, 3 - len(d['faqs'][i % 7:]))])
        dur = sum(s["dur"] for s in tm["landscape"])
        rdur = sum(s["dur"] for s in tm["reel"])
        lc = city.lower()
        tags = TAGS.format(lc=lc, co_lc=co.lower())
        hashtag = "#" + re.sub(r"[^A-Za-z]", "", city)
        md = f"""# Local Vibe Check: Business Spotlight, {co} (2026)

## Main video (16:9)

File: `out/{slug(key)}.mp4` ({ts(dur)})
Thumbnail: `out/thumbnail-youtube.jpg` (1280x720)

### Title

{TITLES[i % 4].format(co=co, city=city)}

### Description

{they(d['hero'])}

🔗 {co}:
{url}

{sentences(by['weather']['say'], 2)}

Window film can block up to {d['stats'][0][1]} of UV rays, up to {d['stats'][1][1]} of solar heat and up to {d['stats'][2][1]} of glare (typical upper ranges; your numbers depend on the film and the glass).

Window film for {city} homes:
{res}

Commercial window film:
{com}

{by['local']['title']}: {sentences(by['local']['say'], 2)}

How an install works: send rough window sizes through the quote form, see film samples on your own glass, installation day (a typical house in a day or less), then a short curing period.

Common questions:
{faq}

📍 Service areas: {', '.join(d['areas'])}

🪟 Need window film or window tinting in {city}? Give {co} a shout.
Residential & commercial · heat, glare, UV, privacy, decorative, security & anti-graffiti film · reply within 24 hours by phone or email
🌐 Free quote: {url}

Chapters:
{chapters}

Local Vibe Check: price guides, places and trusted local businesses. Subscribe for more local spotlights.

{hashtag} #WindowFilm #WindowTinting #HomeImprovement #SmallBusiness #LocalBusiness

### Tags

{tags}

## Reel / YouTube Short (9:16)

File: `out/{slug(key)}-reel.mp4` ({ts(rdur)})
Cover: `out/thumbnail-reel.jpg` (1080x1920)

### Title

{REEL_TITLES[i % 4].format(co=co, city=city, short=SHORT.get(key, city))}

### Caption

{["Local spotlight", "Too much sun?", "Window tinting in " + city + "?", "Meet the local window film pros"][i % 4]} 👇 {co} installs window film for homes and businesses across {city}.
🌞 Up to {d['stats'][1][1]} less solar heat
🛋️ Up to {d['stats'][0][1]} of UV blocked
💻 Up to {d['stats'][2][1]} less glare

🔗 Free quote: {url}

#shorts {hashtag} #WindowFilm #WindowTinting #LocalBusiness
"""
        (p / "youtube.md").write_text(md)
        (p / "README.md").write_text(f"""# Local Vibe Check: Business Spotlight, {co} (2026)

Generated by `../_shared/window-film-pros/build_scripts.py` from the business's own site: {url}
(services, weather and building notes, process, FAQs and service areas). Photos and logo from the Window Film Pros sites.

Voice: Microsoft edge-tts ({spec['voice']}). Scene order, wording, photos and voice rotate across the 14 spotlights.

- `youtube.md`: title, description, chapters, tags and the reel caption
- `out/{slug(key)}.mp4` ({ts(dur)}), `out/{slug(key)}-reel.mp4` ({ts(rdur)})
- `out/thumbnail-youtube.jpg`, `out/thumbnail-reel.jpg`
""")
        print("copy", slug(key), ts(dur), ts(rdur))


if __name__ == "__main__":
    write_copy() if sys.argv[1:] == ["copy"] else write_scripts()
