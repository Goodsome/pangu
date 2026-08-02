from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.value_objects.equipment import Equipment
from d4_leaderboard.domain.value_objects.paragon import ParagonBoard
from d4_leaderboard.domain.value_objects.skill import Skill
from d4_leaderboard.domain.value_objects.talisman import TalismanSnapshot


class EntryDto(BaseModel):
    id: UUID
    player_name: str
    player_class: PlayerClass
    tier: int
    duration_ms: int
    occurred_at: datetime
    equipment: list[Equipment] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    paragon_boards: list[ParagonBoard] = Field(default_factory=list)
    talismans: TalismanSnapshot | None = Field(default=None)
