"""Add mutagens column to charts

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


def upgrade() -> None:
    op.add_column(
        "charts",
        sa.Column(
            "mutagens",
            JSONB,
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column("charts", "mutagens")
