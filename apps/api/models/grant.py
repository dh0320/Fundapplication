from sqlalchemy import Column, String, Text, BigInteger, Date, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    pass


class Grant(Base):
    __tablename__ = "grants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    source_id = Column(String(200), unique=True)
    title = Column(Text, nullable=False)
    organization = Column(String(200), nullable=False)
    category = Column(String(100))
    summary = Column(Text)
    target_audience = Column(Text)
    amount_min = Column(BigInteger)
    amount_max = Column(BigInteger)
    application_start = Column(Date)
    application_deadline = Column(Date)
    detail_url = Column(Text)
    guideline_url = Column(Text)
    status = Column(String(20), nullable=False, default="open")
    raw_data = Column(JSONB)
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ScrapeSource(Base):
    __tablename__ = "scrape_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    url = Column(Text, nullable=False)
    config = Column(JSONB)
    schedule_cron = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("scrape_sources.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default="running")
    records_found = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
