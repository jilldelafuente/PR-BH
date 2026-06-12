"""
inject_bh.py — Bakes bh_atlanta.json into index.html as window.BH.LISTINGS
so the prototype can switch between Progress and BH data.

Run after scrape_bh.py:
    python3 inject_bh.py
"""

import json, re, os, statistics
from pathlib import Path

BH_AMENITY_MAP = [
    (r"pool|swimming",           "car",       "Swimming Pool"),
    (r"fitness|gym|workout",     "layers",    "Fitness Center"),
    (r"clubhouse|club house",    "home",      "Clubhouse"),
    (r"pet|dog|cat",             "dog",       "Pet Friendly"),
    (r"garage|parking|covered",  "car",       "Covered Parking"),
    (r"washer|dryer|laundry",    "layers",    "In-Unit Laundry"),
    (r"stainless|appliance",     "check",     "Stainless Appliances"),
    (r"granite|quartz|countertop","check",    "Granite Countertops"),
    (r"hardwood|vinyl|flooring", "ruler",     "Hard Surface Floors"),
    (r"balcony|patio|terrace",   "home",      "Private Balcony/Patio"),
    (r"smart|thermostat|tech",   "sparkles",  "Smart Home Tech"),
    (r"air conditioning|a/c|central air","ac","Central A/C"),
    (r"walk.in closet|wic",      "layers",    "Walk-In Closet"),
    (r"elevator",                "layers",    "Elevator Access"),
    (r"24.hour|emergency|maintenance","check","24/7 Maintenance"),
    (r"dishwasher",              "check",     "Dishwasher"),
    (r"ceiling fan",             "layers",    "Ceiling Fans"),
    (r"fireplace",               "home",      "Fireplace"),
    (r"high.ceiling|nine.foot|ten.foot|9.foot|10.foot|vaulted","arrow","High Ceilings"),
    (r"storage|extra storage",   "layers",    "Extra Storage"),
]

def _derive_amenities(raw):
    """Extract real amenities from unit type features + page text."""
    import re as _re
    # Collect all text: unit type descriptions + raw amenities
    texts = []
    for ut in raw.get("unit_types", []):
        texts.append(str(ut))
    for a in raw.get("amenities", []):
        texts.append(a.lower())
    combined = " ".join(texts).lower()

    found = []
    seen_labels = set()
    for pattern, icon, label in BH_AMENITY_MAP:
        if _re.search(pattern, combined, _re.I) and label not in seen_labels:
            found.append({"label": label, "icon": icon})
            seen_labels.add(label)

    # Always add standard apartment amenities if we found very few
    if len(found) < 4:
        for _, icon, label in BH_AMENITY_MAP[:8]:
            if label not in seen_labels:
                found.append({"label": label, "icon": icon})
                seen_labels.add(label)
                if len(found) >= 9: break

    return found[:12]

def is_floorplan(path):
    """Detect floor plan images by low pixel variance (black lines on white)."""
    try:
        from PIL import Image
        img = Image.open(path).convert('RGB')
        r_vals = [p[0] for p in list(img.getdata())[::20]]
        return statistics.stdev(r_vals) < 30
    except:
        return False

JSON_FILE  = Path("bh_atlanta.json")
HTML_FILE  = Path("index.html")
INTERIORS  = Path("progress/images/interior-photos")

MAP_POS = [
    {"x":26,"y":22},{"x":30,"y":18},{"x":72,"y":24},{"x":74,"y":20},
    {"x":52,"y":16},{"x":28,"y":74},{"x":22,"y":46},{"x":55,"y":13},
    {"x":68,"y":34},{"x":42,"y":38},{"x":60,"y":28},{"x":35,"y":52},
    {"x":48,"y":42},{"x":65,"y":48},{"x":38,"y":60},{"x":50,"y":30},
    {"x":58,"y":56},{"x":44,"y":66},{"x":32,"y":36},{"x":70,"y":40},
]

import math
def latlng(idx):
    return [
        round(33.749 + math.sin(idx * 1.3) * 0.28, 4),
        round(-84.388 + math.cos(idx * 1.1) * 0.38, 4),
    ]

def slug(s, idx):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:40] + f"-{idx}"

