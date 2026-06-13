"""add members and discriminator to component model

Revision ID: b7d2e4f1a803
Revises: a3c1f8e2d901
Create Date: 2026-05-26 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'b7d2e4f1a803'
down_revision: Union[str, Sequence[str], None] = 'a3c1f8e2d901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('components', sa.Column('members', JSONB, server_default='[]', nullable=False))
    op.add_column('components', sa.Column('discriminator', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('components', 'discriminator')
    op.drop_column('components', 'members')
