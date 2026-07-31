from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.infrastructure.persistence.models.entry_model import EntryModel


def entry_model_to_entity(model: EntryModel) -> Entry:
    return Entry(
        id=EntryId.reconstitute(model.id),
        name=model.name,
    )


def entry_entity_to_model(entity: Entry) -> EntryModel:
    return EntryModel(
        id=entity.id.value,
        name=entity.name,
    )


def entry_model_to_entry_dto(model: EntryModel) -> EntryDto:
    return EntryDto(
        id=model.id,
        name=model.name,
    )
