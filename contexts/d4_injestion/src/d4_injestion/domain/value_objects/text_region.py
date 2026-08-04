"""OCR 文本框矩形区域值对象。"""

from __future__ import annotations

from typing import ClassVar

from pydantic import ConfigDict, Field

from foundation.building_blocks.value_object import ValueObject


class TextRegion(ValueObject):
    """OCR 识别到的文本所在矩形区域 (像素坐标)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    x: int = Field(..., ge=0, description="区域左上角 X 坐标")
    y: int = Field(..., ge=0, description="区域左上角 Y 坐标")
    width: int = Field(..., ge=0, description="区域宽度")
    height: int = Field(..., ge=0, description="区域高度")

    @property
    def right(self) -> int:
        """右边界 X 坐标。"""
        ...

    @property
    def bottom(self) -> int:
        """下边界 Y 坐标。"""
        ...

    @property
    def center_y(self) -> int:
        """区域纵向中心 Y 坐标。"""
        ...
