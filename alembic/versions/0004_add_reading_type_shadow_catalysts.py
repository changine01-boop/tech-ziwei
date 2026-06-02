"""Add shadow_work and positive_catalysts to readingtype enum.

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-02
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL ALTER TYPE ADD VALUE is non-transactional; must run outside any
    # transaction block.  Alembic's execute() with autocommit handles this.
    op.execute("ALTER TYPE readingtype ADD VALUE IF NOT EXISTS 'shadow_work'")
    op.execute("ALTER TYPE readingtype ADD VALUE IF NOT EXISTS 'positive_catalysts'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values; downgrade is a no-op.
    # To fully revert, drop and recreate the enum (requires data migration).
    pass
