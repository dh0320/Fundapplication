import pytest
from datetime import date

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "apps", "api"))
sys.path.insert(0, "/app")


class TestERadScraper:
    def _get_scraper_class(self):
        from workers.scraper.erad import ERadScraper
        return ERadScraper

    def test_parse_period_slash_format(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        start, end = scraper._parse_period("2025/4/1 〜 2025/6/30")
        assert start == date(2025, 4, 1)
        assert end == date(2025, 6, 30)

    def test_parse_period_dash_format(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        start, end = scraper._parse_period("2025-04-01 〜 2025-06-30")
        assert start == date(2025, 4, 1)
        assert end == date(2025, 6, 30)

    def test_parse_period_japanese_format(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        start, end = scraper._parse_period("2025年4月1日 〜 2025年6月30日")
        assert start == date(2025, 4, 1)
        assert end == date(2025, 6, 30)

    def test_parse_period_single_date(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        start, end = scraper._parse_period("2025/6/30")
        assert start == date(2025, 6, 30)
        assert end == date(2025, 6, 30)

    def test_parse_period_empty(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        start, end = scraper._parse_period("")
        assert start is None
        assert end is None

    def test_determine_status_from_date_open(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        assert scraper._determine_status_from_date(date(2099, 12, 31)) == "open"

    def test_determine_status_from_date_closed(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        assert scraper._determine_status_from_date(date(2020, 1, 1)) == "closed"

    def test_determine_status_from_date_none(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        assert scraper._determine_status_from_date(None) == "open"

    def test_parse_html_table(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        scraper.BASE_URL = "https://www.e-rad.go.jp"
        html = """
        <html>
        <body>
        <table>
            <tr><th>機関</th><th>公募名</th><th>期間</th></tr>
            <tr>
                <td>JST</td>
                <td><a href="/offer/detail/12345">科学技術振興事業の研究助成プログラム</a></td>
                <td>2025/4/1 〜 2025/6/30</td>
            </tr>
            <tr>
                <td>JSPS</td>
                <td><a href="/offer/detail/67890">国際共同研究プログラムの応募について</a></td>
                <td>2025/5/1 〜 2025/7/31</td>
            </tr>
        </table>
        </body>
        </html>
        """
        results = scraper.parse([html])
        assert len(results) == 2
        assert results[0]["source"] == "erad"
        assert "科学技術振興事業" in results[0]["title"]
        assert results[0]["organization"] == "JST"
        assert results[0]["application_start"] == date(2025, 4, 1)
        assert results[0]["application_deadline"] == date(2025, 6, 30)
        assert results[1]["organization"] == "JSPS"

    def test_parse_html_empty_table(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        scraper.BASE_URL = "https://www.e-rad.go.jp"
        html = "<html><body><table><tr><th>Header</th></tr></table></body></html>"
        results = scraper.parse([html])
        assert len(results) == 0

    def test_extract_source_id(self):
        ERadScraper = self._get_scraper_class()
        scraper = ERadScraper.__new__(ERadScraper)
        assert scraper._extract_source_id("/offer/detail/12345") == "12345"
        assert scraper._extract_source_id("/no-numbers") is None
        assert scraper._extract_source_id("") is None
