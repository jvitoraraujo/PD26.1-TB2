"""merge heads

Revision ID: f286611dd47d
Revises: de20397ee083, e107b052aff6
Create Date: 2026-05-17 11:11:52.851333

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f286611dd47d'
down_revision: Union[str, Sequence[str], None] = ('de20397ee083', 'e107b052aff6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
