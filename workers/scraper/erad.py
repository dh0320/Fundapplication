import httpx
from bs4 import BeautifulSoup
from datetime import date, datetime
import asyncio
import re
import logging

from workers.scraper.base import BaseScraper

logger = logging.getLogger(__name__)


class ERadScraper(BaseScraper):
    """e-Rad public offering list scraper."""

    BASE_URL = "https://www.e-rad.go.jp"

    async def fetch(self) -> list:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "User-Agent": "GrantDraft/1.0 (research-grant-aggregator)",
                "Accept": "text/html",
                "Accept-Language": "ja,en;q=0.9",
            }
            resp = await client.get(
                f"{self.BASE_URL}/offer_list.html",
                headers=headers,
                follow_redirects=True,
            )
            resp.raise_for_status()
            return [resp.text]

    def parse(self, raw_data: list) -> list[dict]:
        html = raw_data[0]
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Strategy 1: Parse table rows
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all(["td", "th"])
                if len(cols) < 3:
                    continue
                item = self._parse_row(cols, row)
                if item:
                    results.append(item)

        # Strategy 2: Try div/dl-based structure
        if not results:
            offer_items = soup.select(".offer-item, .koubo-item, dl.offer, .offerList li, .offer_list li")
            for item_el in offer_items:
                item = self._parse_offer_element(item_el)
                if item:
                    results.append(item)

        # Strategy 3: Look for any links that might be offer details
        if not results:
            links = soup.find_all("a", href=re.compile(r"(offer|koubo|detail)", re.I))
            for link in links:
                text = link.get_text(strip=True)
                if text and len(text) > 10:
                    href = link.get("href", "")
                    results.append({
                        "source": "erad",
                        "source_id": f"erad_{hash(text)}",
                        "title": text,
                        "organization": "e-Rad掲載機関",
                        "category": "research",
                        "summary": None,
                        "target_audience": None,
                        "amount_min": None,
                        "amount_max": None,
                        "application_start": None,
                        "application_deadline": None,
                        "detail_url": f"{self.BASE_URL}{href}" if href and not href.startswith("http") else href,
                        "status": "open",
                        "raw_data": {"html_text": text, "href": href},
                    })

        if not results:
            logger.warning(
                f"[e-Rad] Parse returned 0 results. Page title: {soup.title.string if soup.title else 'N/A'}"
            )
            logger.warning(
                f"[e-Rad] Tables found: {len(tables)}, "
                f"classes: {[t.get('class') for t in tables[:5]]}"
            )
            try:
                with open("/tmp/erad_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)
                logger.warning("[e-Rad] Debug HTML saved to /tmp/erad_debug.html")
            except Exception:
                pass

        logger.info(f"[e-Rad] Parsed {len(results)} records")
        return results

    def _parse_row(self, cols, row) -> dict | None:
        try:
            title_col = cols[1] if len(cols) > 1 else cols[0]
            title = title_col.get_text(strip=True)
            if not title or len(title) < 5:
                return None

            link = title_col.find("a")
            href = link.get("href", "") if link else ""
            source_id = self._extract_source_id(href)

            org = cols[0].get_text(strip=True) if len(cols) > 0 else "不明"

            period_text = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            start_date, end_date = self._parse_period(period_text)

            detail_url = f"{self.BASE_URL}{href}" if href and not href.startswith("http") else href

            return {
                "source": "erad",
                "source_id": f"erad_{source_id}" if source_id else f"erad_{hash(title)}",
                "title": title,
                "organization": org,
                "category": "research",
                "summary": None,
                "target_audience": None,
                "amount_min": None,
                "amount_max": None,
                "application_start": start_date,
                "application_deadline": end_date,
                "detail_url": detail_url,
                "status": self._determine_status_from_date(end_date),
                "raw_data": {"html_text": row.get_text(strip=True), "href": href},
            }
        except Exception as e:
            logger.warning(f"[e-Rad] Row parse failed: {e}")
            return None

    def _parse_offer_element(self, el) -> dict | None:
        try:
            title_el = el.find(["dt", "h3", "h4", "a"])
            if not title_el:
                return None
            title_text = title_el.get_text(strip=True)
            if not title_text or len(title_text) < 5:
                return None

            link = el.find("a")
            href = link.get("href", "") if link else ""

            return {
                "source": "erad",
                "source_id": f"erad_{hash(title_text)}",
                "title": title_text,
                "organization": "e-Rad掲載機関",
                "category": "research",
                "summary": None,
                "target_audience": None,
                "amount_min": None,
                "amount_max": None,
                "application_start": None,
                "application_deadline": None,
                "detail_url": f"{self.BASE_URL}{href}" if href and not href.startswith("http") else href,
                "status": "open",
                "raw_data": {"html_text": el.get_text(strip=True)},
            }
        except Exception:
            return None

    def _extract_source_id(self, href: str) -> str | None:
        match = re.search(r"/(\d+)", href)
        return match.group(1) if match else None

    def _parse_period(self, text: str) -> tuple[date | None, date | None]:
        date_pattern = r"(\d{4})[/\-年](\d{1,2})[/\-月](\d{1,2})"
        matches = re.findall(date_pattern, text)
        dates = []
        for y, m, d in matches:
            try:
                dates.append(date(int(y), int(m), int(d)))
            except ValueError:
                continue
        start = dates[0] if len(dates) > 0 else None
        end = dates[1] if len(dates) > 1 else (dates[0] if len(dates) == 1 else None)
        return start, end

    def _determine_status_from_date(self, deadline: date | None) -> str:
        if not deadline:
            return "open"
        today = date.today()
        if deadline < today:
            return "closed"
        if (deadline - today).days <= 14:
            return "closing_soon"
        return "open"
