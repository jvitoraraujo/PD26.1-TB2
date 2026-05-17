"""add medico_id e diagnostico na consulta

Revision ID: e107b052aff6
Revises: 87627ab512c3
Create Date: 2026-05-16 21:50:49.138642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e107b052aff6'
down_revision: Union[str, Sequence[str], None] = '87627ab512c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('consultas', sa.Column('diagnostico', sa.Text(), nullable=True))
    op.add_column('consultas', sa.Column('medico_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('consultas', 'medico_id')
    op.drop_column('consultas', 'diagnostico')