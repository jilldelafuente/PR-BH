# Web Scraping Guide — Pulling Real Content & Visuals into Prototypes

A reusable reference for scraping any website to populate a prototype with
accurate, real-world content — product listings, articles, profiles, menus,
events, properties, or anything else displayed on a public webpage.

---

## When to Use This Approach

Use this when your prototype needs real data instead of lorem ipsum:
- Accurate names, titles, prices, descriptions, dates
- Real images tied to specific items
- Live status or availability information
- Any structured content that already exists on a public site

---

## Step 1 — Identify How the Site Renders Its Content

Before writing any code, determine how the site serves its content.

**Test:** Open the page in your browser, right-click → **View Page Source**.
Search for a piece of text you can see on screen (a product name, headline, price).

| Result | Site type | What it means |
|---|---|---|
| Text found in source | Server-rendered | Simple — `requests` + BeautifulSoup works |
| Text NOT in source | JavaScript-rendered | Requires a real browser (Playwright) |

**Examples by type:**

| Server-rendered (simple) | JavaScript-rendered (needs Playwright) |
|---|---|
| Wikipedia, news articles, blogs | Zillow, Airbnb, LinkedIn, most React/Vue apps |
| Government sites, documentation | Instagram, Twitter/X, product catalogs |
| Most e-commerce product pages | Single-page apps, dashboards |

When in doubt, assume JavaScript-rendered. Most modern sites are.

---

## Step 2 — Look for a Hidden JSON API First

Many sites load their data via API calls in the background. If you find one,
you get clean structured data without any HTML parsing.

**How to find it:**
1. Open Chrome DevTools (`Cmd+Option+I`) → **Network** tab
2. Filter by **Fetch/XHR**
3. Reload the page and interact with it (scroll, search, click filters)
4. Look for requests that return JSON containing the content you want

**What to look for in the URL:**
```
/api/...
/graphql
/_next/data/...        (Next.js sites)
/wp-json/...           (WordPress sites)
/__data.json           (SvelteKit sites)
```

If you find a JSON API, you can call it directly with `requests` — no browser needed.
Share the API URL with Claude and it can write the exact request for you.

---

## Step 3 — Environment Setup

```bash
# Install Python dependencies
python3 -m pip install playwright beautifulsoup4 requests

# Install the headless browser
# On corporate networks with SSL inspection (e.g. Bounteous), prefix with:
NODE_TLS_REJECT_UNAUTHORIZED=0 python3 -m playwright install chromium
```

This is a one-time setup per machine.

---

## Step 4 — Inspect the Page Structure

Before writing code, spend 2 minutes inspecting the page:

1. Right-click on one content item → **Inspect**
2. Find the outermost element that wraps a single item (one card, one article, one product)
3. Look for a repeating CSS class — that's your **card selector**
4. Drill into it and note the classes for each piece of data you want

**What to look for:**

| Data type | Typical HTML patterns |
|---|---|
| Title / name | `h1`, `h2`, `h3`, `[class*='title']`, `[class*='name']` |
| Price | `[class*='price']`, `[class*='cost']`, `[class*='amount']` |
| Description | `[class*='description']`, `[class*='summary']`, `p` |
| Date | `time[datetime]`, `[class*='date']`, `[class*='time']` |
| Image | `img[src]`, `img[data-src]` (lazy-loaded), `[style*='background']` |
| Category / tag | `[class*='tag']`, `[class*='badge']`, `[class*='category']` |
| Status | `[class*='status']`, `[class*='badge']`, `[class*='label']` |
| Author / byline | `[class*='author']`, `[class*='byline']`, `[rel='author']` |
| Rating | `[class*='rating']`, `[class*='stars']`, `[aria-label*='star']` |
| Link | `a[href]` — the closest anchor to the card |

If class names look random (e.g. `css-1x7ujm2`), look for `data-testid`,
`data-id`, `aria-label`, or semantic HTML tags (`article`, `section`, `li`)
as alternative selectors.

---

## Step 5 — The Scraper Template

Copy this and adapt the three variables at the top for any site.

