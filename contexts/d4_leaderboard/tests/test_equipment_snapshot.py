import json
from pathlib import Path

from d4_leaderboard.domain.enums.equipment_base_type import EquipmentBaseType
from d4_leaderboard.domain.enums.equipment_rarity import EquipmentRarity
from d4_leaderboard.domain.enums.equipment_slot import EquipmentSlot
from d4_leaderboard.domain.enums.socket_kind import SocketKind
from d4_leaderboard.domain.value_objects.affix import Affix
from d4_leaderboard.domain.value_objects.aspect_power import AspectPower
from d4_leaderboard.domain.value_objects.equipment import Equipment
from d4_leaderboard.domain.value_objects.paragon import (
    ParagonBoard,
    ParagonGlyph,
)
from d4_leaderboard.domain.value_objects.skill import Skill, SkillModifier
from d4_leaderboard.domain.value_objects.socket import Socket
from d4_leaderboard.domain.value_objects.talisman import (
    TalismanAffix,
    TalismanCharm,
    TalismanSeal,
    TalismanSnapshot,
)
from foundation.building_blocks.value_object import ValueObject


def test_value_object_inheritance():
    """验证所有快照值对象均继承自 foundation.building_blocks.value_object.ValueObject"""
    assert issubclass(Equipment, ValueObject)
    assert issubclass(Affix, ValueObject)
    assert issubclass(Socket, ValueObject)
    assert issubclass(AspectPower, ValueObject)
    assert issubclass(Skill, ValueObject)
    assert issubclass(SkillModifier, ValueObject)
    assert issubclass(ParagonBoard, ValueObject)
    assert issubclass(ParagonGlyph, ValueObject)
    assert issubclass(TalismanSnapshot, ValueObject)
    assert issubclass(TalismanSeal, ValueObject)
    assert issubclass(TalismanCharm, ValueObject)


def test_equipment_and_affix_instantiation():
    affix = Affix(
        affix_id=1829570,
        codename="S04_CoreStat_Strength",
        stat_type="Strength",
        is_greater=True,
    )
    socket = Socket(
        id=2089875, kind=SocketKind.RUNE, codename="Rune_Condition_OnCCEnemy"
    )
    aspect = AspectPower(
        id=1489569, codename="Helm_Unique_Barb_100", is_transfigured=False
    )

    eq = Equipment(
        item_id=1489566,
        codename="Helm_Unique_Barb_100",
        slot=EquipmentSlot.HELM,
        base_type=EquipmentBaseType.HELM,
        rarity=EquipmentRarity.MYTHIC_UNIQUE,
        item_power=900,
        is_ancestral=True,
        statlines=[affix],
        sockets=[socket],
        aspect_power=aspect,
    )

    assert eq.slot == EquipmentSlot.HELM
    assert eq.rarity == EquipmentRarity.MYTHIC_UNIQUE
    assert eq.statlines[0].is_greater is True
    assert eq.sockets[0].kind == SocketKind.RUNE
    assert eq.display_type == "Ancestral Mythic Unique Helm"


def test_parse_one_run_json_simplified_snapshots():
    """验证从 one_run.json 解析最新精简后的 Skills(含3个选项), ParagonBoards 及 Talismans 快照"""
    json_path = Path(__file__).parent.parent / "data" / "one_run.json"
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # 1. 解析带选项分支的技能 skillsSNO
    raw_skills_sno = data.get("skillsSNO", [])
    skills = [
        Skill(
            sno=item["sno"],
            codename=item["id"],
            name=item["name"],
            modifiers=[
                SkillModifier(
                    name=mod["name"],
                    is_main=mod.get("is_main", False),
                    bit=mod.get("bit"),
                )
                for mod in item.get("modifiers", [])
            ],
        )
        for item in raw_skills_sno
    ]

    # 2. 解析精简后的巅峰盘 ParagonBoard (包含嵌入的雕文)
    raw_paragon = data.get("paragon", {})
    paragon_boards = [
        ParagonBoard(
            sno=b["sno"],
            codename=b["codename"],
            legendary_node=b.get("legendary_node"),
            glyph=(
                ParagonGlyph(
                    sno=b["glyph"]["sno"],
                    name=b["glyph"]["name"],
                )
                if b.get("glyph")
                else None
            ),
        )
        for b in raw_paragon.get("boards", [])
    ]

    # 3. 解析精简后的护符系统
    raw_talismans = data.get("talismans", {})
    raw_seal = raw_talismans.get("seal")
    talisman_snapshot = TalismanSnapshot(
        seal=(
            TalismanSeal(
                codename=raw_seal["codename"],
                name=raw_seal["name"],
                rarity=raw_seal["rarity"],
                statlines=[
                    TalismanAffix(
                        codename=s["codename"],
                        stat_type=s["stat_type"],
                        is_greater=s.get("is_greater", False),
                        is_mythic=s.get("is_mythic", False),
                        is_set_bonus=s.get("is_set_bonus", False),
                    )
                    for s in raw_seal.get("statlines", [])
                ],
            )
            if raw_seal
            else None
        ),
        charms=[
            TalismanCharm(
                codename=c["codename"],
                name=c["name"],
                rarity=c["rarity"],
                set_name=c["set"]["name"] if c.get("set") else None,
                statlines=[
                    TalismanAffix(
                        codename=s["codename"],
                        stat_type=s["stat_type"],
                        is_greater=s.get("is_greater", False),
                    )
                    for s in c.get("statlines", [])
                ],
            )
            for c in raw_talismans.get("charms", [])
        ],
        sets=raw_talismans.get("sets", []),
    )

    # 断言结构
    assert len(skills) == 6
    assert skills[0].codename == "wrathoftheberserker"
    assert len(skills[0].modifiers) == 3  # 包含了3个强化选项分支！
    assert skills[0].modifiers[0].name == "Full Throttle"

    assert len(paragon_boards) == 5
    assert paragon_boards[0].glyph.name == "Brawl"
    assert paragon_boards[1].legendary_node == "Carnage"

    assert talisman_snapshot.seal.name == "Seal of the Diamond Mind"
    assert len(talisman_snapshot.charms) == 6
    assert talisman_snapshot.charms[0].set_name == "Berserker's Crucible"
