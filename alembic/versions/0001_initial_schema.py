"""Initial schema: users, charts, readings

Revision ID: 0001
Revises:
Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "subscription_tier",
            sa.Enum("free", "basic", "pro", name="subscriptiontier"),
            nullable=False,
            server_default="free",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "charts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gregorian_date", sa.Date(), nullable=False),
        sa.Column("birth_time", sa.Time(), nullable=False),
        sa.Column("is_male", sa.Boolean(), nullable=False),
        sa.Column("timezone_offset", sa.Float(), nullable=False, server_default="8.0"),
        sa.Column("lunar_year", sa.Integer(), nullable=False),
        sa.Column("lunar_month", sa.Integer(), nullable=False),
        sa.Column("lunar_day", sa.Integer(), nullable=False),
        sa.Column("is_leap_month", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ming_branch", sa.Integer(), nullable=False),
        sa.Column("wu_xing_ju", sa.Integer(), nullable=False),
        sa.Column("year_stem", sa.Integer(), nullable=False),
        sa.Column("year_branch", sa.Integer(), nullable=False),
        sa.Column("star_placements", postgresql.JSONB(), nullable=False),
        sa.Column("major_periods", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_charts_user_id", "charts", ["user_id"])

    op.create_table(
        "readings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("chart_id", sa.String(36), sa.ForeignKey("charts.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "reading_type",
            sa.Enum("core", "relationship", "career", "annual", name="readingtype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "generating", "complete", "failed", name="readingstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_readings_chart_id", "readings", ["chart_id"])


def downgrade() -> None:
    op.drop_table("readings")
    op.drop_table("charts")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS readingstatus")
    op.execute("DROP TYPE IF EXISTS readingtype")
    op.execute("DROP TYPE IF EXISTS subscriptiontier")
