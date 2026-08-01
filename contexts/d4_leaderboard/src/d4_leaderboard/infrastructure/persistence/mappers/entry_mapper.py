from uuid import UUID

from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.enums.equipment_base_type import EquipmentBaseType
from d4_leaderboard.domain.enums.equipment_rarity import EquipmentRarity
from d4_leaderboard.domain.enums.equipment_slot import EquipmentSlot
from d4_leaderboard.domain.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.domain.value_objects.affix import Affix
from d4_leaderboard.domain.value_objects.aspect_power import AspectPower
from d4_leaderboard.domain.value_objects.equipment import Equipment
from d4_leaderboard.domain.value_objects.paragon import ParagonBoard
from d4_leaderboard.domain.value_objects.skill import Skill
from d4_leaderboard.domain.value_objects.socket import Socket
from d4_leaderboard.domain.value_objects.talisman import TalismanSnapshot
from d4_leaderboard.infrastructure.persistence.models.entry_equipment_model import (
    EntryEquipmentModel,
)
from d4_leaderboard.infrastructure.persistence.models.entry_model import (
    EntryModel,
)


def equipment_model_to_vo(eq_model: EntryEquipmentModel) -> Equipment:
    raw_base_type = eq_model.base_type
    if raw_base_type in EquipmentBaseType._value2member_map_:
        base_type: EquipmentBaseType | str = EquipmentBaseType(raw_base_type)
    else:
        base_type = raw_base_type

    return Equipment(
        item_id=eq_model.item_id,
        codename=eq_model.codename,
        slot=EquipmentSlot(eq_model.slot),
        base_type=base_type,
        rarity=EquipmentRarity(eq_model.rarity),
        item_power=eq_model.item_power,
        is_ancestral=eq_model.is_ancestral,
        statlines=[Affix.model_validate(s) for s in (eq_model.statlines or [])],
        sockets=[Socket.model_validate(s) for s in (eq_model.sockets or [])],
        aspect_power=(
            AspectPower.model_validate(eq_model.aspect_power)
            if eq_model.aspect_power
            else None
        ),
    )


def equipment_vo_to_model(vo: Equipment, entry_id: UUID) -> EntryEquipmentModel:
    return EntryEquipmentModel(
        entry_id=entry_id,
        item_id=vo.item_id,
        codename=vo.codename,
        slot=int(vo.slot),
        base_type=str(vo.base_type),
        rarity=vo.rarity,
        item_power=vo.item_power,
        is_ancestral=vo.is_ancestral,
        statlines=[s.model_dump() for s in vo.statlines],
        sockets=[s.model_dump() for s in vo.sockets],
        aspect_power=vo.aspect_power.model_dump() if vo.aspect_power else None,
    )


def entry_model_to_entity(model: EntryModel) -> Entry:
    return Entry(
        id=EntryId.reconstitute(model.id),
        player_name=model.player_name,
        player_class=PlayerClass(model.player_class),
        tier=model.tier,
        duration_ms=model.duration_ms,
        occurred_at=model.occurred_at,
        equipment=[equipment_model_to_vo(eq) for eq in (model.equipments or [])],
        skills=[Skill.model_validate(s) for s in (model.skills or [])],
        paragon_boards=[
            ParagonBoard.model_validate(b) for b in (model.paragon_boards or [])
        ],
        talismans=(
            TalismanSnapshot.model_validate(model.talismans)
            if model.talismans
            else None
        ),
    )


def entry_entity_to_model(entity: Entry) -> EntryModel:
    entry_id = entity.id.value
    return EntryModel(
        id=entry_id,
        player_name=entity.player_name,
        player_class=entity.player_class,
        tier=entity.tier,
        duration_ms=entity.duration_ms,
        occurred_at=entity.occurred_at,
        equipments=[equipment_vo_to_model(eq, entry_id) for eq in entity.equipment],
        skills=[s.model_dump() for s in entity.skills],
        paragon_boards=[b.model_dump() for b in entity.paragon_boards],
        talismans=entity.talismans.model_dump() if entity.talismans else None,
    )


def entry_model_to_entry_dto(model: EntryModel) -> EntryDto:
    return EntryDto(
        id=model.id,
        player_name=model.player_name,
        player_class=model.player_class,
        tier=model.tier,
        duration_ms=model.duration_ms,
        occurred_at=model.occurred_at,
        equipment=[equipment_model_to_vo(eq) for eq in (model.equipments or [])],
        skills=[Skill.model_validate(s) for s in (model.skills or [])],
        paragon_boards=[
            ParagonBoard.model_validate(b) for b in (model.paragon_boards or [])
        ],
        talismans=(
            TalismanSnapshot.model_validate(model.talismans)
            if model.talismans
            else None
        ),
    )
