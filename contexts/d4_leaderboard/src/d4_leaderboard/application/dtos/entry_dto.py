from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from d4_leaderboard.domain.enums.player_class import PlayerClass
from d4_leaderboard.domain.value_objects.equipment import Equipment


class EntryDto(BaseModel):
    id: UUID
    player_name: str
    player_class: PlayerClass
    tier: int
    duration_ms: int
    occurred_at: datetime
    equipment: list[Equipment] = Field(default_factory=list)
