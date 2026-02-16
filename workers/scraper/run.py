import argparse
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api"))
sys.path.insert(0, "/app")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main(source: str):
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://grantdraft:grantdraft_dev@db:5432/grantdraft",
    )
    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        if source in ("jgrants", "all"):
            from workers.scraper.jgrants import JGrantsScraper

            logger.info("Starting JGrants scraper...")
            scraper = JGrantsScraper(session, "JGrants API")
            stats = await scraper.run()
            logger.info(f"JGrants scraper finished: {stats}")

        if source in ("erad", "all"):
            from workers.scraper.erad import ERadScraper

            logger.info("Starting e-Rad scraper...")
            scraper = ERadScraper(session, "e-Rad公募一覧")
            stats = await scraper.run()
            logger.info(f"e-Rad scraper finished: {stats}")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrantDraft data collection worker")
    parser.add_argument(
        "--source",
        choices=["jgrants", "erad", "all"],
        default="all",
        help="Data source to scrape",
    )
    args = parser.parse_args()
    asyncio.run(main(args.source))
