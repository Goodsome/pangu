"""update_entry_fields

Revision ID: b09727da4e6a
Revises: 5f930f2e079a
Create Date: 2026-08-01 11:55:37.659712

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b09727da4e6a"
down_revision: str | Sequence[str] | None = "5f930f2e079a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "entries",
        sa.Column(
            "player_name",
            sa.String(),
            nullable=False,
            server_default="UNKNOWN",
        ),
    )
    # 将现有数据行的 name 值复制迁移到 player_name
    op.execute("UPDATE entries SET player_name = name WHERE name IS NOT NULL")

    op.add_column(
        "entries",
        sa.Column(
            "player_class",
            sa.String(),
            nullable=False,
            server_default="barbarian",
        ),
    )
    op.add_column(
        "entries",
        sa.Column(
            "tier",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.add_column(
        "entries",
        sa.Column(
            "duration_ms",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "entries",
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.drop_column("entries", "name")

    # 清理临时 server_default 约束
    op.alter_column("entries", "player_name", server_default=None)
    op.alter_column("entries", "player_class", server_default=None)
    op.alter_column("entries", "tier", server_default=None)
    op.alter_column("entries", "duration_ms", server_default=None)
    op.alter_column("entries", "occurred_at", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "entries",
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
            server_default="UNKNOWN",
        ),
    )
    op.execute("UPDATE entries SET name = player_name WHERE player_name IS NOT NULL")
    op.alter_column("entries", "name", server_default=None)

    op.drop_column("entries", "occurred_at")
    op.drop_column("entries", "duration_ms")
    op.drop_column("entries", "tier")
    op.drop_column("entries", "player_class")
    op.drop_column("entries", "player_name")
