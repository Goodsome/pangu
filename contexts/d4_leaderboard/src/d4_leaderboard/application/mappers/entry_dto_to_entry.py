from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.domain.identities.entry_id import EntryId


def entry_dto_to_entry(dto: EntryDto) -> Entry:
    return Entry(id=EntryId.create())
