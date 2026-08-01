from typing import ClassVar
from d4_leaderboard.domain.enums.socket_kind import SocketKind
from foundation.building_blocks.value_object import ValueObject
from pydantic import ConfigDict, Field


class Socket(ValueObject):
    """装备插槽 (宝石/符文) 值对象"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    id: int = Field(..., description="插槽嵌入物 ID")
    kind: SocketKind = Field(..., description="插槽种类: gem/rune")
    codename: str = Field(..., description="插槽物程序代号")
