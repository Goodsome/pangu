"""榜单整页截图引用值对象。"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import ConfigDict, Field

from d4_types.enums.player_class import PlayerClass
from foundation.building_blocks.value_object import ValueObject


class LeaderboardScreenshot(ValueObject):
    """一张榜单整页截图的定位信息。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    path: Path = Field(..., description="截图文件路径")
    player_class: PlayerClass = Field(..., description="截图所属职业 (目录名)")
    page: int = Field(..., ge=1, description="榜单页码 (文件名解析)")
