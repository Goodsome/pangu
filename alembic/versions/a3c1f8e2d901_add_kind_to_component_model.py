"""add kind to component model

Revision ID: a3c1f8e2d901
Revises: be99a27d8fb3
Create Date: 2026-05-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c1f8e2d901'
down_revision: Union[str, Sequence[str], None] = 'be99a27d8fb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('components', sa.Column('kind', sa.String(length=50), server_default='class', nullable=False))
    op.create_index(op.f('ix_components_kind'), 'components', ['kind'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_components_kind'), table_name='components')
    op.drop_column('components', 'kind')
