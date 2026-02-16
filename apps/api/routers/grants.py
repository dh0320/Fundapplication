from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.grant_service import GrantService
from schemas.grant import (
    GrantResponse,
    GrantDetailResponse,
    GrantListResponse,
    PaginationMeta,
    SourcesMeta,
    SyncRequest,
    SyncResponse,
    ScrapeLogResponse,
)
from uuid import UUID
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["grants"])


@router.get("/grants", response_model=GrantListResponse)
async def list_grants(
    status: Optional[str] = Query(None, description="Filter by status"),
    source: Optional[str] = Query(None, description="Filter by source"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    sort: str = Query("deadline", description="Sort field"),
    order: str = Query("asc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    service = GrantService(db)
    result = await service.list_grants(
        status=status,
        source=source,
        keyword=keyword,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )
    return GrantListResponse(
        data=[GrantResponse.model_validate(g) for g in result["data"]],
        pagination=PaginationMeta(**result["pagination"]),
        meta=SourcesMeta(**result["meta"]),
    )


@router.get("/grants/{grant_id}", response_model=GrantDetailResponse)
async def get_grant(grant_id: UUID, db: AsyncSession = Depends(get_db)):
    service = GrantService(db)
    grant = await service.get_grant(grant_id)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return GrantDetailResponse.model_validate(grant)


async def _run_sync(source: str, log_id: UUID, db_url: str):
    """Run scraper in background."""
    import sys
    import os
    sys.path.insert(0, "/app")
    sys.path.insert(0, "/workers")

    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from workers.scraper.jgrants import JGrantsScraper
    from workers.scraper.erad import ERadScraper

    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            if source in ("jgrants", "all"):
                scraper = JGrantsScraper(session, "JGrants API")
                await scraper.run()
            if source in ("erad", "all"):
                scraper = ERadScraper(session, "e-Rad公募一覧")
                await scraper.run()
        except Exception as e:
            logger.error(f"Sync failed: {e}")
        finally:
            await engine.dispose()


@router.post("/grants/sync", response_model=SyncResponse, status_code=202)
async def trigger_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    service = GrantService(db)

    # Determine source name for log
    source_name_map = {
        "jgrants": "JGrants API",
        "erad": "e-Rad公募一覧",
        "all": "JGrants API",
    }
    source_record = await service.get_scrape_source_by_name(
        source_name_map.get(request.source, "JGrants API")
    )

    if not source_record:
        raise HTTPException(status_code=404, detail="Source not found")

    log = await service.create_scrape_log(source_record.id)

    from config import settings
    background_tasks.add_task(
        asyncio.to_thread,
        lambda: asyncio.run(_run_sync(request.source, log.id, settings.DATABASE_URL)),
    )

    return SyncResponse(
        scrape_log_id=log.id,
        message=f"Sync started for source: {request.source}",
    )


@router.get("/sync/status/{log_id}", response_model=ScrapeLogResponse)
async def get_sync_status(log_id: UUID, db: AsyncSession = Depends(get_db)):
    service = GrantService(db)
    log = await service.get_scrape_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Sync log not found")
    return ScrapeLogResponse.model_validate(log)
