from datetime import datetime
from d4_leaderboard.domain.enums.player_class import PlayerClass
from foundation.building_blocks.aggregate_root import AggregateRoot
from d4_leaderboard.domain.identities.entry_id import EntryId
from pydantic import Field


class Entry(AggregateRoot[EntryId]):
    player_name: str
    player_class: PlayerClass
    tier: int = Field(..., ge=1, le=150)
    duration_ms: int = Field(..., ge=0, le=600000)
    occurred_at: datetime
