"""视觉流数据层。

定义纯数据结构 (ImageResult, Region) 和类型别名 (HWND, ImageBytes)。
使用 Dataclass 实现。
"""

from dataclasses import dataclass, field
import time
from typing import TypeAlias

from vision_stream.constants import ColorFormat

# ---------------------------------------------------------------------------
# 类型别名 (TypeAlias)
# ---------------------------------------------------------------------------
HWND: TypeAlias = int
ImageBytes: TypeAlias = bytes


# ---------------------------------------------------------------------------
# Dataclass 数据结构
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Region:
    """图像/窗口抓取感兴趣区域 (ROI, Region of Interest)。"""

    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


@dataclass(frozen=True)
class ImageResult:
    """单帧图像抓取结果。"""

    data: bytes
    width: int
    height: int
    channels: int = 4
    color_format: ColorFormat = ColorFormat.BGRA
    timestamp: float = field(default_factory=time.time)
    stride: int = 0
