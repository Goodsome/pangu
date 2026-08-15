"""HelltidesRunDetail 强类型解析单元测试 (载荷取自真实 getRun 响应的精简版)。"""

from __future__ import annotations

from typing import Any

from d4_injestion.domain.value_objects.helltides_run_detail import HelltidesRunDetail


def make_run_payload() -> dict[str, Any]:
    """构造覆盖全部嵌套结构的精简 getRun 载荷。"""
    return {
        "id": "3a9be422-1563-57d9-88bf-6c5b7c14ba85",
        "run_uuid": "f10c58ee-4675-5c06-8971-d21bcbf7092e",
        "slot_id": "3a9be422-1563-57d9-88bf-6c5b7c14ba85",
        "playerName": "Resistance",
        "battle_tag": "Resistance#11731",
        "normalized_battle_tag": "resistance#11731",
        "class": "druid",
        "tier": 150,
        "run_time_ms": 121190,
        "runTime": {"minutes": 2, "seconds": 1, "milliseconds": 190},
        "runCreatedAt": "2026-08-13T19:17:54.794Z",
        "syncedAt": {"_seconds": 1786762391, "_nanoseconds": 321762000},
        "platform": "pc",
        "hardcore": False,
        "ssf": False,
        "active": True,
        "entity_id": "696563387",
        "owner_hero_id": "1a418ce0-74a7-11f1-8277-59a91d74d442",
        "client_build_version": "3.1.3.73224",
        "powers": ["Helm_Unique_Druid_102"],
        "skills": ["lightningstorm"],
        "skillsSNO": [
            {
                "name": "Lightning Storm",
                "id": "lightningstorm",
                "sno": 548399,
                "modifiers": [
                    {
                        "is_main": True,
                        "name": "Hero of the Storm",
                        "bit": 2,
                        "known": True,
                    },
                    {
                        "is_main": False,
                        "name": "Additional Strikes",
                        "bit": 4,
                        "known": True,
                    },
                ],
            }
        ],
        "paragonIDs": [940011, 1028233],
        "paragon": {
            "legendary_nodes": ["Lust for Carnage"],
            "boards": [
                {
                    "sno": 940011,
                    "codename": "Paragon_Druid_00",
                    "slot": 0,
                    "is_starting_board": True,
                    "legendary_node": None,
                    "legendary_icon": None,
                    "glyph": {
                        "level": 150,
                        "name": "Keeper",
                        "icon": "glyph_icon_3.png",
                        "sno": 1028233,
                    },
                },
                {
                    "sno": 939984,
                    "codename": "Paragon_Druid_04",
                    "slot": 1,
                    "is_starting_board": False,
                    "legendary_node": "Lust for Carnage",
                    "legendary_icon": "board_939984.png",
                    "glyph": None,
                },
            ],
            "glyphs": [
                {
                    "icon": "glyph_icon_3.png",
                    "name": "Keeper",
                    "level": 150,
                    "board_slot": 0,
                    "board_legendary": None,
                    "sno": 1028233,
                }
            ],
        },
        "talismanIDs": [
            "Talisman_Seal_MythicUnique_03",
            "Talisman_Charm_Set_Druid_03_05",
        ],
        "talismans": {
            "seal": {
                "codename": "Talisman_Seal_MythicUnique_03",
                "name": "Seal of the Diamond Mind",
                "rarity": "Mythic",
                "greaterAffixCount": 0,
                "iconUrl": "https://images.helltides.com/icons/x.png",
                "statlines": [
                    {
                        "stat_type": "Damage",
                        "codename": "Talisman_SealAffix_Normal_Damage_All",
                        "is_greater": False,
                        "is_mythic": False,
                        "is_set_bonus": False,
                    },
                    {
                        "stat_type": "Skill Rank Bonus Wolves",
                        "codename": "Talisman_SealAffix_Set_Druid_05",
                        "is_greater": False,
                        "is_mythic": False,
                        "is_set_bonus": True,
                    },
                ],
            },
            "charms": [
                {
                    "codename": "Talisman_Charm_Set_Druid_03_05",
                    "name": "Berú of the Storm Shepherd",
                    "rarity": "Set",
                    "power": None,
                    "set": {
                        "bonuses": [
                            {
                                "pieces": 2,
                                "desc": "<span>grant stacks</span>",
                                "sno": 2294631,
                            }
                        ]
                    },
                    "statlines": [
                        {
                            "stat_type": "Werewolf Skill Ranks",
                            "codename": "Talisman_Charm_SkillRankBonus_Druid",
                            "is_greater": True,
                        }
                    ],
                }
            ],
        },
        "equipment": [
            {
                "item_id": 2081129,
                "codename": "Helm_Unique_Druid_102",
                "slot": 288,
                "base_type": "Helm",
                "item_type": "Ancestral Mythic Unique Helm",
                "rarity": "Mythic Unique",
                "item_power": 900,
                "is_ancestral": True,
                "statlines": [
                    {
                        "affix_id": 1829574,
                        "stat_type": "Willpower",
                        "codename": "S04_CoreStat_Willpower",
                        "category": 0,
                        "is_greater": True,
                        "is_rerolled": False,
                        "is_masterwork_crit": False,
                        "is_transfigured": False,
                        "is_temper": False,
                    },
                    {
                        "affix_id": 1862295,
                        "stat_type": "Maximum Life",
                        "codename": "Tempered_Generic_LifeMax_Tier3",
                        "category": 4,
                        "is_greater": False,
                        "is_rerolled": False,
                        "is_masterwork_crit": False,
                        "is_transfigured": False,
                        "is_temper": True,
                    },
                ],
                "sockets": [
                    {"id": 2294631, "kind": "rune", "codename": "Rune_Name_01"},
                    {"id": 123, "kind": "gem", "codename": "Gem_Name_01"},
                ],
                "aspect_power": {
                    "id": 2224,
                    "codename": "Helm_Unique_Druid_102",
                    "category": 0,
                    "is_transfigured": False,
                },
            },
            {
                "item_id": 2081130,
                "codename": "Chest_Rare_Generic_Crafted028",
                "slot": 304,
                "item_type": "Ancestral Rare Chest Armor",
                "rarity": "Rare",
                "item_power": 900,
                "is_ancestral": True,
                "statlines": [],
                "sockets": [],
                "aspect_power": None,
            },
        ],
    }


