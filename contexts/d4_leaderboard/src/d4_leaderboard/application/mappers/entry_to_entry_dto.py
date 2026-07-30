from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.domain.aggregates.entry import Entry


def entry_to_entry_dto(_entry: Entry) -> EntryDto:
    return EntryDto()
