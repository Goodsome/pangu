from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.infrastructure.persistence.models.entry_model import EntryModel


def entry_model_to_entity(model: EntryModel) -> Entry:
    return Entry(
        id=EntryId.reconstitute(model.id),
        player_name=model.player_name,
        player_class=PlayerClass(model.player_class),
        tier=model.tier,
        duration_ms=model.duration_ms,
        occurred_at=model.occurred_at,
    )


def entry_entity_to_model(entity: Entry) -> EntryModel:
    return EntryModel(
        id=entity.id.value,
        player_name=entity.player_name,
        player_class=entity.player_class,
        tier=entity.tier,
        duration_ms=entity.duration_ms,
        occurred_at=entity.occurred_at,
    )


def entry_model_to_entry_dto(model: EntryModel) -> EntryDto:
    return EntryDto(
        id=model.id,
        player_name=model.player_name,
        player_class=model.player_class,
        tier=model.tier,
        duration_ms=model.duration_ms,
        occurred_at=model.occurred_at,
    )
