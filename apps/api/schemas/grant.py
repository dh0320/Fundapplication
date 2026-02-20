from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class GrantResponse(BaseModel):
    id: UUID
    source: str
    title: str
    organization: str
    category: Optional[str] = None
    summary: Optional[str] = None
    target_audience: Optional[str] = None
    amount_min: Optional[int] = None
    amount_max: Optional[int] = None
    application_start: Optional[date] = None
    application_deadline: Optional[date] = None
    detail_url: Optional[str] = None
    guideline_url: Optional[str] = None
    status: str
    last_synced_at: datetime

    class Config:
        from_attributes = True


class GrantDetailResponse(GrantResponse):
    raw_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


class SourcesMeta(BaseModel):
    sources: dict[str, int]
    last_synced: Optional[datetime] = None


class GrantListResponse(BaseModel):
    data: list[GrantResponse]
    pagination: PaginationMeta
    meta: SourcesMeta


class SyncRequest(BaseModel):
    source: str  # "jgrants" | "erad" | "all"


class SyncResponse(BaseModel):
    scrape_log_id: UUID
    message: str


class ScrapeLogResponse(BaseModel):
    id: UUID
    source_id: UUID
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    records_found: int
    records_created: int
    records_updated: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
