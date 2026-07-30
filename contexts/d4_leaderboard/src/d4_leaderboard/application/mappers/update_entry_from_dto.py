from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.application.dtos.entry_dto import EntryDto


def update_entry_from_dto(entry: Entry, dto: EntryDto) -> Entry:
    return entry
