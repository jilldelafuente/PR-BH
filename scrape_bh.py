"""
scrape_bh.py — Scrapes Atlanta-area listings from livebh.com using Playwright.
Outputs: bh_atlanta.json + images/bh/listing-XXXX/ folders

Run:
    python3 scrape_bh.py
Then:
    python3 inject_bh.py
"""

import json, re, time, requests, warnings
from pathlib import Path
from playwright.sync_api import sync_playwright
from requests.packages.urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

SEARCH_URL  = "https://livebh.com/apartment-search/?search=Atlanta%2C+GA"
BASE        = "https://livebh.com"
OUTPUT_JSON = "bh_atlanta.json"
IMAGES_DIR  = Path("images/bh")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

DL = requests.Session()
DL.verify = False
DL.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
DL.headers["Referer"] = "https://livebh.com/"


def clean(t): return " ".join((t or "").split()).strip()

def parse_price(t):
    m = re.search(r"[\d,]+", (t or "").replace(",", ""))
    return int(m.group()) if m else 0

def ext_from_url(url):
    m = re.search(r"\.(webp|png|jpeg|jpg)(\?|$)", url, re.I)
    return "." + m.group(1).lower() if m else ".jpg"

def download(url, dest):
    if dest.exists() and dest.stat().st_size > 3000:
        return True
    if not url or re.search(r"logo|icon|svg|pixel|placeholder|favicon|font", url, re.I):
        return False
    try:
        r = DL.get(url, timeout=15)
        if r.ok and len(r.content) > 3000:
            dest.write_bytes(r.content)
            return True
    except Exception as e:
        print(f"    ✗ {e}")
    return False


def scrape_detail_page(page, url, idx):
    """Visit an individual property page and scrape full details + photos."""
    print(f"  Loading: {url}")
    try:
        page.goto(url, wait_until="networkidle", timeout=25000)
        page.wait_for_timeout(1500)
    except Exception as e:
        print(f"  Timeout: {e}")
        return {}

    prop = {"url": url}
    content = page.content()
    text = page.inner_text("body")

    # Property name
    for sel in ["h1", ".property-name", ".community-name", ".et_pb_text h1"]:
        el = page.query_selector(sel)
        if el:
            t = clean(el.inner_text())
            if t and len(t) < 80:
                prop["name"] = t
                break

    # Address
    for sel in [".property-address", "[class*='address']", "[itemprop='streetAddress']"]:
        el = page.query_selector(sel)
        if el:
            prop["address"] = clean(el.inner_text())
            break
    if not prop.get("address"):
        m = re.search(r"\d+\s+[\w\s]+(?:Rd|Dr|Ln|Blvd|Ave|St|Way|Ct|Pl|Pkwy)[^\n]{0,40}", text)
        if m: prop["address"] = clean(m.group())

    # City / state
    if prop.get("address"):
        parts = prop["address"].split(",")
        if len(parts) >= 2:
            prop["city_state"] = ", ".join(p.strip() for p in parts[1:3])

    # Price
    for sel in [".property-price", "[class*='price']", "[class*='rent']", "[class*='starting']"]:
        el = page.query_selector(sel)
        if el:
            t = clean(el.inner_text())
            if re.search(r"\$|\d", t):
                prop["price_text"] = t
                prop["price"] = parse_price(t)
                break
    if not prop.get("price"):
        m = re.search(r"[Ss]tarting at\s*\$?([\d,]+)|From\s*\$?([\d,]+)|\$([\d,]+)\s*/?mo", text)
        if m:
            val = next(v for v in m.groups() if v)
            prop["price"] = parse_price(val)
            prop["price_text"] = f"Starting at ${val}"

    # Beds / baths / sqft
    beds, baths, sqft = [], [], []
    for m in re.finditer(r"(\d+)\s*(?:Bed|bed|BR|Bedroom)", text): beds.append(int(m.group(1)))
    for m in re.finditer(r"(\d+(?:\.\d)?)\s*(?:Bath|bath|BA)", text): baths.append(float(m.group(1)))
    for m in re.finditer(r"([\d,]+)\s*(?:sq\.?\s?ft|sqft)", text): sqft.append(int(m.group(1).replace(",","")))

    if beds:  prop["bedrooms_min"] = min(beds); prop["bedrooms_max"] = max(beds)
    if baths: prop["bathrooms_min"] = min(baths); prop["bathrooms_max"] = max(baths)
    if sqft:  prop["sqft_min"] = min(sqft); prop["sqft_max"] = max(sqft)

    # Availability
    m = re.search(r"(\d+\+?)\s+(?:unit|apartment)s?\s+available", text, re.I)
    if m: prop["availability"] = f"{m.group(1)} units available"
    elif re.search(r"available now|move.in ready", text, re.I):
        prop["availability"] = "Available Now"

    # Amenities
    amenities = []
    for sel in [".amenity", "[class*='amenity']", "[class*='feature'] li",
                ".et_pb_blurb_description", "ul li"]:
        for el in page.query_selector_all(sel):
            t = clean(el.inner_text())
            if 3 < len(t) < 50 and t not in amenities:
                amenities.append(t)
    prop["amenities"] = amenities[:12]

    # Images — collect all candidate sources
    img_urls = []
    seen = set()

    # img tags
    for img in page.query_selector_all("img[src]"):
        src = img.get_attribute("src") or ""
        if (src and src not in seen
                and not src.startswith("data:")
                and not src.endswith(".svg")
                and not re.search(r"logo|icon|pixel|avatar|map|floor|spinner|blank", src, re.I)
                and re.search(r"\.(jpe?g|png|webp)", src, re.I)):
            img_urls.append(src if src.startswith("http") else BASE + src)
            seen.add(src)

    # background-image styles
    for m in re.finditer(r'url\(["\']?([^)"\']+\.(?:jpe?g|png|webp)[^)"\']*)["\']?\)', content, re.I):
        src = m.group(1)
        if src not in seen and not re.search(r"logo|icon|gradient|sprite", src, re.I):
            img_urls.append(src if src.startswith("http") else BASE + src)
            seen.add(src)

    # Download
    folder = IMAGES_DIR / f"listing-{idx:04d}"
    folder.mkdir(exist_ok=True)
    local = []
    for i, url in enumerate(img_urls[:15]):
        dest = folder / f"photo-{i:02d}{ext_from_url(url)}"
        if download(url, dest):
            local.append(str(dest))

    if local:
        prop["image_url"]    = local[0]
        prop["local_image"]  = local[0]
        prop["local_images"] = local

    print(f"  ✓ {prop.get('name','?')} | {prop.get('city_state','?')} | "
          f"${prop.get('price',0):,} | {len(local)} photos")
    return prop


