"""base_version

Revision ID: 34b3faf6499c
Revises: 
Create Date: 2026-06-13 14:37:10.477116

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '34b3faf6499c'
down_revision: Union[str, Sequence[str], None] = '7293379d522a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
