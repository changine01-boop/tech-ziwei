"""Add stripe_customer_id to users

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "stripe_customer_id")
