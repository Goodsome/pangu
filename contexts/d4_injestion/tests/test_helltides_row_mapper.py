"""HelltidesRowMapper / HelltidesRow 解析单元测试。"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from d4_types.enums.player_class import PlayerClass

from d4_injestion.domain.serivces.helltides_row_mapper import HelltidesRowMapper
from d4_injestion.domain.value_objects.helltides_row import HelltidesRow

OCCURRED_AT = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)


def make_row(**overrides: Any) -> HelltidesRow:
    """构造一条 helltides 榜单行强类型模型 (可覆盖字段)。"""
    payload: dict[str, Any] = {
        "id": "3a9be422-1563-57d9-88bf-6c5b7c14ba85",
        "rank": 1,
        "filteredRank": 1,
        "playerName": "Resistance",
        "battle_tag": "Resistance#11731",
        "class": "druid",
        "tier": 150,
        "run_time_ms": 121190,
        "run_uuid": "f10c58ee-4675-5c06-8971-d21bcbf7092e",
        "platform": "pc",
        "hardcore": False,
        "ssf": False,
        "client_build_version": "3.1.3.73224",
        "isTopRunByClass": True,
        "skills": ["lightningstorm", "shred"],
        "skillDetails": [
            {
                "id": "lightningstorm",
                "name": "Lightning Storm",
                "type": "Core",
                "skillClass": "druid",
                "sno": 548399,
            }
        ],
        "paragonIDs": [940011, 1028233],
        "talismanIDs": ["Talisman_Seal_MythicUnique_03"],
        "powers": ["Helm_Unique_Druid_102"],
    }
    payload.update(overrides)
    return HelltidesRow.model_validate(payload)


def test_helltides_row_parses_camel_case_aliases() -> None:
    """原始 camelCase 键经 alias 正确落到 snake_case 字段。"""
    row = make_row()

    assert row.player_name == "Resistance"
    assert row.player_class == "druid"
    assert row.filtered_rank == 1
    assert row.is_top_run_by_class is True
    assert row.paragon_ids == [940011, 1028233]
    assert row.skill_details[0].sno == 548399


def test_to_records_maps_fields() -> None:
    """正常行映射: playerName/class/tier/run_time_ms 全部落到记录字段。"""
    records = HelltidesRowMapper().to_records([make_row()], OCCURRED_AT)

    assert len(records) == 1
    record = records[0]
    assert record.player_name == "Resistance"
    assert record.player_class is PlayerClass.DRUID
    assert record.tier == 150
    assert record.duration_ms == 121190
    assert record.occurred_at == OCCURRED_AT


def test_to_records_skips_row_beyond_duration_constraint() -> None:
    """超出 duration_ms 上限 (600000) 的行被跳过, 不影响其余行。"""
    records = HelltidesRowMapper().to_records(
        [make_row(run_time_ms=700_000), make_row(playerName="Liam")],
        OCCURRED_AT,
    )

    assert [r.player_name for r in records] == ["Liam"]


def test_to_records_skips_unknown_class() -> None:
    """未知职业的行被跳过。"""
    records = HelltidesRowMapper().to_records(
        [make_row(**{"class": "wizard"})],
        OCCURRED_AT,
    )

    assert records == []


def test_to_records_maps_all_player_classes() -> None:
    """helltides 全部 8 个小写职业名均可映射。"""
    classes = [
        "barbarian",
        "druid",
        "necromancer",
        "paladin",
        "rogue",
        "sorcerer",
        "spiritborn",
        "warlock",
    ]
    rows = [make_row(playerName=f"p{i}", **{"class": c}) for i, c in enumerate(classes)]

    records = HelltidesRowMapper().to_records(rows, OCCURRED_AT)

    assert [r.player_class for r in records] == [
        PlayerClass[c.upper()] for c in classes
    ]


def test_helltides_row_drops_none_skill_slots() -> None:
    """真实数据中 skills/skillDetails 数组含 null 空槽位, 解析时应被过滤。"""
    row = make_row(
        skills=["lightningstorm", None, "shred"],
        skillDetails=[
            {
                "id": "lightningstorm",
                "name": "Lightning Storm",
                "type": "Core",
                "skillClass": "druid",
                "sno": 548399,
            },
            None,
        ],
    )

    assert row.skills == ["lightningstorm", "shred"]
    assert len(row.skill_details) == 1


def test_helltides_row_rejects_missing_required_field() -> None:
    """缺少必填字段的原始载荷解析失败 (由适配器层拦截)。"""
    with pytest.raises(ValueError):  # noqa: PT011  (pydantic.ValidationError 子类)
        HelltidesRow.model_validate({"id": "x", "rank": 1})
