from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, or_
from sqlalchemy.sql import text
from models.grant import Grant, ScrapeSource, ScrapeLog
from uuid import UUID
from datetime import datetime
from typing import Optional
import math


class GrantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_grants(
        self,
        status: Optional[str] = None,
        source: Optional[str] = None,
        keyword: Optional[str] = None,
        sort: str = "deadline",
        order: str = "asc",
        page: int = 1,
        limit: int = 20,
    ) -> dict:
        limit = min(limit, 100)
        page = max(page, 1)
        offset = (page - 1) * limit

        query = select(Grant)
        count_query = select(func.count(Grant.id))

        # Filters
        if status:
            query = query.where(Grant.status == status)
            count_query = count_query.where(Grant.status == status)
        if source:
            query = query.where(Grant.source == source)
            count_query = count_query.where(Grant.source == source)
        if keyword:
            pattern = f"%{keyword}%"
            query = query.where(Grant.title.ilike(pattern))
            count_query = count_query.where(Grant.title.ilike(pattern))

        # Sort
        sort_column_map = {
            "deadline": Grant.application_deadline,
            "created": Grant.created_at,
            "amount": Grant.amount_max,
            "title": Grant.title,
        }
        sort_column = sort_column_map.get(sort, Grant.application_deadline)
        if order == "desc":
            query = query.order_by(desc(sort_column).nulls_last())
        else:
            query = query.order_by(asc(sort_column).nulls_last())

        # Pagination
        query = query.offset(offset).limit(limit)

        # Execute
        result = await self.db.execute(query)
        grants = result.scalars().all()

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Source counts
        source_counts_result = await self.db.execute(
            select(Grant.source, func.count(Grant.id)).group_by(Grant.source)
        )
        source_counts = {row[0]: row[1] for row in source_counts_result.all()}

        # Last synced
        last_synced_result = await self.db.execute(
            select(func.max(Grant.last_synced_at))
        )
        last_synced = last_synced_result.scalar()

        return {
            "data": grants,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": math.ceil(total / limit) if total > 0 else 0,
            },
            "meta": {
                "sources": source_counts,
                "last_synced": last_synced,
            },
        }

    async def get_grant(self, grant_id: UUID) -> Optional[Grant]:
        result = await self.db.execute(select(Grant).where(Grant.id == grant_id))
        return result.scalar_one_or_none()

    async def get_scrape_log(self, log_id: UUID) -> Optional[ScrapeLog]:
        result = await self.db.execute(select(ScrapeLog).where(ScrapeLog.id == log_id))
        return result.scalar_one_or_none()

    async def get_scrape_source_by_name(self, name: str) -> Optional[ScrapeSource]:
        result = await self.db.execute(
            select(ScrapeSource).where(ScrapeSource.name == name)
        )
        return result.scalar_one_or_none()

    async def create_scrape_log(self, source_id: UUID) -> ScrapeLog:
        log = ScrapeLog(source_id=source_id)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log
