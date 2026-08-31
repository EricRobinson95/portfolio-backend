"""add project image display order constraint

Revision ID: ed063c3d37f0
Revises: 1c2a5aa369ae
Create Date: 2026-08-29 13:43:33.697741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed063c3d37f0'
down_revision: Union[str, Sequence[str], None] = '1c2a5aa369ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_project_images_project_display_order",
        "project_images",
        ["project_id", "display_order"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_project_images_project_display_order",
        "project_images",
        type_="unique",
    )