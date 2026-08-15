"""HelltidesBuildMapper 映射单元测试 (载荷复用 run detail 真实样例)。"""

from __future__ import annotations

from datetime import UTC, datetime

from d4_types.enums.player_class import PlayerClass

from d4_injestion.domain.serivces.helltides_build_mapper import HelltidesBuildMapper
from d4_injestion.domain.value_objects.helltides_run_detail import HelltidesRunDetail
from d4_injestion.domain.value_objects.leaderboard_build import EquipmentRarity
from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord

from test_helltides_run_detail import make_run_payload

_OCCURRED_AT = datetime(2026, 8, 15, tzinfo=UTC)


def make_base_record() -> LeaderboardRecord:
    """构造榜单行映射产物的基础 record (不含 build 数据)。"""
    return LeaderboardRecord(
        player_name="Resistance",
        player_class=PlayerClass.DRUID,
        tier=150,
        duration_ms=121190,
        occurred_at=_OCCURRED_AT,
    )


def test_build_mapper_enriches_record() -> None:
    """build 数据回填: 基础字段不变, 裁剪字段不出现, 原 record 不被修改。"""
    record = make_base_record()
    detail = HelltidesRunDetail.model_validate(make_run_payload())

    enriched = HelltidesBuildMapper().to_record(record, detail)

    # 原 record 为 frozen, 不携带 build 数据
    assert record.equipment == []
    assert record.talismans is None
    # 基础字段保持
    assert enriched.player_name == "Resistance"
    assert enriched.tier == 150

    helm = enriched.equipment[0]
    assert helm.slot == 288
    assert helm.rarity is EquipmentRarity.MYTHIC_UNIQUE
    assert helm.aspect_power is not None
    assert helm.aspect_power.codename == "Helm_Unique_Druid_102"
    assert [socket.kind for socket in helm.sockets] == ["rune", "gem"]

    skill = enriched.skills[0]
    assert skill.sno == 548399
    assert skill.codename == "lightningstorm"
    assert skill.modifiers[0].is_main is True

    starting, mounted = enriched.paragon_boards
    assert starting.glyph is not None
    assert starting.glyph.name == "Keeper"
    assert mounted.legendary_node == "Lust for Carnage"

    assert enriched.talismans is not None
    assert enriched.talismans.seal is not None
    assert enriched.talismans.seal.rarity is EquipmentRarity.MYTHIC
    charm = enriched.talismans.charms[0]
    assert charm.set_name is None  # 样例套装无 name, bonuses 被裁剪


def test_build_mapper_wire_payload_roundtrip() -> None:
    """注入 wire 契约: enriched payload 含 build 字段, 基础 record 不含。"""
    detail = HelltidesRunDetail.model_validate(make_run_payload())
    enriched = HelltidesBuildMapper().to_record(make_base_record(), detail)

    payload = enriched.model_dump(mode="json", exclude_unset=True)
    assert set(payload) == {
        "player_name",
        "player_class",
        "tier",
        "duration_ms",
        "occurred_at",
        "equipment",
        "skills",
        "paragon_boards",
        "talismans",
    }
    # 枚举序列化为服务端契约取值
    assert payload["equipment"][0]["rarity"] == "Mythic Unique"
    assert payload["equipment"][0]["slot"] == 288
    # 裁剪字段不下发
    assert "item_type" not in payload["equipment"][0]
    assert "category" not in payload["equipment"][0]["statlines"][0]
    assert "known" not in payload["skills"][0]["modifiers"][0]

    base_payload = make_base_record().model_dump(mode="json", exclude_unset=True)
    assert "equipment" not in base_payload
    assert "talismans" not in base_payload


def test_equipment_rarity_tolerant_parsing() -> None:
    """稀有度镜像枚举容忍大小写/空格差异。"""
    assert EquipmentRarity("mythic unique") is EquipmentRarity.MYTHIC_UNIQUE
    assert EquipmentRarity("set") is EquipmentRarity.SET