def main():
    all_listings = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )

        # ── Step 1: Get all property URLs from the search page ──
        print("Step 1: Loading search results...")
        search_page = ctx.new_page()
        search_page.goto(SEARCH_URL, wait_until="networkidle", timeout=30000)
        search_page.wait_for_timeout(3000)

        # Get slugs from rendered page content
        content = search_page.content()
        slugs = list(dict.fromkeys(re.findall(r'/apartments/([\w-]+)/', content)))
        print(f"  Found {len(slugs)} property slugs: {slugs}")

        # Also collect any price/availability from the search card
        card_data = {}
        for card in search_page.query_selector_all(".property-card-wrapper"):
            card_text = clean(card.inner_text())
            # Try to find the slug via the card's link
            a = card.query_selector("a[href*='/apartments/']")
            if a:
                href = a.get_attribute("href") or ""
                m = re.search(r"/apartments/([\w-]+)/", href)
                if m:
                    slug = m.group(1)
                    card_data[slug] = {"card_text": card_text}

        search_page.close()

        if not slugs:
            print("No slugs found — check the site structure")
            return

        # ── Step 2: Visit each property detail page ──
        print(f"\nStep 2: Scraping {len(slugs)} property pages...\n")
        detail_page = ctx.new_page()

        for idx, slug in enumerate(slugs):
            url = f"{BASE}/apartments/{slug}/"
            print(f"[{idx+1}/{len(slugs)}] {slug}")
            prop = scrape_detail_page(detail_page, url, idx)
            if prop and (prop.get("name") or prop.get("address")):
                # Merge any card data
                if slug in card_data:
                    prop.setdefault("card_text", card_data[slug]["card_text"])
                all_listings.append(prop)
            time.sleep(1.0)

        detail_page.close()
        browser.close()

    Path(OUTPUT_JSON).write_text(
        json.dumps(all_listings, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n✓ Saved {len(all_listings)} listings → {OUTPUT_JSON}")
    print("Next: python3 inject_bh.py")


if __name__ == "__main__":
    main()
