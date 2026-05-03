# scraper.py
from playwright.sync_api import sync_playwright
import time
import re

class GoogleMapsScraper:
    def __init__(self, location, profile_path=None, headless=False):
        self.location = location
        self.profile_path = profile_path
        self.headless = headless
        self.all_results = []
    
    def scrape_multiple_queries(self, search_queries):
        with sync_playwright() as p:
            if self.profile_path:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_path,
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ],
                    accept_downloads=False,
                    ignore_https_errors=True
                )
                page = context.pages[0] if context.pages else context.new_page()
            else:
                browser = p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                context = browser.new_context()
                page = context.new_page()

            # First visit - handle consent
            page.goto("https://www.google.com/maps", timeout=30000)
            time.sleep(3)
            self._handle_consent(page)

            for idx, query in enumerate(search_queries, 1):
                print(f"\n🔍 [{idx}/{len(search_queries)}] Searching: {query}")
                try:
                    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}+in+{self.location.replace(' ', '+')}"
                    page.goto(url, timeout=30000)
                    time.sleep(3)
                    self._handle_consent(page)
                    self._scroll_results(page)

                    cards = page.query_selector_all('div[role="article"]')
                    print(f"   Found {len(cards)} business cards")

                    query_results = []
                    for card in cards[:25]:
                        try:
                            data = self._extract_business_data(card, page, query)
                            if data and data['rating_count'] >= 20:
                                query_results.append(data)
                        except:
                            continue

                    print(f"   ✅ {len(query_results)} businesses with 20+ reviews")
                    self.all_results.extend(query_results)
                    time.sleep(2)

                except Exception as e:
                    print(f"   ❌ Error on '{query}': {e}")
                    continue

            print(f"\n📊 Total: {len(self.all_results)} businesses found")
            context.close()

        return self.all_results

    def _handle_consent(self, page):
        try:
            time.sleep(2)
            selectors = [
                'button:has-text("Accept all")',
                'button:has-text("Accept")',
                'button:has-text("I agree")',
                'button:has-text("Reject all")',
                '[aria-label*="Accept"]',
                '[aria-label*="Agree"]',
                'button[jsname="b3VHJd"]',
                'button.VfPpkd-LgbsSe'
            ]
            for selector in selectors:
                try:
                    btn = page.query_selector(selector)
                    if btn and btn.is_visible():
                        btn.click()
                        time.sleep(2)
                        return
                except:
                    continue
        except:
            pass

    def _scroll_results(self, page):
        try:
            feed_selectors = [
                'div[role="feed"]',
                'div.m6QErb',
                '[aria-label*="Results"]'
            ]
            selector_used = None
            for selector in feed_selectors:
                if page.query_selector(selector):
                    selector_used = selector
                    break

            if selector_used:
                for _ in range(5):
                    page.evaluate(f'''
                        const el = document.querySelector('{selector_used}');
                        if (el) el.scrollTop = el.scrollHeight;
                    ''')
                    time.sleep(1.5)
            else:
                for _ in range(5):
                    page.evaluate('window.scrollBy(0, 3000)')
                    time.sleep(1.5)
        except:
            pass

    def _extract_business_data(self, card, page, category):
        try:
            card.click()
            time.sleep(2.5)

            # ── Name ──────────────────────────────────────────────
            name = "N/A"
            for sel in ['h1.DUwDvf', 'h1', '[class*="fontHeadline"]']:
                elem = page.query_selector(sel)
                if elem:
                    text = elem.inner_text().strip()
                    if text and text != "Results":
                        name = text
                        break

            # ── Rating ────────────────────────────────────────────
            rating = "0"
            for sel in [
                'div.F7nice span[aria-hidden="true"]',
                'span.ceNzKf',
                'span[aria-label*="stars"]'
            ]:
                elem = page.query_selector(sel)
                if elem:
                    try:
                        text = elem.inner_text().strip()
                        if text and text.replace('.', '').isdigit():
                            rating = text
                            break
                    except:
                        continue

            # ── Rating Count ──────────────────────────────────────
            rating_count = 0

            # Method 1: known selectors with aria-label
            for sel in [
                'div.F7nice span[aria-label*="reviews"]',
                'button[aria-label*="reviews"]',
                'span[aria-label*="reviews"]',
                'button[aria-label*="Reviews"]',
                'span[aria-label*="Reviews"]'
            ]:
                elem = page.query_selector(sel)
                if elem:
                    try:
                        aria = elem.get_attribute('aria-label') or ''
                        text = elem.inner_text().strip()
                        combined = aria + ' ' + text
                        digits = re.sub(r'[^\d]', '', combined.split()[0] if combined else '')
                        if not digits:
                            match = re.search(r'[\d,]+', combined)
                            if match:
                                digits = match.group().replace(',', '')
                        if digits:
                            rating_count = int(digits)
                            break
                    except:
                        continue

            # Method 2: parse F7nice container text for (N) pattern
            if rating_count == 0:
                try:
                    container = page.query_selector('div.F7nice')
                    if container:
                        text = container.inner_text()
                        match = re.search(r'\(([\d,]+)\)', text)
                        if match:
                            rating_count = int(match.group(1).replace(',', ''))
                except:
                    pass

            # Method 3: JavaScript scan all aria-labels
            if rating_count == 0:
                try:
                    rating_count = page.evaluate(r'''
                        () => {
                            const candidates = [
                                'div.F7nice span[aria-label*="reviews"]',
                                'button[aria-label*="reviews"]',
                                'span[aria-label*="reviews"]',
                                '[aria-label*="review"]'
                            ];
                            for (const sel of candidates) {
                                const el = document.querySelector(sel);
                                if (el) {
                                    const aria = el.getAttribute("aria-label") || "";
                                    const text = el.innerText || "";
                                    const match = (aria + " " + text).match(/[\d,]+/);
                                    if (match) return parseInt(match[0].replace(/,/g, ""));
                                }
                            }
                            // Scan every span for review aria-label
                            for (const el of document.querySelectorAll("span")) {
                                const aria = el.getAttribute("aria-label") || "";
                                if (aria.toLowerCase().includes("review")) {
                                    const match = aria.match(/[\d,]+/);
                                    if (match) return parseInt(match[0].replace(/,/g, ""));
                                }
                            }
                            return 0;
                        }
                    ''') or 0
                except:
                    pass

            # ── Address ───────────────────────────────────────────
            address = "N/A"
            for sel in [
                'button[data-item-id="address"]',
                'button[aria-label*="Address"]',
                'button[data-tooltip="Copy address"]'
            ]:
                elem = page.query_selector(sel)
                if elem:
                    try:
                        text = elem.inner_text().strip()
                        if text and len(text) > 3:
                            address = text
                            break
                    except:
                        continue

            # ── Phone ─────────────────────────────────────────────
            phone = "N/A"
            for sel in [
                'button[data-item-id*="phone"]',
                'button[aria-label*="Phone"]',
                'button[data-tooltip="Copy phone number"]',
                'a[href^="tel:"]'
            ]:
                elem = page.query_selector(sel)
                if elem:
                    try:
                        text = elem.inner_text().strip()
                        if text and text != "N/A":
                            phone = text
                            break
                        href = elem.get_attribute('href') or ''
                        if href.startswith('tel:'):
                            phone = href.replace('tel:', '').strip()
                            break
                    except:
                        continue

            # ── Website ───────────────────────────────────────────
            website_url = None
            has_website = False
            for sel in [
                'a[data-item-id="authority"]',
                'a[aria-label*="Website"]',
                'a[data-tooltip="Open website"]'
            ]:
                elem = page.query_selector(sel)
                if elem:
                    try:
                        href = elem.get_attribute('href') or ''
                        if href and 'google.com/maps' not in href:
                            website_url = href
                            has_website = True
                            break
                    except:
                        continue

            # ── Email ─────────────────────────────────────────────
            email = self._find_email(page)

            return {
                'name': name,
                'rating': rating,
                'rating_count': rating_count,
                'address': address,
                'phone': phone,
                'website': website_url,
                'has_website': has_website,
                'email': email,
                'category': category
            }

        except:
            return None

    def _find_email(self, page):
        try:
            content = page.content()
            pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(pattern, content)
            excluded = ['google', 'schema.org', 'w3.org', 'gstatic', 'googleapis']
            valid = [e for e in emails if not any(x in e.lower() for x in excluded)]
            return valid[0] if valid else "Not found"
        except:
            return "Not found"
