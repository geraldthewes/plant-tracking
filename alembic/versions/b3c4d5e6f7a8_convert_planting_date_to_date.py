"""Convert planting_date to DATE

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-08-23 21:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert planting_date column to DATE type.

    Requires that all existing values are valid ISO dates — run
    scripts/verify_planting_dates.py first. Fails loudly if any
    value cannot be cast.
    """
    op.execute(
        "ALTER TABLE plants ALTER COLUMN planting_date TYPE DATE "
        "USING planting_date::date"
    )


def downgrade() -> None:
    """Revert planting_date column to VARCHAR type."""
    op.execute(
        "ALTER TABLE plants ALTER COLUMN planting_date TYPE VARCHAR(10) "
        "USING planting_date::varchar"
    )
