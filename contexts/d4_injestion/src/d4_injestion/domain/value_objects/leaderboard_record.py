"""榜单单条记录解析结果值对象。"""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import ConfigDict, Field

from d4_types.enums.player_class import PlayerClass
from foundation.building_blocks.value_object import ValueObject

from d4_injestion.domain.value_objects.leaderboard_build import (
    Equipment,
    ParagonBoard,
    Skill,
    TalismanSnapshot,
)


class LeaderboardRecord(ValueObject):
    """从榜单整页截图中解析出的单条玩家记录 (待注入 d4_leaderboard)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    player_name: str = Field(..., description="玩家名称")
    player_class: PlayerClass = Field(..., description="玩家职业")
    tier: int = Field(..., ge=1, le=150, description="大秘境层数")
    duration_ms: int = Field(..., ge=0, le=600000, description="通关用时 (毫秒)")
    occurred_at: datetime = Field(..., description="通关时间")
    equipment: list[Equipment] = Field(default_factory=list, description="装备快照列表")
    skills: list[Skill] = Field(default_factory=list, description="技能快照列表")
    paragon_boards: list[ParagonBoard] = Field(
        default_factory=list, description="巅峰盘快照列表"
    )
    talismans: TalismanSnapshot | None = Field(default=None, description="护符快照")
