from typing import ClassVar

from pydantic import ConfigDict, Field

from foundation.building_blocks.value_object import ValueObject


class ParagonGlyph(ValueObject):
    """巅峰雕文值对象 (精简版)"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    sno: int = Field(..., description="雕文 SNO ID")
    name: str = Field(..., description="雕文显示名称")


class ParagonBoard(ValueObject):
    """巅峰盘值对象 (精简版)"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    sno: int = Field(..., description="巅峰盘 SNO ID")
    codename: str = Field(..., description="巅峰盘代号")
    legendary_node: str | None = Field(default=None, description="激活的传奇节点名称")
    glyph: ParagonGlyph | None = Field(default=None, description="盘上嵌入的雕文")