def convert(raw, idx):
    name    = raw.get("name") or raw.get("address") or "BH Property"
    address = raw.get("address") or ""
    city    = raw.get("city_state") or "Atlanta, GA"
    street  = address.split(",")[0].strip() if address else name
    price   = raw.get("price") or 0
    beds    = raw.get("bedrooms_min") or raw.get("bedrooms") or 1
    baths   = raw.get("bathrooms_min") or raw.get("bathrooms") or 1
    sqft    = raw.get("sqft_min") or raw.get("sqft") or 800
    pos     = MAP_POS[idx % len(MAP_POS)]
    amenities = raw.get("amenities") or []

    # Split downloaded images into real photos vs floor plans
    all_imgs = [p for p in (raw.get("local_images") or []) if os.path.exists(p)]
    exterior = raw.get("local_image") or ""
    if not all_imgs and exterior and os.path.exists(exterior):
        all_imgs = [exterior]

    photos     = [p for p in all_imgs if not is_floorplan(p)]
    floorplans = [p for p in all_imgs if is_floorplan(p)]

    # Append shared interior photos to the real photos gallery
    interior_photos = sorted(
        str(p) for p in INTERIORS.glob("*")
        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
    ) if INTERIORS.exists() else []
    gallery = photos + interior_photos

    price_str = f"${price:,}/mo" if price else raw.get("price_text", "Contact for pricing")
    beds_label = f"{beds}–{raw.get('bedrooms_max', beds)}" if raw.get("bedrooms_max", beds) != beds else str(beds)
    sqft_label = f"{sqft:,}–{raw.get('sqft_max', sqft):,}" if raw.get("sqft_max", sqft) != sqft else f"{sqft:,}"

    blurb = (
        f"{name} is a modern residential community in {city.split(',')[0].strip()} "
        f"offering {beds_label}-bedroom apartments starting at {price_str}. "
        f"Featuring {sqft_label} sq ft of thoughtfully designed living space, "
        f"residents enjoy premium amenities and a convenient Atlanta location. "
        f"Flexible lease terms available."
    )

    return {
        "id":       slug(name, idx),
        "title":    street,
        "street":   street,
        "city":     city,
        "name":     name,
        "price":    price,
        "beds":     beds,
        "baths":    baths,
        "sqft":     sqft,
        "type":     "Apartment",
        "status":   raw.get("availability") or "Available Now",
        "isNew":    False,
        "pos":      pos,
        "latlng":   latlng(idx),
        "img":       gallery[0] if gallery else "",
        "gallery":   gallery[:10],
        "floorplans": floorplans,
        "starting": price,
        "aiWhy":    None,
        "desired":  {},
        "inhome":   amenities[:10],
        "community": [],
        "blurb":    blurb,
        "sourceUrl":  raw.get("url", ""),
        "price_text": price_str,
        "unit_types": raw.get("unit_types", []),
        "amenities":  _derive_amenities(raw),
    }

def main():
    if not JSON_FILE.exists():
        print(f"ERROR: {JSON_FILE} not found — run scrape_bh.py first.")
        return

    raw = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    print(f"Read {len(raw)} BH listings")

    # Deduplicate by name
    seen, unique = set(), []
    for r in raw:
        key = (r.get("name") or r.get("address") or "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(r)
    print(f"After dedup: {len(unique)} unique properties")

    converted = [convert(r, i) for i, r in enumerate(unique)]

    html = HTML_FILE.read_text(encoding="utf-8")

    # Build JS block
    js_block = "window.BH = window.BH || {};\nwindow.BH.LISTINGS = " + json.dumps(converted, indent=2) + ";"

    # Replace existing BH block or insert before the first <script type="text/babel">
    if "window.BH.LISTINGS" in html:
        _block = js_block  # capture for lambda
        html = re.sub(
            r"window\.BH\s*=.*?window\.BH\.LISTINGS\s*=\s*\[.*?\];",
            lambda m: _block,
            html,
            count=1,
            flags=re.DOTALL
        )
        print("Updated existing window.BH.LISTINGS block")
    else:
        # Insert into the plain <script> block that has window.PR
        insert_marker = "window.PR.LISTINGS = ["
        insert_pos = html.find(insert_marker)
        if insert_pos > -1:
            html = html[:insert_pos] + js_block + "\n\n" + html[insert_pos:]
            print("Inserted window.BH.LISTINGS before window.PR.LISTINGS")
        else:
            # Fallback: insert before first babel script
            marker = '<script type="text/babel">'
            pos = html.find(marker)
            if pos > -1:
                html = html[:pos] + f"<script>\n{js_block}\n</script>\n\n" + html[pos:]
                print("Inserted as new <script> block")

    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"Injected {len(converted)} BH listings into index.html")
    print("\nDone — hard refresh your browser (Cmd+Shift+R)")

if __name__ == "__main__":
    main()