def test_run_detail_parses_top_level_aliases() -> None:
    """顶层字段: camelCase/关键字 class/下划线前缀时间戳均正确落位。"""
    run = HelltidesRunDetail.model_validate(make_run_payload())

    assert run.player_name == "Resistance"
    assert run.player_class == "druid"
    assert run.tier == 150
    assert run.run_time_ms == 121190
    assert run.run_time is not None
    assert run.run_time.minutes == 2  # type: ignore[union-attr]
    assert run.run_created_at is not None
    assert run.run_created_at.year == 2026  # type: ignore[union-attr]
    assert run.synced_at is not None
    assert run.synced_at.seconds == 1786762391  # type: ignore[union-attr]


def test_run_detail_parses_equipment_nested_models() -> None:
    """装备嵌套: 词缀/插槽/威能强类型解析。"""
    run = HelltidesRunDetail.model_validate(make_run_payload())

    assert len(run.equipment) == 2
    helm = run.equipment[0]
    assert helm.codename == "Helm_Unique_Druid_102"
    assert helm.slot == 288
    assert helm.is_ancestral is True
    assert len(helm.statlines) == 2
    assert helm.statlines[0].is_greater is True
    assert helm.statlines[1].is_temper is True
    assert [s.kind for s in helm.sockets] == ["rune", "gem"]
    assert helm.aspect_power is not None
    assert helm.aspect_power.codename == "Helm_Unique_Druid_102"
    # 无威能装备
    chest = run.equipment[1]
    assert chest.aspect_power is None


def test_run_detail_parses_skills_paragon_talismans() -> None:
    """技能/巅峰/护身符嵌套强类型解析。"""
    run = HelltidesRunDetail.model_validate(make_run_payload())

    skill = run.skills_sno[0]
    assert skill.sno == 548399
    assert skill.modifiers[0].is_main is True
    assert skill.modifiers[0].bit == 2

    assert run.paragon is not None
    starting, mounted = run.paragon.boards
    assert starting.is_starting_board is True
    assert starting.glyph is not None
    assert starting.glyph.name == "Keeper"
    assert mounted.legendary_node == "Lust for Carnage"
    assert mounted.glyph is None

    assert run.talismans is not None
    assert run.talismans.seal is not None
    assert run.talismans.seal.rarity == "Mythic"
    assert run.talismans.seal.greater_affix_count == 0
    charm = run.talismans.charms[0]
    assert charm.rarity == "Set"
    assert charm.set is not None
    assert charm.set.bonuses[0].pieces == 2
    assert charm.statlines[0].is_greater is True


def test_run_detail_tolerates_minimal_payload() -> None:
    """最小载荷 (仅必填字段) 也可解析, 其余字段取默认值。"""
    run = HelltidesRunDetail.model_validate(
        {
            "id": "uuid",
            "playerName": "Someone",
            "class": "barbarian",
            "tier": 130,
            "run_time_ms": 300000,
        }
    )

    assert run.player_class == "barbarian"
    assert run.equipment == []
    assert run.talismans is None
    assert run.paragon is None
    assert run.run_created_at is None
