"""add_media_attachments_table

Revision ID: f6a7830adb3d
Revises: 72fff22905dd
Create Date: 2026-06-06 14:21:52.677624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a7830adb3d'
down_revision: Union[str, Sequence[str], None] = '72fff22905dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "media_attachments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "plant_id", sa.String(20), sa.ForeignKey("plants.id"), nullable=False
        ),
        sa.Column("media_type", sa.String(20), nullable=False),
        sa.Column("s3_key", sa.String(500), nullable=False),
        sa.Column("timestamp", sa.String(20), nullable=False),
        sa.Column("label", sa.String(200), nullable=True),
        sa.Column("tags", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.CheckConstraint(
            "media_type IN ('image', 'video', 'audio')",
            name="check_media_type",
        ),
    )
    op.create_index(
        "ix_media_attachments_plant_id", "media_attachments", ["plant_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_media_attachments_plant_id", table_name="media_attachments")
    op.drop_table("media_attachments")
