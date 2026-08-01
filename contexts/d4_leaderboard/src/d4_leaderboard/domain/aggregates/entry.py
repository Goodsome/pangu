from datetime import datetime

from pydantic import Field

from d4_leaderboard.domain.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.domain.value_objects.equipment import Equipment
from d4_leaderboard.domain.value_objects.paragon import ParagonBoard
from d4_leaderboard.domain.value_objects.skill import Skill
from d4_leaderboard.domain.value_objects.talisman import TalismanSnapshot
from foundation.building_blocks.aggregate_root import AggregateRoot


class Entry(AggregateRoot[EntryId]):
    player_name: str
    player_class: PlayerClass
    tier: int = Field(..., ge=1, le=150)
    duration_ms: int = Field(..., ge=0, le=600000)
    occurred_at: datetime

    # 配装与构筑快照
    equipment: list[Equipment] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    paragon_boards: list[ParagonBoard] = Field(default_factory=list)
    talismans: TalismanSnapshot | None = Field(default=None)
