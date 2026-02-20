import pytest
import asyncio
from uuid import uuid4
from datetime import date, datetime, timezone

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.grant import Base, Grant, ScrapeSource, ScrapeLog
from database import get_db
from main import app


# Use sqlite for tests or in-memory postgres mock
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://grantdraft:grantdraft_dev@db:5432/grantdraft_test",
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        # Clean up after each test
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"DELETE FROM {table.name}"))
        await session.commit()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_grants(db_session):
    """Create sample grants for testing."""
    grants = [
        Grant(
            id=uuid4(),
            source="jgrants",
            source_id="jgrants_test_1",
            title="研究開発支援事業",
            organization="文部科学省",
            category="research",
            summary="研究開発のための補助金",
            amount_min=1000000,
            amount_max=5000000,
            application_start=date(2026, 4, 1),
            application_deadline=date(2026, 6, 30),
            status="open",
        ),
        Grant(
            id=uuid4(),
            source="jgrants",
            source_id="jgrants_test_2",
            title="スタートアップ支援事業",
            organization="経済産業省",
            category="startup",
            summary="スタートアップ企業への補助金",
            amount_min=500000,
            amount_max=10000000,
            application_start=date(2026, 3, 1),
            application_deadline=date(2026, 3, 15),
            status="closing_soon",
        ),
        Grant(
            id=uuid4(),
            source="erad",
            source_id="erad_test_1",
            title="科学技術振興機構 研究助成",
            organization="JST",
            category="research",
            summary="基礎研究のための助成金",
            amount_min=2000000,
            amount_max=20000000,
            application_start=date(2026, 1, 1),
            application_deadline=date(2026, 5, 31),
            status="open",
        ),
        Grant(
            id=uuid4(),
            source="erad",
            source_id="erad_test_2",
            title="国際共同研究プログラム",
            organization="JSPS",
            category="international",
            amount_min=3000000,
            amount_max=15000000,
            application_start=date(2025, 10, 1),
            application_deadline=date(2025, 12, 31),
            status="closed",
        ),
        Grant(
            id=uuid4(),
            source="jgrants",
            source_id="jgrants_test_3",
            title="設備導入支援補助金",
            organization="中小企業庁",
            category="equipment",
            amount_min=100000,
            amount_max=3000000,
            application_start=date(2026, 5, 1),
            application_deadline=date(2026, 7, 31),
            status="open",
        ),
    ]
    for grant in grants:
        db_session.add(grant)
    await db_session.commit()
    return grants
