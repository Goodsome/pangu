from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.domain.aggregates.entry import Entry


def update_entry_from_dto(entry: Entry, _dto: EntryDto) -> Entry:
    return entry
