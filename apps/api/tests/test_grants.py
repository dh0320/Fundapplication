import pytest
import pytest_asyncio


@pytest.mark.asyncio
class TestGrantsAPI:
    async def test_health_check(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    async def test_list_grants_empty(self, client):
        """Empty DB should return 200 with empty list."""
        resp = await client.get("/api/v1/grants")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_list_grants_with_data(self, client, seed_grants):
        """With seed data, correct count should be returned."""
        resp = await client.get("/api/v1/grants")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 5
        assert data["pagination"]["total"] == 5

    async def test_filter_by_status(self, client, seed_grants):
        """Filtering by status=open should return correct results."""
        resp = await client.get("/api/v1/grants?status=open")
        assert resp.status_code == 200
        data = resp.json()
        for grant in data["data"]:
            assert grant["status"] == "open"
        assert data["pagination"]["total"] == 3

    async def test_filter_by_source(self, client, seed_grants):
        """Filtering by source=jgrants should return correct results."""
        resp = await client.get("/api/v1/grants?source=jgrants")
        assert resp.status_code == 200
        data = resp.json()
        for grant in data["data"]:
            assert grant["source"] == "jgrants"
        assert data["pagination"]["total"] == 3

    async def test_filter_by_source_erad(self, client, seed_grants):
        """Filtering by source=erad should return correct results."""
        resp = await client.get("/api/v1/grants?source=erad")
        assert resp.status_code == 200
        data = resp.json()
        for grant in data["data"]:
            assert grant["source"] == "erad"
        assert data["pagination"]["total"] == 2

    async def test_keyword_search(self, client, seed_grants):
        """Keyword search should match title (ILIKE)."""
        resp = await client.get("/api/v1/grants?keyword=研究")
        assert resp.status_code == 200
        data = resp.json()
        assert data["pagination"]["total"] >= 2
        for grant in data["data"]:
            assert "研究" in grant["title"]

    async def test_keyword_search_no_results(self, client, seed_grants):
        """Keyword search with no match should return empty."""
        resp = await client.get("/api/v1/grants?keyword=存在しないキーワード")
        assert resp.status_code == 200
        data = resp.json()
        assert data["pagination"]["total"] == 0
        assert data["data"] == []

    async def test_pagination(self, client, seed_grants):
        """Pagination should work correctly."""
        resp = await client.get("/api/v1/grants?limit=2&page=1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["total_pages"] == 3

        # Page 2
        resp2 = await client.get("/api/v1/grants?limit=2&page=2")
        data2 = resp2.json()
        assert len(data2["data"]) == 2
        assert data2["pagination"]["page"] == 2

        # Page 3 (last page, only 1 item)
        resp3 = await client.get("/api/v1/grants?limit=2&page=3")
        data3 = resp3.json()
        assert len(data3["data"]) == 1

    async def test_sort_by_deadline_asc(self, client, seed_grants):
        """Sort by deadline ascending should work."""
        resp = await client.get("/api/v1/grants?sort=deadline&order=asc")
        assert resp.status_code == 200
        data = resp.json()
        deadlines = [
            g["application_deadline"]
            for g in data["data"]
            if g["application_deadline"]
        ]
        assert deadlines == sorted(deadlines)

    async def test_sort_by_deadline_desc(self, client, seed_grants):
        """Sort by deadline descending should work."""
        resp = await client.get("/api/v1/grants?sort=deadline&order=desc")
        assert resp.status_code == 200
        data = resp.json()
        deadlines = [
            g["application_deadline"]
            for g in data["data"]
            if g["application_deadline"]
        ]
        assert deadlines == sorted(deadlines, reverse=True)

    async def test_get_grant_detail(self, client, seed_grants):
        """GET /api/v1/grants/{id} should return the grant detail."""
        # First get list to find an id
        resp = await client.get("/api/v1/grants")
        data = resp.json()
        grant_id = data["data"][0]["id"]

        resp2 = await client.get(f"/api/v1/grants/{grant_id}")
        assert resp2.status_code == 200
        detail = resp2.json()
        assert detail["id"] == grant_id
        assert "created_at" in detail
        assert "updated_at" in detail

    async def test_get_grant_not_found(self, client):
        """GET /api/v1/grants/{id} with invalid id should return 404."""
        resp = await client.get(
            "/api/v1/grants/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    async def test_meta_sources(self, client, seed_grants):
        """Meta should contain source counts."""
        resp = await client.get("/api/v1/grants")
        data = resp.json()
        assert "sources" in data["meta"]
        assert data["meta"]["sources"].get("jgrants", 0) == 3
        assert data["meta"]["sources"].get("erad", 0) == 2
