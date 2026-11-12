
"""add ticket lifecycle fields

Revision ID: 521419be03b5
Revises: a2dfeaec9b49
Create Date: 2026-11-12 15:23:54.462889
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '521419be03b5'
down_revision: Union[str, Sequence[str], None] = 'a2dfeaec9b49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ticket lifecycle fields."""

    op.add_column(
        'tickets',
        sa.Column(
            'status',
            sa.String(length=20),
            server_default='new',
            nullable=False,
        ),
    )

    op.add_column(
        'tickets',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
    )

    op.add_column(
        'tickets',
        sa.Column(
            'resolved_at',
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_check_constraint(
        'tickets_status_check',
        'tickets',
        "status IN ('new', 'open', 'in_progress', "
        "'waiting_customer', 'resolved', 'closed')",
    )


def downgrade() -> None:
    """Remove ticket lifecycle fields."""

    op.drop_constraint(
        'tickets_status_check',
        'tickets',
        type_='check',
    )

    op.drop_column('tickets', 'resolved_at')
    op.drop_column('tickets', 'updated_at')
    op.drop_column('tickets', 'status')
