"""add_death_fields_to_plant

Revision ID: a1b2c3d4e5f6
Revises: f6a7830adb3d
Create Date: 2026-08-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f6a7830adb3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add death tracking fields to plants table."""
    op.add_column(
        'plants',
        sa.Column('death_date', sa.String(length=10), nullable=True)
    )
    op.add_column(
        'plants',
        sa.Column('death_reason', sa.String(length=50), nullable=True)
    )
    op.add_column(
        'plants',
        sa.Column('death_comment', sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    """Remove death tracking fields from plants table."""
    op.drop_column('plants', 'death_comment')
    op.drop_column('plants', 'death_reason')
    op.drop_column('plants', 'death_date')