```python
"""
Generic web scraper for prototype content.
Adapt BASE_URL, CARD_SELECTOR, and the field mappings in scrape_card().

Requirements:
    python3 -m pip install playwright beautifulsoup4
    NODE_TLS_REJECT_UNAUTHORIZED=0 python3 -m playwright install chromium
"""

import json, re, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# ── Configure these three things ──────────────────────────────────────────────
BASE_URL      = "https://TARGET-SITE.com/section?page={page}"  # use {page} for pagination
CARD_SELECTOR = "[class*='card']"   # the repeating element wrapping one content item
OUTPUT_FILE   = "scraped_content.json"
MAX_PAGES     = 10
# ──────────────────────────────────────────────────────────────────────────────


def scrape_card(card_html):
    """Extract fields from one content card. Add/remove fields as needed."""
    soup = BeautifulSoup(card_html, "html.parser")
    item = {}

    # Title / name
    for sel in ["h1","h2","h3","[class*='title']","[class*='name']"]:
        el = soup.select_one(sel)
        if el:
            item["title"] = el.get_text(strip=True)
            break

    # Price (strips symbols, extracts number)
    for sel in ["[class*='price']","[class*='cost']","[class*='amount']"]:
        el = soup.select_one(sel)
        if el:
            item["price_text"] = el.get_text(strip=True)
            m = re.search(r"[\d,\.]+", item["price_text"].replace(",",""))
            if m: item["price"] = float(m.group())
            break

    # Description
    for sel in ["[class*='description']","[class*='summary']","[class*='excerpt']","p"]:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(strip=True)
            if len(text) > 20:   # skip very short fragments
                item["description"] = text
                break

    # Date
    el = soup.select_one("time[datetime]")
    if el:
        item["date"] = el.get("datetime") or el.get_text(strip=True)
    else:
        for sel in ["[class*='date']","[class*='time']","[class*='published']"]:
            el = soup.select_one(sel)
            if el:
                item["date"] = el.get_text(strip=True)
                break

    # Category / tag
    for sel in ["[class*='category']","[class*='tag']","[class*='badge']","[class*='label']"]:
        el = soup.select_one(sel)
        if el:
            item["category"] = el.get_text(strip=True)
            break

    # Status
    for sel in ["[class*='status']","[class*='availability']","[class*='stock']"]:
        el = soup.select_one(sel)
        if el:
            item["status"] = el.get_text(strip=True)
            break

    # Image — skip icons, SVGs, tracking pixels
    for img in soup.select("img[src],img[data-src]"):
        src = img.get("src") or img.get("data-src","")
        if (src
            and not src.startswith("data:")
            and not src.endswith(".svg")
            and not re.search(r"logo|icon|pixel|avatar|placeholder|spinner", src, re.I)
            and len(src) > 10):
            item["image_url"] = src
            break

    # Link to detail page
    a = soup.select_one("a[href]")
    if a:
        href = a["href"]
        # Make relative URLs absolute — replace 'example.com' with the real domain
        item["url"] = href if href.startswith("http") else f"https://example.com{href}"

    return item


def scrape():
    all_items = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_context(
            ignore_https_errors=True,      # handles corporate SSL inspection
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        ).new_page()

        for page_num in range(1, MAX_PAGES + 1):
            url = BASE_URL.format(page=page_num)
            print(f"\nPage {page_num}: {url}")

            try:
                page.goto(url, wait_until="networkidle", timeout=30_000)
            except Exception as e:
                print(f"  Failed to load: {e}")
                continue

            # Check for empty / no-results page
            body_text = page.inner_text("body")
            if re.search(r"no results|nothing found|0 results|page not found", body_text, re.I):
                print("  No results — stopping")
                break

            # Find cards
            try:
                page.wait_for_selector(CARD_SELECTOR, timeout=8_000)
            except Exception:
                pass

            cards = page.locator(CARD_SELECTOR)
            count = cards.count()

            if count == 0:
                print(f"  No cards found with selector: {CARD_SELECTOR}")
                print(f"  Saving debug_page_{page_num}.html for inspection")
                Path(f"debug_page_{page_num}.html").write_text(page.content(), encoding="utf-8")
                break

            for i in range(count):
                item = scrape_card(cards.nth(i).inner_html())
                if any(item.values()):   # skip completely empty results
                    all_items.append(item)

            print(f"  Found {count} items | Total so far: {len(all_items)}")
            time.sleep(1.0)   # polite delay between pages

        browser.close()

    return all_items


if __name__ == "__main__":
    items = scrape()

    # Deduplicate by title (change key field as needed)
    seen, unique = set(), []
    for item in items:
        key = (item.get("title") or item.get("url") or "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(item)

    print(f"\n{len(items)} total → {len(unique)} unique after deduplication")

    Path(OUTPUT_FILE).write_text(json.dumps(unique, indent=2, ensure_ascii=False))
    print(f"Saved → {OUTPUT_FILE}")
```

---

## Step 6 — Download Images Locally

Always download images during the scrape — not after.
Images are removed from CDNs when content is deleted, archived, or sold.

