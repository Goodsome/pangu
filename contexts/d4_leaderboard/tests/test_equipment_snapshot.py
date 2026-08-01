import json
from datetime import datetime, timezone
from pathlib import Path

from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.enums.equipment_base_type import EquipmentBaseType
from d4_leaderboard.domain.enums.equipment_rarity import EquipmentRarity
from d4_leaderboard.domain.enums.equipment_slot import EquipmentSlot
from d4_leaderboard.domain.enums.player_class import PlayerClass
from d4_leaderboard.domain.enums.socket_kind import SocketKind
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.domain.value_objects.affix import Affix
from d4_leaderboard.domain.value_objects.aspect_power import AspectPower
from d4_leaderboard.domain.value_objects.equipment import Equipment
from d4_leaderboard.domain.value_objects.socket import Socket
from d4_leaderboard.infrastructure.persistence.mappers.entry_mapper import (
    entry_entity_to_model,
    entry_model_to_entity,
)
from foundation.building_blocks.value_object import ValueObject


def test_value_object_inheritance():
    """验证所有快照值对象均继承自 foundation.building_blocks.value_object.ValueObject"""
    assert issubclass(Equipment, ValueObject)
    assert issubclass(Affix, ValueObject)
    assert issubclass(Socket, ValueObject)
    assert issubclass(AspectPower, ValueObject)


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


def test_parse_one_run_json_equipments():
    """从 one_run.json 实际数据解析装备快照"""
    json_path = Path(__file__).parent.parent / "data" / "one_run.json"
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    raw_equipments = data.get("equipment", [])
    equipments = []
    for item in raw_equipments:
        eq = Equipment(
            item_id=item["item_id"],
            codename=item["codename"],
            slot=item["slot"],
            base_type=item["base_type"],
            rarity=item["rarity"],
            item_power=item["item_power"],
            is_ancestral=item.get("is_ancestral", False),
            statlines=[
                Affix(
                    affix_id=s.get("affix_id"),
                    codename=s.get("codename", ""),
                    stat_type=s.get("stat_type", ""),
                    is_greater=s.get("is_greater", False),
                    is_temper=s.get("is_temper", False),
                    is_rerolled=s.get("is_rerolled", False),
                    is_transfigured=s.get("is_transfigured", False),
                    is_masterwork_crit=s.get("is_masterwork_crit", False),
                )
                for s in item.get("statlines", [])
            ],
            sockets=[
                Socket(
                    id=sk["id"],
                    kind=sk["kind"],
                    codename=sk["codename"],
                )
                for sk in item.get("sockets", [])
            ],
            aspect_power=(
                AspectPower(
                    id=item["aspect_power"]["id"],
                    codename=item["aspect_power"]["codename"],
                    category=item["aspect_power"].get("category", 0),
                    is_transfigured=item["aspect_power"].get("is_transfigured", False),
                )
                if item.get("aspect_power")
                else None
            ),
        )
        equipments.append(eq)

    entry = Entry(
        id=EntryId.create(),
        player_name="rob#2628",
        player_class=PlayerClass.BARBARIAN,
        tier=148,
        duration_ms=547000,
        occurred_at=datetime.now(timezone.utc),
        equipment=equipments,
    )

    assert len(entry.equipment) == len(raw_equipments)
    assert entry.equipment[0].slot == EquipmentSlot.HELM

    # 测试 ORM 模型映射转换
    model = entry_entity_to_model(entry)
    assert len(model.equipments) == len(raw_equipments)
    assert model.equipments[0].slot == EquipmentSlot.HELM

    # 还原为实体
    reconstituted = entry_model_to_entity(model)
    assert len(reconstituted.equipment) == len(raw_equipments)
    assert reconstituted.equipment[0].slot == EquipmentSlot.HELM
