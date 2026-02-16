"""Initial tables: grants, scrape_sources, scrape_logs

Revision ID: 001
Revises:
Create Date: 2026-02-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # grants table
    op.create_table(
        "grants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(200), unique=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("organization", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("summary", sa.Text),
        sa.Column("target_audience", sa.Text),
        sa.Column("amount_min", sa.BigInteger),
        sa.Column("amount_max", sa.BigInteger),
        sa.Column("application_start", sa.Date),
        sa.Column("application_deadline", sa.Date),
        sa.Column("detail_url", sa.Text),
        sa.Column("guideline_url", sa.Text),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("raw_data", JSONB),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("idx_grants_source", "grants", ["source"])
    op.create_index("idx_grants_status", "grants", ["status"])
    op.create_index("idx_grants_deadline", "grants", ["application_deadline"])
    op.create_index("idx_grants_source_id", "grants", ["source_id"])
    op.execute("CREATE INDEX idx_grants_title_gin ON grants USING gin(to_tsvector('simple', title))")

    # scrape_sources table
    op.create_table(
        "scrape_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("config", JSONB),
        sa.Column("schedule_cron", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # scrape_logs table
    op.create_table(
        "scrape_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("scrape_sources.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'running'")),
        sa.Column("records_found", sa.Integer, server_default=sa.text("0")),
        sa.Column("records_created", sa.Integer, server_default=sa.text("0")),
        sa.Column("records_updated", sa.Integer, server_default=sa.text("0")),
        sa.Column("error_message", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed data for scrape_sources
    op.execute("""
        INSERT INTO scrape_sources (name, type, url, config, schedule_cron) VALUES
        (
          'JGrants API',
          'api',
          'https://api.jgrants-portal.go.jp/exp/v1/public/subsidies',
          '{"default_keyword": "研究", "keywords": ["研究", "科学技術", "イノベーション", "スタートアップ", "事業"], "acceptance": 1, "sort": "created_date", "order": "DESC", "limit": 100}',
          '0 6 * * *'
        ),
        (
          'e-Rad公募一覧',
          'scrape',
          'https://www.e-rad.go.jp/offer_list.html',
          '{"parser": "beautifulsoup4", "interval_sec": 3}',
          '0 7 * * *'
        )
    """)


def downgrade() -> None:
    op.drop_table("scrape_logs")
    op.drop_table("scrape_sources")
    op.execute("DROP INDEX IF EXISTS idx_grants_title_gin")
    op.drop_table("grants")