```python
import requests, re
from pathlib import Path

session = requests.Session()
session.verify = False   # bypass corporate SSL inspection
session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

def download_images(items, output_dir="images"):
    Path(output_dir).mkdir(exist_ok=True)

    for idx, item in enumerate(items):
        url = item.get("image_url")
        if not url:
            continue

        folder = Path(output_dir) / f"item-{idx:04d}"
        folder.mkdir(exist_ok=True)

        # Determine file extension from URL
        m = re.search(r"\.(jpe?g|png|webp|gif)(\?|$)", url, re.I)
        ext = "." + m.group(1).lower() if m else ".jpg"
        dest = folder / f"image-00{ext}"

        if dest.exists():
            item["local_image"] = str(dest)
            continue

        try:
            r = session.get(url, timeout=15)
            if r.ok and len(r.content) > 3_000:   # skip tiny images/icons
                dest.write_bytes(r.content)
                item["local_image"] = str(dest)
                print(f"  ✓ {dest}")
            else:
                print(f"  ✗ Too small or error: {url[:60]}")
        except Exception as e:
            print(f"  ✗ {e}")
```

---

## Step 7 — Inject into Your Prototype

Once you have a JSON file, bake it directly into `index.html` so the prototype
works as a standalone file — no server, no fetch calls.

```python
import json, re
from pathlib import Path

items = json.loads(Path("scraped_content.json").read_text())
html  = Path("index.html").read_text()

# Replace the existing data variable in your HTML
# Change "window.MY_DATA" to whatever variable name your prototype uses
new_block = "window.MY_DATA = " + json.dumps(items, indent=2) + ";"

html, n = re.subn(
    r"window\.MY_DATA\s*=\s*\[.*?\];",
    new_block,
    html,
    count=1,
    flags=re.DOTALL
)

if n == 0:
    print("WARNING: Variable not found in HTML. Check the variable name.")
else:
    Path("index.html.bak").write_text(Path("index.html").read_text())
    Path("index.html").write_text(html)
    print(f"Injected {len(items)} items into index.html")
```

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Fields are empty | Wrong CSS selectors | Save `debug_page_1.html`, open it, find the real class names |
| Page shows "No results" | JS not done rendering | Increase timeout or add `page.wait_for_selector(CARD_SELECTOR)` |
| Images are tiny icons | Selector too broad | Add minimum size check `len(r.content) > 5000` |
| Images return 404 | Content removed from CDN | Download during scrape, not later |
| `playwright install` fails | Corporate SSL inspection | Use `NODE_TLS_REJECT_UNAUTHORIZED=0` |
| `requests` SSL error | Corporate SSL inspection | Use `session.verify = False` |
| Scraper gets blocked | Bot detection | Add `time.sleep(1)` between pages, use a realistic User-Agent |
| Duplicate items | Content repeats across pages | Deduplicate by title or URL |
| Lazy-loaded images missing | Images load on scroll | Use `img[data-src]` selector instead of `img[src]` |

---

## Debugging When Nothing Works

If the scraper finds cards but all fields are empty, or finds no cards at all:

1. **Save the debug HTML:**
   ```python
   Path("debug.html").write_text(page.content())
   ```
2. **Open it in your browser** — it shows what Playwright actually received
3. **Share it with Claude** — paste the relevant HTML structure and ask:
   *"What selector would match the listing card, and what classes hold the title, price, and image?"*

---

## Making It Repeatable

Structure your project like this:

```
_prototype/
├── index.html              ← your prototype (data injected here)
├── scrape.py               ← the scraper script
├── inject.py               ← the injection script
├── scraped_content.json    ← raw scraped data
├── images/                 ← downloaded images
│   ├── item-0000/image-00.jpg
│   ├── item-0001/image-00.jpg
│   └── ...
├── .gitignore              ← exclude json, py, debug html from GitHub
└── .nojekyll               ← required for GitHub Pages
```

**`.gitignore` template:**
```
scraped_content.json
*.csv
debug_*.html
__pycache__/
*.pyc
scrape.py
inject.py
```

**To refresh data:** run `scrape.py` then `inject.py`
**To publish:** `git add -A && git commit -m "Refresh" && git push`

---

## GitHub Pages Checklist

- [ ] No spaces in folder or file names (`interior photos/` → `interior-photos/`)
- [ ] `.nojekyll` file at the repo root
- [ ] All image paths in HTML are relative (not `localhost` or absolute)
- [ ] Scraper scripts and raw JSON excluded via `.gitignore`
- [ ] Settings → Pages → Source: Deploy from branch → main → / (root)
