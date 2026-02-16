import pytest
from datetime import date

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "apps", "api"))
sys.path.insert(0, "/app")


class TestJGrantsScraper:
    def _get_scraper_class(self):
        from workers.scraper.jgrants import JGrantsScraper
        return JGrantsScraper

    def test_parse_amount_integer(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        assert scraper._parse_amount(1000000) == 1000000

    def test_parse_amount_float(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        assert scraper._parse_amount(1000000.0) == 1000000

    def test_parse_amount_string(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        assert scraper._parse_amount("1,000,000") == 1000000

    def test_parse_amount_man(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        assert scraper._parse_amount("100万円") == 1000000

    def test_parse_amount_oku(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        assert scraper._parse_amount("1億円") == 100000000

    def test_parse_amount_none(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        assert scraper._parse_amount(None) is None

    def test_parse_date_iso(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        result = scraper._parse_date("2025-06-30")
        assert result == date(2025, 6, 30)

    def test_parse_date_with_time(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        result = scraper._parse_date("2025-06-30T23:59:59")
        assert result == date(2025, 6, 30)

    def test_parse_date_with_z(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        result = scraper._parse_date("2025-06-30T23:59:59Z")
        assert result == date(2025, 6, 30)

    def test_parse_date_none(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        assert scraper._parse_date(None) is None

    def test_parse_date_empty(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        assert scraper._parse_date("") is None

    def test_determine_status_open(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        item = {"acceptance_end_datetime": "2099-12-31T23:59:59"}
        assert scraper._determine_status(item) == "open"

    def test_determine_status_closed(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        item = {"acceptance_end_datetime": "2020-01-01T00:00:00"}
        assert scraper._determine_status(item) == "closed"

    def test_determine_status_no_deadline(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        item = {}
        assert scraper._determine_status(item) == "open"

    def test_classify_category_research(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        item = {"title": "基礎研究推進事業", "outline": ""}
        assert scraper._classify_category(item) == "research"

    def test_classify_category_startup(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        item = {"title": "スタートアップ支援", "outline": ""}
        assert scraper._classify_category(item) == "startup"

    def test_classify_category_equipment(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        item = {"title": "設備導入支援", "outline": ""}
        assert scraper._classify_category(item) == "equipment"

    def test_classify_category_international(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        item = {"title": "国際共同研究", "outline": "海外の大学との連携"}
        assert scraper._classify_category(item) == "international"

    def test_classify_category_other(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        item = {"title": "補助金事業", "outline": "一般的な事業"}
        assert scraper._classify_category(item) == "other"

    def test_parse_response(self):
        JGrantsScraper = self._get_scraper_class()
        scraper = JGrantsScraper.__new__(JGrantsScraper)
        raw_data = [
            {
                "id": "12345",
                "title": "テスト研究補助金",
                "subsidy_executing_organization_name": "テスト省",
                "outline": "テスト概要",
                "target": "研究者",
                "subsidy_min_limit": 100000,
                "subsidy_max_limit": 500000,
                "acceptance_start_datetime": "2026-04-01T00:00:00",
                "acceptance_end_datetime": "2026-06-30T23:59:59",
            }
        ]
        result = scraper.parse(raw_data)
        assert len(result) == 1
        assert result[0]["source"] == "jgrants"
        assert result[0]["source_id"] == "jgrants_12345"
        assert result[0]["title"] == "テスト研究補助金"
        assert result[0]["organization"] == "テスト省"
        assert result[0]["amount_min"] == 100000
        assert result[0]["amount_max"] == 500000
        assert result[0]["application_start"] == date(2026, 4, 1)
        assert result[0]["application_deadline"] == date(2026, 6, 30)
        assert result[0]["category"] == "research"
