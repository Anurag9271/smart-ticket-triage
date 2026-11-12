
"""baseline existing tickets schema

Revision ID: a2dfeaec9b49
Revises:
Create Date: 2026-11-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "a2dfeaec9b49"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the original tickets table."""

    op.create_table(
        "tickets",

        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "email",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "category",
            sa.String(length=20),
            nullable=False,
        ),

        sa.Column(
            "urgency",
            sa.String(length=10),
            nullable=False,
        ),

        sa.Column(
            "sentiment",
            sa.String(length=10),
            nullable=False,
        ),

        sa.Column(
            "review_status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),

        sa.CheckConstraint(
            "category IN ('billing', 'technical', 'account', 'other')",
            name="tickets_category_check",
        ),

        sa.CheckConstraint(
            "urgency IN ('high', 'medium', 'low')",
            name="tickets_urgency_check",
        ),

        sa.CheckConstraint(
            "sentiment IN ('positive', 'neutral', 'negative')",
            name="tickets_sentiment_check",
        ),

        sa.CheckConstraint(
            "review_status IN ('pending', 'approved', 'rejected')",
            name="tickets_review_status_check",
        ),
    )


def downgrade() -> None:
    """Remove the tickets table."""

    op.drop_table("tickets")
