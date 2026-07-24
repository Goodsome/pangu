"""CV 引擎数据层。

定义坐标、矩形区域、模板匹配结果与 OCR 文本识别结果的 Dataclasses 数据结构。
"""

from dataclasses import dataclass, field
from typing import TypeAlias

import numpy as np

# ---------------------------------------------------------------------------
# 类型别名 (TypeAlias)
# ---------------------------------------------------------------------------
MatLike: TypeAlias = np.ndarray


# ---------------------------------------------------------------------------
# Dataclass 数据结构
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Point:
    """二维像素坐标点。"""

    x: int = 0
    y: int = 0


@dataclass(frozen=True)
class Region:
    """矩形区域 (ROI, Region of Interest)。"""

    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @property
    def center(self) -> Point:
        """获取矩形区域中心坐标。"""
        return Point(x=self.x + self.width // 2, y=self.y + self.height // 2)

    @property
    def right(self) -> int:
        """右边界 X 坐标。"""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """下边界 Y 坐标。"""
        return self.y + self.height


@dataclass(frozen=True)
class MatchResult:
    """模板匹配命中结果模型。"""

    score: float
    rect: Region
    center: Point = field(init=False)
    template_name: str | None = None

    def __post_init__(self) -> None:
        """在初始化完成后计算中心坐标。"""
        object.__setattr__(self, "center", self.rect.center)


@dataclass(frozen=True)
class OcrResult:
    """OCR 文本识别与定位结果模型。"""

    text: str
    confidence: float
    rect: Region
    box_points: tuple[Point, Point, Point, Point]
    center: Point = field(init=False)

    def __post_init__(self) -> None:
        """在初始化完成后计算文本框中心坐标。"""
        object.__setattr__(self, "center", self.rect.center)
