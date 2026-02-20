from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import func

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api"))
sys.path.insert(0, "/app")

from models.grant import Grant, ScrapeSource, ScrapeLog

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all scrapers."""

    def __init__(self, db: AsyncSession, source_name: str):
        self.db = db
        self.source_name = source_name
        self.stats = {
            "records_found": 0,
            "records_created": 0,
            "records_updated": 0,
        }

    async def run(self) -> dict:
        """Main execution flow: fetch -> parse -> upsert -> log."""
        log = await self._create_log()
        try:
            # Update expired statuses before syncing
            await self._update_expired_statuses()

            raw_items = await self.fetch()
            parsed_items = self.parse(raw_items)
            self.stats["records_found"] = len(parsed_items)

            for item in parsed_items:
                await self.upsert(item)

            await self._complete_log(log, "success")
            logger.info(f"[{self.source_name}] Completed: {self.stats}")
        except Exception as e:
            await self._complete_log(log, "failed", str(e))
            logger.error(f"[{self.source_name}] Failed: {e}")
            raise
        return self.stats

    @abstractmethod
    async def fetch(self) -> list:
        """Fetch raw data from the source."""
        ...

    @abstractmethod
    def parse(self, raw_data: list) -> list[dict]:
        """Parse raw data into grant dicts."""
        ...

    async def upsert(self, item: dict):
        """Insert or update a grant record based on source_id."""
        # Check if record exists to track created vs updated
        existing = await self.db.execute(
            select(Grant.id).where(Grant.source_id == item.get("source_id"))
        )
        exists = existing.scalar_one_or_none()

        stmt = pg_insert(Grant).values(**item)
        stmt = stmt.on_conflict_do_update(
            index_elements=["source_id"],
            set_={
                "title": stmt.excluded.title,
                "organization": stmt.excluded.organization,
                "category": stmt.excluded.category,
                "summary": stmt.excluded.summary,
                "target_audience": stmt.excluded.target_audience,
                "amount_min": stmt.excluded.amount_min,
                "amount_max": stmt.excluded.amount_max,
                "application_start": stmt.excluded.application_start,
                "application_deadline": stmt.excluded.application_deadline,
                "detail_url": stmt.excluded.detail_url,
                "status": stmt.excluded.status,
                "raw_data": stmt.excluded.raw_data,
                "last_synced_at": func.now(),
                "updated_at": func.now(),
            },
        )
        await self.db.execute(stmt)
        await self.db.commit()

        if exists:
            self.stats["records_updated"] += 1
        else:
            self.stats["records_created"] += 1

    async def _update_expired_statuses(self):
        """Update status to 'closed' for grants past their deadline."""
        await self.db.execute(
            update(Grant)
            .where(Grant.application_deadline < func.current_date())
            .where(Grant.status != "closed")
            .values(status="closed", updated_at=func.now())
        )
        await self.db.commit()

    async def _create_log(self) -> ScrapeLog:
        """Create a scrape log entry."""
        source = await self.db.execute(
            select(ScrapeSource).where(ScrapeSource.name == self.source_name)
        )
        source_record = source.scalar_one_or_none()
        if not source_record:
            logger.warning(f"Source '{self.source_name}' not found in DB, creating log without source_id")
            return None

        log = ScrapeLog(source_id=source_record.id)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def _complete_log(self, log: ScrapeLog, status: str, error: str = None):
        """Update the scrape log with final status."""
        if not log:
            return
        log.finished_at = datetime.utcnow()
        log.status = status
        log.records_found = self.stats["records_found"]
        log.records_created = self.stats["records_created"]
        log.records_updated = self.stats["records_updated"]
        log.error_message = error
        await self.db.commit()
