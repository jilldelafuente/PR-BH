"""
scrape_bh_units.py — Scrapes unit-type data (floor plans, pricing, availability)
from each livebh.com property page and merges into bh_atlanta.json.

Run:
    python3 scrape_bh_units.py
Then:
    python3 inject_bh.py
"""

import json, re, time, requests, warnings
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from requests.packages.urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

JSON_FILE  = Path("bh_atlanta.json")
IMAGES_DIR = Path("images/bh")

DL = requests.Session()
DL.verify = False
DL.headers["User-Agent"] = "Mozilla/5.0"
DL.headers["Referer"] = "https://livebh.com/"

def clean(t): return " ".join((t or "").split()).strip()

def parse_price(t):
    nums = re.findall(r"[\d,]+", (t or "").replace(",",""))
    vals = [int(n) for n in nums if int(n) > 500]
    return (vals[0], vals[-1]) if len(vals) >= 2 else (vals[0], vals[0]) if vals else (0, 0)

def parse_sqft(t):
    m = re.search(r"([\d,]+)\s*sq", t or "", re.I)
    return int(m.group(1).replace(",","")) if m else 0

def parse_avail(t):
    m = re.search(r"(\d+\+?)\s*available", t or "", re.I)
    return m.group(1) if m else "0"

def download_fp_image(url, dest):
    if dest.exists() and dest.stat().st_size > 2000:
        return str(dest)
    try:
        r = DL.get(url, timeout=15)
        if r.ok and len(r.content) > 2000:
            dest.write_bytes(r.content)
            return str(dest)
    except: pass
    return ""

def scrape_unit_types(page, listing_idx):
    """Extract all floor plan / unit type data from current page."""
    unit_types = []
    slides = page.query_selector_all(".floorplan-slide")

    for i, slide in enumerate(slides):
        text = clean(slide.inner_text())

        # Price lives in a child element, get all child text
        all_child_text = " ".join(
            clean(c.inner_text()) for c in slide.query_selector_all("*")
        )

        img_el = slide.query_selector("img")
        img_url = img_el.get_attribute("src") if img_el else ""

        # Parse fields — use all_child_text for price, text for beds/avail
        bd_m    = re.search(r"(\d+)\s*Bed", text, re.I)
        ba_m    = re.search(r"(\d+(?:\.\d)?)\s*Bath", text, re.I)
        price_m = re.search(r"\$([\d,]+)\s*[-–]\s*\$([\d,]+)", all_child_text)
        avail   = parse_avail(text)

        # Sqft: parse from image URL filename (e.g. "...1x1 708 ...")
        sqft = 0
        if img_url:
            sqft_m = re.search(r"\b(\d{3,4})\b(?=\s|$|[^0-9])", img_url.split("/")[-1])
            if sqft_m:
                sqft = int(sqft_m.group(1))
        if not sqft:
            sqft = parse_sqft(all_child_text)

        beds  = int(bd_m.group(1)) if bd_m else 0
        baths = float(ba_m.group(1)) if ba_m else 0
        price_min = int(price_m.group(1).replace(",","")) if price_m else 0
        price_max = int(price_m.group(2).replace(",","")) if price_m else price_min

        # Unit type label
        label = f"{beds}×{int(baths)}" if beds and baths else "Studio"

        # Download floor plan image
        fp_local = ""
        if img_url:
            ext = ".jpg" if img_url.lower().endswith((".jpg","jpeg")) else ".png"
            fp_dest = IMAGES_DIR / f"listing-{listing_idx:04d}" / f"fp-{i:02d}{ext}"
            fp_dest.parent.mkdir(exist_ok=True)
            fp_local = download_fp_image(img_url, fp_dest)

        unit_types.append({
            "label":      label,
            "beds":       beds,
            "baths":      baths,
            "sqft":       sqft,
            "price_min":  price_min,
            "price_max":  price_max,
            "available":  avail,
            "fp_image":   fp_local or img_url,
            "fp_image_url": img_url,
        })

    # Deduplicate by label+sqft (same floor plan may appear multiple times)
    seen = set()
    unique = []
    for ut in unit_types:
        key = f"{ut['label']}-{ut['sqft']}"
        if key not in seen:
            seen.add(key)
            unique.append(ut)

    return unique


def main():
    data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(data)} listings\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = ctx.new_page()

        for idx, listing in enumerate(data):
            url = listing.get("url","")
            if not url:
                continue
            print(f"[{idx+1}/{len(data)}] {listing.get('name','?')}")
            try:
                page.goto(url, wait_until="networkidle", timeout=25000)
                page.wait_for_timeout(1500)
            except Exception as e:
                print(f"  Error: {e}")
                continue

            unit_types = scrape_unit_types(page, idx)
            listing["unit_types"] = unit_types

            # Update price from unit types
            prices = [ut["price_min"] for ut in unit_types if ut["price_min"] > 0]
            if prices:
                listing["price"]     = min(prices)
                listing["price_max"] = max(ut["price_max"] for ut in unit_types if ut["price_max"] > 0)
                listing["price_text"] = f"${min(prices):,} – ${max(ut['price_max'] for ut in unit_types if ut['price_max'] > 0):,}/mo"

            beds_all  = [ut["beds"] for ut in unit_types if ut["beds"]]
            baths_all = [ut["baths"] for ut in unit_types if ut["baths"]]
            sqft_all  = [ut["sqft"] for ut in unit_types if ut["sqft"]]
            if beds_all:
                listing["bedrooms_min"] = min(beds_all)
                listing["bedrooms_max"] = max(beds_all)
            if baths_all:
                listing["bathrooms_min"] = min(baths_all)
                listing["bathrooms_max"] = max(baths_all)
            if sqft_all:
                listing["sqft_min"] = min(sqft_all)
                listing["sqft_max"] = max(sqft_all)

            print(f"  ✓ {len(unit_types)} unit types | {listing.get('price_text','')}")
            for ut in unit_types:
                print(f"    {ut['label']} {ut['beds']}bd/{ut['baths']}ba {ut['sqft']}sqft "
                      f"${ut['price_min']:,}–${ut['price_max']:,} ({ut['available']} avail)")
            time.sleep(0.8)

        browser.close()

    JSON_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n✓ Updated {JSON_FILE} with unit type data")
    print("Next: python3 inject_bh.py")


if __name__ == "__main__":
    main()
