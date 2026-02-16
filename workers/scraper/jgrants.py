import httpx
import asyncio
from datetime import datetime, date
import logging

from workers.scraper.base import BaseScraper

logger = logging.getLogger(__name__)


class JGrantsScraper(BaseScraper):
    """JGrants API integration worker."""

    KEYWORDS = ["研究", "科学技術", "イノベーション", "スタートアップ", "事業"]

    async def fetch(self) -> list:
        all_results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for keyword in self.KEYWORDS:
                offset = 0
                while True:
                    params = {
                        "keyword": keyword,
                        "sort": "created_date",
                        "order": "DESC",
                        "acceptance": 1,
                        "limit": 100,
                        "offset": offset,
                    }
                    headers = {
                        "User-Agent": "GrantDraft/1.0 (research-grant-aggregator)",
                        "Accept": "application/json",
                    }
                    try:
                        resp = await client.get(
                            "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies",
                            params=params,
                            headers=headers,
                        )
                        if resp.status_code == 403:
                            logger.warning(f"[JGrants] 403 received for keyword='{keyword}', waiting 5 min...")
                            await asyncio.sleep(300)
                            continue

                        resp.raise_for_status()
                        data = resp.json()
                    except httpx.HTTPStatusError as e:
                        logger.error(f"[JGrants] HTTP error: {e}")
                        break
                    except Exception as e:
                        logger.error(f"[JGrants] Request error: {e}")
                        break

                    results = data.get("result", [])
                    if not results:
                        break

                    all_results.extend(results)
                    offset += len(results)

                    if len(results) < 100:
                        break

                    await asyncio.sleep(1.0)

                await asyncio.sleep(1.0)

        # Deduplicate by source ID
        seen = set()
        unique = []
        for item in all_results:
            sid = str(item.get("id", ""))
            if sid and sid not in seen:
                seen.add(sid)
                unique.append(item)

        logger.info(f"[JGrants] Fetched {len(unique)} unique records (from {len(all_results)} total)")
        return unique

    def parse(self, raw_data: list) -> list[dict]:
        parsed = []
        for item in raw_data:
            try:
                parsed.append({
                    "source": "jgrants",
                    "source_id": f"jgrants_{item.get('id', '')}",
                    "title": item.get("title", ""),
                    "organization": (
                        item.get("subsidy_executing_organization_name", "")
                        or item.get("target_org_name", "不明")
                    ),
                    "category": self._classify_category(item),
                    "summary": item.get("outline", ""),
                    "target_audience": item.get("target", ""),
                    "amount_min": self._parse_amount(item.get("subsidy_min_limit")),
                    "amount_max": self._parse_amount(item.get("subsidy_max_limit")),
                    "application_start": self._parse_date(item.get("acceptance_start_datetime")),
                    "application_deadline": self._parse_date(item.get("acceptance_end_datetime")),
                    "detail_url": f"https://www.jgrants-portal.go.jp/subsidy/{item.get('id', '')}",
                    "status": self._determine_status(item),
                    "raw_data": item,
                })
            except Exception as e:
                logger.warning(f"[JGrants] Failed to parse item: {e}")
                continue
        return parsed

    def _parse_amount(self, val) -> int | None:
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return int(val)
        try:
            cleaned = str(val).replace(",", "").replace("円", "").strip()
            if "万" in cleaned:
                cleaned = cleaned.replace("万", "")
                return int(float(cleaned) * 10000)
            if "億" in cleaned:
                cleaned = cleaned.replace("億", "")
                return int(float(cleaned) * 100000000)
            return int(float(cleaned)) if cleaned else None
        except (ValueError, TypeError):
            return None

    def _parse_date(self, val) -> date | None:
        if not val:
            return None
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            return None

    def _determine_status(self, item) -> str:
        deadline_str = item.get("acceptance_end_datetime")
        if not deadline_str:
            return "open"
        try:
            deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00")).date()
            today = date.today()
            if deadline < today:
                return "closed"
            elif (deadline - today).days <= 14:
                return "closing_soon"
            return "open"
        except (ValueError, AttributeError):
            return "open"

    def _classify_category(self, item) -> str:
        text = f"{item.get('title', '')} {item.get('outline', '')}"
        if any(w in text for w in ["研究", "科研", "学術"]):
            return "research"
        if any(w in text for w in ["スタートアップ", "創業", "起業", "ベンチャー"]):
            return "startup"
        if any(w in text for w in ["設備", "機器", "導入"]):
            return "equipment"
        if any(w in text for w in ["国際", "海外", "渡航"]):
            return "international"
        return "other"
