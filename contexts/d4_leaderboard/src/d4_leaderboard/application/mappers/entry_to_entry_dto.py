from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.application.dtos.entry_dto import EntryDto


def entry_to_entry_dto(entry: Entry) -> EntryDto:
    return EntryDto(
        id=entry.id.value,
        name=entry.name,
    )
