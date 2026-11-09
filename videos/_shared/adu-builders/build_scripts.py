"""Writes script.json, youtube.md and README.md for the 10 "ADU Builder Pros" pricing videos.

    python3 videos/_shared/adu-builders/build_scripts.py

Prices: the four ADU types from All Exclusive Construction's 2026 Santa Monica ADU guide
(the earlier santa-monica-adu-pricing-2026 video) are the baseline, scaled by a per-city
factor for local cost conditions (coastal review, hillside and fire-zone work, septic,
finish level, labor and land costs), then rounded to the nearest $5,000. The builder sites
themselves publish no prices.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEOS = HERE.parent.parent

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def w99(n):
    return ONES[n] if n < 20 else TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")


def w999(n):
    h, r = divmod(n, 100)
    return (ONES[h] + " hundred" + (" " + w99(r) if r else "")) if h else w99(r)


def words(n):
    m, r = divmod(n, 1_000_000)
    t, u = divmod(r, 1000)
    out = []
    if m: out.append(w999(m) + " million")
    if t: out.append(w999(t) + " thousand")
    if u: out.append(w999(u))
    return " ".join(out) or "zero"


def spell(text):
    """$60,000 -> sixty thousand dollars, for the voice."""
    return re.sub(r"\$(\d{1,3}(?:,\d{3})*)", lambda m: words(int(m.group(1).replace(",", ""))) + " dollars", text)


def money(k):
    return f"${k * 1000:,}"


def P(i):
    return next(f.name for f in HERE.glob(f"p{i:02d}-*.jpg"))


# Baseline (thousands of dollars): Santa Monica design/build ADU ranges.
BASE = {"jadu": (75, 150), "garage": (125, 250), "attached": (200, 375), "detached": (250, 500)}
TYPE = {
    "jadu": ("Junior ADU", "Up to 500 sq ft, inside the house"),
    "garage": ("Garage conversion", "Studio or 1-bedroom"),
    "attached": ("Attached ADU", "New addition to the house"),
    "detached": ("Detached ADU", "New backyard home"),
}
SPOKEN_TYPE = {"jadu": "a junior ADU", "garage": "a garage conversion", "attached": "an attached ADU", "detached": "a detached ADU"}


def r5(x):
    return int(round(x / 5.0)) * 5


def prices(mult):
    return {k: (r5(lo * mult), r5(hi * mult)) for k, (lo, hi) in BASE.items()}


# Statewide rule tiles every site lists; each city swaps in one local tile.
STATE = {
    "setback": {"v": "4 ft", "n": "Side & rear setbacks", "s": "The most a city can require", "cue": "4-foot"},
    "days": {"v": "60", "n": "Days to decide", "s": "On a complete application", "cue": "60"},
    "jadu": {"v": "500", "n": "Sq ft JADU cap", "s": "Junior ADUs stay inside the house", "cue": "500"},
    "fees": {"v": "≤750", "n": "Sq ft, no impact fees", "s": "Smaller units skip impact fees", "cue": "750"},
}

CITIES = [
    {
        "key": "santaclarita", "city": "Santa Clarita", "mult": 0.80,
        "hoods": ["Valencia", "Saugus", "Newhall", "Canyon Country", "Stevenson Ranch"],
        "areas": "Valencia, Saugus, Newhall, Canyon Country, Sand Canyon, Stevenson Ranch, Castaic & beyond",
        "hook_img": 20, "intro": "In the Santa Clarita Valley, an ADU can house aging parents, adult kids who work in the valley, or a long-term tenant.",
        "feats": [
            ("garage", "Saugus", "Garage conversion on an older tract lot", 24,
             ["Keeps the backyard open", "Reuses the slab, walls & roof", "No replacement parking required"],
             "Many older Saugus homes have an attached two-car garage facing the street."),
            ("jadu", "Bridgeport", "Junior ADU inside a Cape Cod home", 38,
             ["Up to 500 sq ft within the existing walls", "Separate outside door", "Efficiency kitchen"],
             "Compact Valencia lots where a backyard unit may not fit."),
            ("detached", "Stevenson Ranch", "Detached ADU on a hillside lot", 9,
             ["Permitted by LA County, not the city", "Stepped or engineered foundation", "Soils report & drainage"],
             "Sloped rear yards in the Santa Susana foothills."),
        ],
        "drivers": [
            ("City or county permit", "Stevenson Ranch & Castaic go through LA County", 2),
            ("Hillside lots", "Grading, retaining walls & soils reports", 26),
            ("Oak trees", "Protected oaks change where the ADU can go", 9),
            ("Fire zones", "2025 maps grew the Very High zones", 4),
            ("Utility runs", "Sewer laterals, trenching & panel upgrades", 1),
            ("Kitchens & baths", "Finishes move the total most", 23),
        ],
        "local_tile": {"v": "0", "n": "Parking spaces", "s": "City's 2026 ADU handout", "cue": "parking"},
        "tiles": ["setback", "days", "fees"],
        "faq": [
            ("Can I rent it out?", "Yes, for 30 days or longer. No vacation rentals", "roof"),
            ("Do I need parking?", "No parking required for ADUs or JADUs in the city", "map"),
            ("Must I live on site?", "No, except a JADU sharing a bath with the house", "pin"),
            ("Property taxes?", "Only the ADU's value is added; the house isn't reassessed", "chart"),
        ],
        "steps": [16, 30, 47, 46], "pick_img": 32, "cta_img": 20, "thumb": (20, ["ADU", "Prices"]),
    },
    {
        "key": "thousandoaks", "city": "Thousand Oaks", "mult": 0.85,
        "hoods": ["Newbury Park", "Dos Vientos", "Lang Ranch", "Wildwood", "Casa Conejo"],
        "areas": "Newbury Park, Dos Vientos, Lang Ranch, Wildwood, Casa Conejo, Lynn Ranch & Santa Rosa Valley",
        "hook_img": 32, "intro": "Conejo Valley families tend to stay: grown kids come home, parents move closer, and many lots have more yard than anyone uses.",
        "feats": [
            ("garage", "Casa Conejo", "Garage conversion on an early-1960s tract lot", 25,
             ["Reuses the slab & roof", "County island: Ventura County reviews it", "Keeps the yard open"],
             "Newbury Park's first planned community, with attached two-car garages."),
            ("jadu", "Dos Vientos", "Junior ADU inside an HOA home", 16,
             ["Up to 500 sq ft inside the house", "Its own entrance", "Simple HOA review"],
             "Compact lots with HOA design rules and little spare yard."),
            ("detached", "Wildwood", "Detached ADU on a sloped lot near open space", 20,
             ["Soils report & stepped foundation", "Oak root zones respected", "Ignition-resistant construction"],
             "Lots that slope toward canyon edges and carry mature oaks."),
        ],
        "drivers": [
            ("City or Ventura County", "County islands like Casa Conejo & Lynn Ranch", 2),
            ("Oak trees", "Work in a root zone can need an oak permit", 9),
            ("Slopes & canyon edges", "Retaining walls & stepped foundations", 8),
            ("Wildland edge", "Ignition-resistant materials near open space", 4),
            ("Utilities", "Panel upgrades & long trench runs", 0),
            ("HOA review", "Dos Vientos & Lang Ranch design standards", 47),
        ],
        "local_tile": {"v": "2026", "n": "New city ordinance", "s": "State law still sets the floor", "cue": "ordinance"},
        "tiles": ["days", "jadu", "fees"],
        "faq": [
            ("City or county?", "A Thousand Oaks address isn't always city-permitted", "map"),
            ("Near an oak tree?", "Often yes, but root-zone work can need a permit", "shield"),
            ("Can my HOA stop it?", "No, but it can apply reasonable design rules", "page"),
            ("Can I rent it out?", "Yes, for terms longer than 30 days", "roof"),
        ],
        "steps": [36, 41, 3, 33], "pick_img": 9, "cta_img": 32, "thumb": (36, ["ADU", "Cost"]),
    },
    {
        "key": "calabasas", "city": "Calabasas", "mult": 0.97,
        "hoods": ["Calabasas Highlands", "Mont Calabasas", "Park Moderne", "The Oaks", "Hidden Hills"],
        "areas": "Calabasas Highlands, Mont Calabasas, The Oaks, Park Moderne, Hidden Hills, Monte Nido & Bell Canyon",
        "hook_img": 9, "intro": "Buildable land in Calabasas is scarce, so an ADU adds a home on ground you already own.",
        "feats": [
            ("garage", "Mont Calabasas", "Garage conversion in a planned tract home", 24,
             ["Slab, roof & walls stay", "Kitchenette & bathroom added", "No replacement parking"],
             "Attached garages built to tract standards make conversion straightforward."),
            ("attached", "Calabasas Highlands", "Attached ADU on a sloped hillside lot", 32,
             ["Reuses the existing grade & foundation line", "Shorter utility runs", "Very High fire zone construction"],
             "Steep rear yards make a freestanding pad costly."),
            ("detached", "Park Moderne", "Compact detached ADU on a 5,000 sq ft lot", 9,
             ["One-story unit at the 4-foot setbacks", "Bedroom, bath & kitchen", "Windows placed for privacy"],
             "The original 1920s lots leave little rear yard."),
        ],
        "drivers": [
            ("Hillside foundations", "Can add a large share to any project", 26),
            ("Fire zone", "Wildland-urban interface standards & brush clearance", 4),
            ("HOA design rules", "Master-planned tracts off Parkway Calabasas", 32),
            ("Utility runs", "How far water, sewer & power must go", 1),
            ("Small lots", "Park Moderne's 5,000 sq ft parcels", 9),
            ("Kitchens & baths", "Same cost whether the unit is big or small", 18),
        ],
        "local_tile": {"v": "2026", "n": "Ordinance under state review", "s": "State law controls if they conflict", "cue": "state"},
        "tiles": ["setback", "days", "fees"],
        "faq": [
            ("Can my HOA stop it?", "No. State law voids CC&Rs that block ADUs", "page"),
            ("Fire-resistant build?", "Yes, in a Very High fire zone", "flame"),
            ("Need a parking space?", "Often not; garage spaces needn't be replaced", "map"),
            ("Can I rent it out?", "Yes, to long-term tenants over 30 days", "roof"),
        ],
        "steps": [7, 29, 21, 40], "pick_img": 30, "cta_img": 24, "thumb": (7, ["ADU", "Pricing"]),
    },
    {
        "key": "westlakevillage", "city": "Westlake Village", "mult": 0.87,
        "hoods": ["First Neighborhood", "North Ranch", "Southshore Hills", "Lake Sherwood", "Hidden Valley"],
        "areas": "First Neighborhood, Three Springs, Lakeshore, Westlake Island, Southshore Hills, North Ranch, Lake Sherwood & Hidden Valley",
        "hook_img": 32, "intro": "Westlake grew up as a planned suburb, with three-car garages, wide corner lots and bonus rooms that can become a separate home.",
        "feats": [
            ("garage", "First Neighborhood", "Garage conversion on an original tract lot", 24,
             ["Can start from LA County's pre-approved plan", "City Zoning Clearance", "Egress windows & insulation"],
             "The earliest Westlake streets, with attached garages on level lots."),
            ("attached", "Southshore Hills", "Attached ADU on a sloped hillside lot", 42,
             ["Builds on the existing pad", "Structural review & soils report", "Fire-rated materials"],
             "Homes that step down the hillsides south of the lake."),
            ("detached", "North Ranch", "Detached ADU among the oaks", 20,
             ["Sited outside oak root zones", "Utility trenching planned around trees", "HOA architectural review"],
             "Larger lots around the country club."),
        ],
        "drivers": [
            ("Which agency permits it", "City + LA County, Thousand Oaks or Ventura County", 2),
            ("Oak trees", "Protected oaks shape the footprint", 9),
            ("Hillside pads", "Structural work instead of cutting into slopes", 8),
            ("Well & septic", "Hidden Valley ranch parcels", 1),
            ("HOA review", "Colors, materials & roof style", 32),
            ("Finishes", "Kitchens & baths concentrate cost", 47),
        ],
        "local_tile": {"v": "2", "n": "Approvals in a row", "s": "City Zoning Clearance, then LA County permit", "cue": "two"},
        "tiles": ["setback", "days", "jadu"],
        "faq": [
            ("Which city permits it?", "Many Westlake addresses are in Thousand Oaks", "map"),
            ("Can my HOA stop it?", "No, but reasonable design rules apply", "page"),
            ("How close to the line?", "4-foot side & rear setbacks under state law", "roof"),
            ("Need parking?", "Not for conversions; max one space otherwise", "pin"),
        ],
        "steps": [42, 31, 23, 15], "pick_img": 3, "cta_img": 9, "thumb": (42, ["ADU", "Prices"]),
    },
    {
        "key": "beverlyhills", "city": "Beverly Hills", "mult": 1.15,
        "hoods": ["The Flats", "Trousdale Estates", "Southwest BH", "Beverly Crest"],
        "areas": "The Flats, Trousdale Estates, Southeast & Southwest Beverly Hills, Beverly Crest, Benedict Canyon & nearby LA",
        "hook_img": 9, "intro": "Most Beverly Hills properties were built with more yard than the owners use, and the city now invites more than one unit per lot.",
        "feats": [
            ("detached", "The Flats", "Detached guest house on a deep lot", 9,
             ["Up to 1,400 sq ft & 25 ft tall", "Often replaces an old rear garage", "Long, level lots"],
             "Lots between Sunset and Santa Monica Boulevard."),
            ("garage", "Beverly Crest", "Garage conversion on a hillside lot", 24,
             ["City of LA: LADBS reviews it", "No new grading on the slope", "Avoids fire-zone access issues"],
             "Steep lots on the LA side of the 90210."),
            ("attached", "Southwest Beverly Hills", "Attached ADU on a rectangular lot", 42,
             ["Shares a wall, keeps its own entrance", "Fits narrower side yards", "Objective standards skip extra review"],
             "More rectangular lots south of Wilshire."),
        ],
        "drivers": [
            ("Finish level", "High-end kitchens, baths & materials", 41),
            ("Size & height", "Guest houses up to 1,400 sq ft", 42),
            ("Fire zone", "North of Sunset: ignition-resistant build", 4),
            ("City of LA lots", "Beverly Crest & Benedict Canyon follow LADBS", 2),
            ("Extra review", "Minor Accommodation Permit if you exceed standards", 32),
            ("Utilities", "Panel upgrades & sewer runs", 0),
        ],
        "local_tile": {"v": "4", "n": "Units per lot", "s": "JADU, conversion, detached & one more", "cue": "four"},
        "tiles": ["days", "jadu", "fees"],
        "faq": [
            ("How many ADUs?", "Up to four on a single-family lot", "roof"),
            ("Is 90210 in the city?", "Not always: Beverly Crest is City of LA", "map"),
            ("Need parking?", "Often not near transit, like the new Metro stop", "pin"),
            ("Can I rent it out?", "Yes, for 31 days or longer", "page"),
        ],
        "steps": [31, 43, 37, 22], "pick_img": 30, "cta_img": 42, "thumb": (30, ["ADU", "Cost"]),
    },
    {
        "key": "malibu", "city": "Malibu", "mult": 1.20,
        "hoods": ["Point Dume", "Las Flores", "Carbon Beach", "Malibu Park", "Topanga"],
        "areas": "Point Dume, Malibu Colony, Carbon Beach, Broad Beach, Big Rock, Las Flores, Malibu Park, Trancas & Topanga",
        "hook_img": 20, "intro": "Malibu adds very few homes, so a second unit is one of the few ways to house family, staff or a year-round tenant on the coast.",
        "feats": [
            ("detached", "Point Dume", "Detached ADU on a fire-rebuild lot", 20,
             ["Planned with the main rebuild", "Shares septic, utilities & foundation work", "Single-story on flat land"],
             "Some of Malibu's flattest land, where many homes were lost in the Woolsey Fire."),
            ("garage", "Malibu Park", "Garage conversion on an existing pad", 24,
             ["Uses the level pad you already have", "No new grading or retaining walls", "Septic capacity checked first"],
             "Canyon and hillside lots often have one level pad: the garage."),
            ("jadu", "Carbon Beach", "Junior ADU inside a beach house", 38,
             ["Up to 500 sq ft within the walls", "No new footprint near the sand", "Its own exterior door"],
             "Tight beachfront lots where the buildable area is small."),
        ],
        "drivers": [
            ("Coastal review", "Every Malibu ADU is checked for coastal compliance", 9),
            ("Foundations", "Slabs, caissons or deep piles near the waves", 26),
            ("Septic", "An upgrade can change budget and placement", 1),
            ("Hillside & bluffs", "Retaining walls, drainage & bluff setbacks", 8),
            ("Fire rebuilds", "Plan the ADU with the new house to share costs", 4),
            ("Geology reports", "Common on canyon & bluff parcels", 2),
        ],
        "local_tile": {"v": "100%", "n": "Coastal Zone", "s": "Coastal review comes first", "cue": "coastal"},
        "tiles": ["setback", "days", "jadu"],
        "faq": [
            ("Coastal approval?", "Yes: all of Malibu is in the Coastal Zone", "drop"),
            ("Will my septic work?", "Depends on capacity; checked early", "search"),
            ("Short-term rental?", "No. Rentals must be over 30 days", "roof"),
            ("ADU with a fire rebuild?", "Often yes, sharing septic & foundation work", "flame"),
        ],
        "steps": [36, 33, 3, 38], "pick_img": 9, "cta_img": 30, "thumb": (9, ["ADU", "Prices"]),
    },
    {
        "key": "santamonica", "city": "Santa Monica", "mult": 1.00,
        "hoods": ["North of Montana", "Ocean Park", "Sunset Park", "Mid-City", "Sawtelle"],
        "areas": "North of Montana, Wilshire Montana, Mid-City, Pico, Ocean Park, Sunset Park, Santa Monica Canyon & Sawtelle",
        "hook_img": 9, "intro": "Santa Monica handles ADUs ministerially: no design review board, no public hearing and no neighbor appeal.",
        "feats": [
            ("detached", "North of Montana", "Two-bedroom detached ADU on a 50x150 lot", 20,
             ["Room for a two-story cottage", "A real garden between the buildings", "Family-sized ADUs most realistic here"],
             "Long, flat parcels with space near the rear line."),
            ("garage", "Sunset Park", "Garage conversion behind a 1940s cottage", 25,
             ["Reuses the footprint, keeps the yard", "Foundation check & structural review", "Insulation, windows & panel upgrade"],
             "Small postwar homes with a detached garage at the back."),
            ("jadu", "Mid-City", "Junior ADU with alley access", 2,
             ["Up to 500 sq ft inside the house", "Its own exterior door", "Alley makes deliveries easier"],
             "Grid blocks where a rear alley is the most useful thing on the lot."),
        ],
        "drivers": [
            ("Alley access", "Utilities, deliveries & a separate front door", 26),
            ("Coastal Zone lots", "Some parcels need a Coastal Commission permit", 9),
            ("Two-story units", "Structure, stairs & fire separation", 37),
            ("Older slabs", "Postwar garages often need upgrades", 25),
            ("Panel upgrades", "A second kitchen needs more power", 0),
            ("Finishes", "Kitchens & baths set the total", 18),
        ],
        "local_tile": {"v": "Condo", "n": "ADUs can be sold", "s": "Santa Monica's condo ordinance", "cue": "sold"},
        "tiles": ["setback", "days", "fees"],
        "faq": [
            ("Must I live on site?", "No owner occupancy required", "pin"),
            ("Vacation rental?", "No. Rentals must be over 30 days", "roof"),
            ("Need parking?", "No on-site parking required", "map"),
            ("Sell it separately?", "Yes, through the city's condo ordinance", "page"),
        ],
        "steps": [29, 39, 16, 44], "pick_img": 7, "cta_img": 20, "thumb": (47, ["ADU", "Cost"]),
    },
    {
        "key": "pacificpalisades", "city": "Pacific Palisades", "mult": 1.10,
        "hoods": ["Alphabet Streets", "Palisades Highlands", "Huntington Palisades", "Rustic Canyon", "The Riviera"],
        "areas": "Alphabet Streets, Marquez Knolls, Palisades Highlands, Castellammare, Huntington Palisades, Rustic Canyon & The Riviera",
        "hook_img": 32, "intro": "For many Palisades families rebuilding after the fire, an ADU can come first, and it doesn't shrink the house you plan to rebuild.",
        "feats": [
            ("detached", "Alphabet Streets", "Detached ADU on a compact flat lot", 9,
             ["Uses the 4-foot side & rear setbacks", "Usable yard between buildings", "LADBS permit & LADWP service"],
             "Some of the smallest, flattest parcels near the Village."),
            ("attached", "Huntington Palisades", "Attached ADU set back from a bluff", 42,
             ["25 ft from a coastal bluff, 10 ft from a canyon", "Skips Coastal & CEQA review on fire lots", "Built with or before the new house"],
             "Bluff-top parcels where distance from the edge sets the buildable area."),
            ("garage", "Rustic Canyon", "Garage conversion on a narrow canyon street", 24,
             ["Work stays inside an existing structure", "Fewer deliveries & haul trips", "Covered parking needn't be replaced"],
             "Canyon streets with little room to stage a new build."),
        ],
        "drivers": [
            ("Fire rebuild timing", "Build the ADU with or before the new home", 4),
            ("Bluffs & hillsides", "Deeper foundations & setbacks from the edge", 26),
            ("Narrow streets", "Staging, deliveries & haul trips", 25),
            ("Fire-zone materials", "Ignition-resistant construction", 8),
            ("LADWP service", "A separate meter means a bigger panel", 0),
            ("HOA guidelines", "Many Palisades HOAs regulate design", 32),
        ],
        "local_tile": {"v": "EO 1", "n": "Fire-lot fast track", "s": "No Coastal or CEQA review for many rebuild ADUs", "cue": "executive"},
        "tiles": ["days", "jadu", "fees"],
        "faq": [
            ("ADU before the house?", "Yes, and it doesn't count against floor area", "roof"),
            ("Can I rent it out?", "Yes, on leases longer than 30 days", "page"),
            ("Do HOAs get a say?", "Many regulate design, so plan for review", "shield"),
            ("Its own LADWP meter?", "Often yes, with a larger service", "bolt"),
        ],
        "steps": [41, 47, 34, 37], "pick_img": 20, "cta_img": 3, "thumb": (32, ["ADU", "Pricing"]),
    },
    {
        "key": "culvercity", "city": "Culver City", "mult": 0.93,
        "hoods": ["Carlson Park", "Sunkist Park", "Blair Hills", "Fox Hills", "Culver West"],
        "areas": "Blair Hills, Culver Crest, Carlson Park, Culver West, Sunkist Park, McManus, Fox Hills, Palms & Del Rey",
        "hook_img": 24, "intro": "Many Culver City homes sit on modest lots with a detached garage at the back, which is close to ideal for a second unit.",
        "feats": [
            ("garage", "Carlson Park", "Garage conversion behind a bungalow", 25,
             ["Detached garage at the back of the lot", "Keeps the yard intact", "No replacement parking"],
             "Older bungalows and Spanish revival homes with a rear garage."),
            ("detached", "Blair Hills", "Detached ADU on a fire-zone hillside", 20,
             ["Stepped or deeper footings", "Soils report", "Ignition-resistant siding & roofing"],
             "Very High fire zone on the slopes of the Baldwin Hills."),
            ("jadu", "Sunkist Park", "Junior ADU inside a post-war home", 16,
             ["Up to 500 sq ft within the walls", "Its own exterior door", "Keeps the backyard"],
             "Compact post-war homes on modest lots."),
        ],
        "drivers": [
            ("Pre-approved plans", "468, 637 or 806 sq ft new-build layouts", 32),
            ("Baldwin Hills slopes", "Retaining walls & longer utility runs", 26),
            ("Fire zone", "Blair Hills & Culver Crest", 4),
            ("Water provider", "LADWP or Golden State Water", 1),
            ("Older garages", "Foundation & framing checks", 25),
            ("Finishes", "Kitchens & baths move the total", 36),
        ],
        "local_tile": {"v": "3", "n": "Pre-approved plans", "s": "Studio, 1-bed & 2-bed layouts", "cue": "pre-approved"},
        "tiles": ["setback", "days", "fees"],
        "faq": [
            ("Who issues the permit?", "Culver City inside city limits; LA for Palms", "page"),
            ("Need parking?", "Often not near E Line stations or bus routes", "map"),
            ("Pre-approved plans?", "New builds only, not garage conversions", "search"),
            ("Legalize an old unit?", "Possibly, with the Safe ADU checklist", "shield"),
        ],
        "steps": [18, 45, 7, 10], "pick_img": 32, "cta_img": 9, "thumb": (24, ["ADU", "Prices"]),
    },
    {
        "key": "agourahills", "city": "Agoura Hills", "mult": 0.90,
        "hoods": ["Old Agoura", "Lake Lindero", "Morrison Ranch", "Indian Hills", "Liberty Canyon"],
        "areas": "Old Agoura, Morrison Ranch, Lake Lindero, Liberty Canyon, Hillrise, Indian Hills, Chateau Park, Oak Park & Malibou Lake",
        "hook_img": 9, "intro": "Open space wraps Agoura Hills, so new homes rarely come from new subdivisions. A backyard unit is one of the few ways to add one.",
        "feats": [
            ("jadu", "Lake Lindero", "Junior ADU inside a tract home", 38,
             ["Uses a bedroom wing or attached garage", "Under 500 sq ft, no added floor area", "Leaves the yard untouched"],
             "Homes in the original tract with a spare wing."),
            ("detached", "Old Agoura", "Detached cottage on an estate lot", 20,
             ["Half-acre and larger parcels", "Septic capacity needs Public Health sign-off", "Keeps the equestrian area"],
             "Room for a cottage set well back from the main house."),
            ("garage", "Liberty Canyon", "Garage conversion on a level lot", 24,
             ["Reuses the slab, walls & roof", "Lowest-cost path to a full unit", "No replacement parking"],
             "Modest, mostly level lots in the original tracts."),
        ],
        "drivers": [
            ("Oak tree zones", "The site plan must show oaks & root zones", 9),
            ("Fire zone", "Most of the city, including all south of the 101", 4),
            ("Septic", "Old Agoura parcels need Public Health sign-off", 1),
            ("Slopes", "Grading & retaining walls in Indian Hills", 26),
            ("HOA review", "Morrison Ranch & Chateau Park CC&Rs", 32),
            ("Long utility runs", "Big lots mean longer trenches", 0),
        ],
        "local_tile": {"v": "Oaks", "n": "On every site plan", "s": "Root zones drawn in; permit to dig inside", "cue": "oak"},
        "tiles": ["setback", "days", "jadu"],
        "faq": [
            ("Oak trees on my lot?", "Place the ADU outside protection zones", "shield"),
            ("In a fire zone?", "Quite possibly: most of the city is Very High", "flame"),
            ("Does my HOA approve?", "It can review design, but can't block it", "page"),
            ("Can I rent it out?", "Yes, long-term only, over 30 days", "roof"),
        ],
        "steps": [30, 19, 28, 40], "pick_img": 42, "cta_img": 20, "thumb": (29, ["ADU", "Cost"]),
    },
]

# Hook/ranges/winner phrasing rotates so the ten scripts don't read the same.
HOOKS = [
    "How much does it cost to build an ADU in {city} in 2026? Here's the pricing guide: what each type of ADU costs, real examples from {h1}, {h2} and {h3}, what drives the price, and the local rules to know.",
    "Thinking about adding an ADU in {city}? Here's what it costs in 2026, from a junior ADU to a brand-new backyard home, plus the local cost drivers and rules that shape your project.",
    "What does an accessory dwelling unit really cost in {city}? We break down 2026 prices for every type of ADU, the neighborhood examples, and what moves the price up or down.",
]
WINS = [
    "If you need an ADU builder or contractor in {city}, give {co} a shout. They handle the whole path, from site review and design to permits, construction and final inspection.",
    "Need an ADU builder in {city}? Give {co} a shout. They design, permit and build ADUs across {short}, from garage conversions to brand-new backyard homes.",
    "Looking for an ADU contractor in {city}? Give {co} a shout. One team handles your design, your permit file and the build, all the way to the final inspection.",
]


def scenes(c, i):
    city = c["city"]
    co = f"{city} ADU Builder Pros"
    domain = f"adubuilders{c['key']}.pro"
    pr = prices(c["mult"])
    h = c["hoods"]
    short = ", ".join(h[:3])
    lo_all = pr["jadu"][0]
    hi_all = pr["detached"][1]
    maxk = 600 if hi_all > 500 else 500
    ticks = [0, 200, 400, 600] if maxk == 600 else [0, 100, 200, 300, 400, 500]

    rows = [{"name": TYPE[k][0], "note": TYPE[k][1], "lo": pr[k][0], "hi": pr[k][1], "plus": True, "cue": cue}
            for k, cue in (("jadu", "junior"), ("garage", "garage"), ("attached", "attached"), ("detached", "detached"))]
    ranges_say = (f"In {city}, a junior ADU runs about {money(pr['jadu'][0])} to {money(pr['jadu'][1])} and up. "
                  f"A garage conversion, about {money(pr['garage'][0])} to {money(pr['garage'][1])}. "
                  f"An attached ADU, about {money(pr['attached'][0])} to {money(pr['attached'][1])}. "
                  f"And a brand-new detached ADU runs about {money(pr['detached'][0])} to {money(pr['detached'][1])} and up.")
    hook_say = HOOKS[i % 3].format(city=city, h1=c["feats"][0][1], h2=c["feats"][1][1], h3=c["feats"][2][1])

    land = [
        {"id": "hook", "kind": "title", "label": "2026 Price Guide", "image": P(c["hook_img"]),
         "kicker": f"{city}, California", "titlePx": 124, "title": ["ADU Pricing", "Guide"], "year": "2026",
         "chips": h[:5], "say": hook_say},
        {"id": "ranges", "kind": "ranges", "label": "2026 Price Ranges",
         "title": f"What an ADU costs in {city}", "sub": "2026 ranges · design, permits & construction",
         "max": maxk, "ticks": ticks, "rows": rows, "speak": spell(ranges_say), "say": ranges_say},
    ]
    for n, (typ, hood, title, img, bullets, desc) in enumerate(c["feats"], 1):
        lo, hi = pr[typ]
        b = [{"t": t, "cue": re.sub(r"[^a-z0-9-]", "", t.split()[0].lower())} for t in bullets]
        art = "an" if title[0].lower() in "aeiou" else "a"
        say = (f"In {hood}, a common fit is {art} {title[0].lower() + title[1:]}, at about {money(lo)} to {money(hi)} and up. "
               f"{desc} " + " ".join(t.rstrip(".") + "." for t in bullets)).replace(" & ", " and ")
        land.append({"id": f"f{n}", "kind": "price", "label": f"{hood}", "image": P(img),
                     "kicker": f"{hood} · {TYPE[typ][0]}", "name": title, "lo": lo, "hi": hi, "plus": True,
                     "priceCue": hood.split()[0], "desc": desc, "bullets": b, "speak": spell(say), "say": say})
    drv_say = (f"What drives the price in {city}? " + ". ".join(f"{d[0]}: {d[1][0].lower() + d[1][1:]}" for d in c["drivers"]) + ".")
    land.append({"id": "drivers", "kind": "factors", "label": "What Drives the Price", "cols": 3,
                 "title": f"What drives ADU cost in {city}",
                 "cards": [{"name": d[0], "desc": d[1], "image": P(d[2]), "cue": d[0].split()[0].lower()} for d in c["drivers"]],
                 "say": drv_say})
    tiles = [STATE[k] for k in c["tiles"]] + [c["local_tile"]]
    tiles_say = {
        "setback": "A city can require no more than four-foot side and rear setbacks.",
        "days": "A city has sixty days to act on a complete application.",
        "jadu": "A junior ADU tops out at five hundred square feet.",
        "fees": "And ADUs of seven hundred fifty square feet or less skip impact fees.",
    }
    local_say = {
        "santaclarita": "And in Santa Clarita, the city's 2026 handout requires zero parking spaces for ADUs.",
        "thousandoaks": "And Thousand Oaks adopted a new ADU ordinance in 2026, but state law still sets the floor.",
        "calabasas": "And Calabasas's ADU ordinance is under state review, so state law controls where they conflict.",
        "westlakevillage": "And in Westlake Village, you need two approvals in a row: a city Zoning Clearance, then an LA County building permit.",
        "beverlyhills": "And Beverly Hills allows up to four units on a single-family lot.",
        "malibu": "And because all of Malibu is in the Coastal Zone, coastal review comes first.",
        "santamonica": "And Santa Monica is one of the few cities where an ADU can be sold separately, as a condo.",
        "pacificpalisades": "And on fire-damaged lots, the Mayor's executive order lets many rebuild ADUs skip Coastal and CEQA review.",
        "culvercity": "And Culver City offers three pre-approved ADU plans for new builds.",
        "agourahills": "And in Agoura Hills, every ADU site plan has to show the oak trees and their root zones.",
    }[c["key"]]
    rule_say = "A few rules to know. " + " ".join(tiles_say[k] for k in c["tiles"]) + " " + local_say
    rule_say = rule_say.replace("And ADUs", "ADUs") if c["tiles"][-1] == "fees" else rule_say
    land.append({"id": "rules", "kind": "stats", "label": "Rules to Know", "title": f"{city} ADU rules to know",
                 "tiles": tiles, "tvPx": 64, "speak": rule_say, "say": rule_say.replace("sixty days", "60 days")
                 .replace("four-foot", "4-foot").replace("five hundred square feet", "500 square feet")
                 .replace("seven hundred fifty square feet", "750 square feet").replace("zero parking", "0 parking")})
    faq_say = "Common questions: " + " ".join(f"{q} {a}." for q, a, _ in c["faq"])
    land.append({"id": "faq", "kind": "factors", "label": "Common Questions", "cols": 4,
                 "title": "Common questions, answered",
                 "cards": [{"name": q, "desc": a, "icon": ic, "cue": q.split()[0].lower().strip("?")} for q, a, ic in c["faq"]],
                 "say": faq_say})
    if i % 2:  # vary the order: half the videos cover rules before the cost drivers
        land[5], land[6] = land[6], land[5]
    win_say = WINS[i % 3].format(city=city, co=co, short=short)
    land += [
        {"id": "pick", "kind": "winner", "label": "Need an ADU Builder?", "image": P(c["pick_img"]),
         "stamp": "Need an ADU builder?", "name": co, "nameCue": city.split()[0],
         "where": " · ".join(h[:4]),
         "points": ["Site review & ADU design", "Permits & plan check, city or county",
                    "Foundations, utilities & construction", "Garage conversions to new backyard homes",
                    "Reply within 24 hours"],
         "say": win_say},
        {"id": "work", "kind": "steps", "label": "ADU Interiors", "plain": True,
         "title": "Inside a finished ADU", "sub": "Kitchens, baths & living space",
         "steps": [{"image": P(s)} for s in c["steps"]],
         "say": "A finished ADU is a full home, with its own kitchen, bathroom and living space."},
        {"id": "cta", "kind": "cta", "label": "Free Consultation", "image": P(c["cta_img"]),
         "name": co, "phone": "Free Consultation", "phoneCue": "free",
         "address": "Design · Permits · Construction", "hours": "Reply within 24 hours",
         "url": domain, "urlCue": "visit", "tip": f"Serving {short} & more",
         "speak": f"For a free ADU consultation in {city}, visit adu builders {city.lower()} dot pro. This has been Local Vibe Check.",
         "say": f"For a free ADU consultation in {city}, visit {domain}. This has been Local Vibe Check."},
    ]
    reel_ranges_say = (f"A junior ADU in {city} starts around {money(pr['jadu'][0])}. A garage conversion, about {money(pr['garage'][0])}. "
                       f"An attached ADU, about {money(pr['attached'][0])}. And a new detached ADU runs about {money(pr['detached'][0])} to {money(pr['detached'][1])} and up.")
    reel = [
        {"id": "r-hook", "kind": "title", "label": "2026 Price Guide", "image": P(c["hook_img"]),
         "kicker": f"{city}, CA · 2026", "title": ["ADU", "Prices"], "year": "2026", "chips": h[:4],
         "say": f"What does an ADU cost in {city}?"},
        {"id": "r-ranges", "kind": "ranges", "label": "2026 Prices", "title": f"ADU prices, {city}",
         "max": maxk, "ticks": [0, maxk // 2, maxk],
         "rows": [{**r, "note": r["note"].split(",")[0]} for r in rows], "speak": spell(reel_ranges_say), "say": reel_ranges_say},
        {"id": "r-pick", "kind": "winner", "label": "Need an ADU Builder?", "image": P(c["pick_img"]),
         "stamp": "Need an ADU builder?", "name": co, "nameCue": city.split()[0], "where": short,
         "points": ["Design & permits", "Construction", "Reply within 24 hours"],
         "say": f"Need an ADU builder or contractor? Give {co} a shout."},
        {"id": "r-cta", "kind": "cta", "label": "Free Consultation", "image": P(c["cta_img"]),
         "name": co, "phone": "Free Consultation", "phoneCue": "free", "address": "Design · Permits · Construction",
         "hours": "Reply within 24 hours", "url": domain, "urlCue": "visit", "tip": "Follow Local Vibe Check for more.",
         "speak": f"Visit adu builders {city.lower()} dot pro for a free consultation.",
         "say": f"Visit {domain} for a free consultation."},
    ]
    return land, reel, pr


def stamp(i):
    return [["4", ["ADU", "TYPES"]], ["2026", ["PRICE", "GUIDE"]], ["4", ["PRICE", "RANGES"]]][i % 3]


def build(c, i):
    slug = f"{c['key'].replace('santaclarita', 'santa-clarita').replace('thousandoaks', 'thousand-oaks').replace('westlakevillage', 'westlake-village').replace('beverlyhills', 'beverly-hills').replace('santamonica', 'santa-monica').replace('pacificpalisades', 'pacific-palisades').replace('culvercity', 'culver-city').replace('agourahills', 'agoura-hills')}-adu-builder-pricing-2026"
    land, reel, pr = scenes(c, i)
    img, lines = c["thumb"]
    spec = {
        "tts": "gemini", "gemini": {"model": "gemini-3.8-flash-tts", "voice": "Charon"},
        "assetsDir": "../_shared/adu-builders",
        "header": f"{c['city']}, CA · ADU Prices · 2026",
        "source": f"Estimated 2026 ranges: a Westside design/build ADU baseline adjusted for {c['city']} conditions. Ballpark only; get an on-site estimate.",
        "sourceKinds": ["ranges", "price"],
        "thumbs": {"image": P(img), "landscapePos": "50% 50%", "reelPos": "50% 50%", "lines": lines,
                   "sub": f"{c['city']}, CA", "tag": f"From {money(pr['jadu'][0]).replace(',000', 'K')}", "year": "2026",
                   "bigPx": 150, "reelBigPx": 210, "subPx": 52, "reelSubPx": 68,
                   "stamp": stamp(i), "reelStamp": stamp(i + 1)},
        "landscape": land, "reel": reel,
    }
    return slug, spec, pr


def main():
    out = []
    for i, c in enumerate(CITIES):
        slug, spec, pr = build(c, i)
        d = VIDEOS / slug
        (d / "out").mkdir(parents=True, exist_ok=True)
        (d / "script.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
        (d / ".gitignore").write_text(f"# Keep only the deliverables and timings from out/\nout/*\n!out/timings.json\n!out/{slug}.mp4\n!out/{slug}-reel.mp4\n!out/thumbnail-youtube.jpg\n!out/thumbnail-reel.jpg\n")
        out.append((slug, c["city"], {k: v for k, v in pr.items()}))
    json.dump(out, open(HERE / "projects.json", "w"), indent=1)
    for slug, city, pr in out:
        print(slug, {k: f"{lo}-{hi}K" for k, (lo, hi) in pr.items()})


if __name__ == "__main__":
    main()
