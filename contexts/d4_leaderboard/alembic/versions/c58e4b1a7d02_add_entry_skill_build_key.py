"""add_entry_skill_build_key

entries 增加 skill_build_key 派生列 (技能 codename 排序去重后 '+'
拼接), 用于按技能组合 (build) 分组与过滤, 并回填存量数据。

Revision ID: c58e4b1a7d02
Revises: a3c1f8d92b47
Create Date: 2026-08-16 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c58e4b1a7d02"
down_revision: str | Sequence[str] | None = "a3c1f8d92b47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 与领域层 SkillBuild 语义一致: codename 去重排序后拼接, 空技能列表聚合为 NULL
_BACKFILL_SQL = sa.text(
    """
    UPDATE entries SET skill_build_key = (
        SELECT string_agg(codename, '+' ORDER BY codename)
        FROM (
            SELECT DISTINCT s->>'codename' AS codename
            FROM jsonb_array_elements(entries.skills) AS s
        ) AS t
    )
    WHERE skills IS NOT NULL AND jsonb_typeof(skills) = 'array'
    """
)


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "entries",
        sa.Column("skill_build_key", sa.String(), nullable=True),
    )
    op.create_index(
        op.f("ix_entries_skill_build_key"),
        "entries",
        ["skill_build_key"],
        unique=False,
    )
    op.execute(_BACKFILL_SQL)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_entries_skill_build_key"), table_name="entries")
    op.drop_column("entries", "skill_build_key")
