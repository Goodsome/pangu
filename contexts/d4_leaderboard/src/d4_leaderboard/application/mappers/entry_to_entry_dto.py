from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.domain.aggregates.entry import Entry


def entry_to_entry_dto(entry: Entry) -> EntryDto:
    return EntryDto(
        id=entry.id.value,
        player_name=entry.player_name,
        player_class=entry.player_class,
        tier=entry.tier,
        duration_ms=entry.duration_ms,
        occurred_at=entry.occurred_at,
    )
