"""split_equipment_statlines_table

词缀从 entry_equipments.statlines JSONB 规范化拆表为
entry_equipment_statlines, 并回填存量数据。

Revision ID: a3c1f8d92b47
Revises: e2539d730886
Create Date: 2026-08-16 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a3c1f8d92b47"
down_revision: str | Sequence[str] | None = "e2539d730886"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BACKFILL_SQL = sa.text(
    """
    INSERT INTO entry_equipment_statlines (
        id, equipment_id, position, affix_id, codename, stat_type,
        is_greater, is_temper, is_rerolled, is_transfigured, is_masterwork_crit
    )
    SELECT
        gen_random_uuid(),
        eq.id,
        ord - 1,
        (line->>'affix_id')::bigint,
        line->>'codename',
        line->>'stat_type',
        COALESCE((line->>'is_greater')::boolean, false),
        COALESCE((line->>'is_temper')::boolean, false),
        COALESCE((line->>'is_rerolled')::boolean, false),
        COALESCE((line->>'is_transfigured')::boolean, false),
        COALESCE((line->>'is_masterwork_crit')::boolean, false)
    FROM entry_equipments AS eq
    CROSS JOIN LATERAL jsonb_array_elements(eq.statlines)
        WITH ORDINALITY AS t(line, ord)
    """
)

_RESTORE_SQL = sa.text(
    """
    UPDATE entry_equipments AS eq
    SET statlines = sub.aggregated
    FROM (
        SELECT equipment_id, jsonb_agg(
            jsonb_build_object(
                'affix_id', affix_id,
                'codename', codename,
                'stat_type', stat_type,
                'is_greater', is_greater,
                'is_temper', is_temper,
                'is_rerolled', is_rerolled,
                'is_transfigured', is_transfigured,
                'is_masterwork_crit', is_masterwork_crit
            ) ORDER BY position
        ) AS aggregated
        FROM entry_equipment_statlines
        GROUP BY equipment_id
    ) AS sub
    WHERE eq.id = sub.equipment_id
    """
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "entry_equipment_statlines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("equipment_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("affix_id", sa.BigInteger(), nullable=True),
        sa.Column("codename", sa.String(), nullable=False),
        sa.Column("stat_type", sa.String(), nullable=False),
        sa.Column("is_greater", sa.Boolean(), nullable=False),
        sa.Column("is_temper", sa.Boolean(), nullable=False),
        sa.Column("is_rerolled", sa.Boolean(), nullable=False),
        sa.Column("is_transfigured", sa.Boolean(), nullable=False),
        sa.Column("is_masterwork_crit", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["equipment_id"], ["entry_equipments.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_entry_equipment_statlines_equipment_id"),
        "entry_equipment_statlines",
        ["equipment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_entry_equipment_statlines_codename"),
        "entry_equipment_statlines",
        ["codename"],
        unique=False,
    )
    # 存量 JSONB 词缀回填到新表
    op.execute(_BACKFILL_SQL)
    op.drop_column("entry_equipments", "statlines")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "entry_equipments",
        sa.Column("statlines", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    # 词缀聚合回 JSONB 后删除新表
    op.execute(_RESTORE_SQL)
    op.drop_index(
        op.f("ix_entry_equipment_statlines_codename"),
        table_name="entry_equipment_statlines",
    )
    op.drop_index(
        op.f("ix_entry_equipment_statlines_equipment_id"),
        table_name="entry_equipment_statlines",
    )
    op.drop_table("entry_equipment_statlines")
