"""client_core 通用领域数据模型层与防腐转换器 (Anti-Corruption Layer)。

定义 client_core 共享的纯数据模型，隔离底层 sys_input, vision_stream, cv_engine 库的数据类型细节。
"""

from dataclasses import dataclass, field
from enum import StrEnum
from functools import cached_property
from pathlib import Path
from typing import Self
import cv2
import numpy as np

from cv_engine import MatLike
from cv_engine.models import (
    MatchResult as CVMatchResult,
    OcrResult as CVOcrResult,
    Point as CVPoint,
    Region as CVRegion,
)
from sys_input import HWND
from sys_input.models import Point as SysInputPoint
from vision_stream.models import (
    ImageResult as VisionImageResult,
    Region as VisionRegion,
)


class SplitMode(StrEnum):
    """矩形区域切分方向模式。"""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


@dataclass(frozen=True)
class BaseRegion:
    """矩形感知区域 (ROI) 基础抽象模型。"""

    x: int | float = 0
    y: int | float = 0
    width: int | float = 0
    height: int | float = 0

    @property
    def right(self) -> int | float:
        """获取右边界 X 坐标。"""
        return self.x + self.width

    @property
    def bottom(self) -> int | float:
        """获取下边界 Y 坐标。"""
        return self.y + self.height

    def split(
        self,
        n: int,
        mode: SplitMode = SplitMode.VERTICAL,
    ) -> list[Self]:
        """按指定方向模式将矩形区域等分为 n 个同类型子矩形区域。

        Args:
            n: 等分的份数，必须大于等于 1。
            mode: 切分模式 Enum (SplitMode.VERTICAL 或 SplitMode.HORIZONTAL)。

        Returns:
            list[Self]: 切分后的子矩形区域列表。

        Raises:
            ValueError: 当 n < 1 或 mode 不在 SplitMode 枚举中抛出异常。
        """
        if n < 1:
            raise ValueError("等分份数 n 必须大于等于 1")

        is_int = (
            isinstance(self.x, int)
            and isinstance(self.y, int)
            and isinstance(self.width, int)
            and isinstance(self.height, int)
        )

        if mode == SplitMode.VERTICAL:
            if is_int:
                return [
                    self.__class__(
                        x=self.x,
                        y=self.y + int(round(i * self.height / n)),
                        width=self.width,
                        height=int(round((i + 1) * self.height / n))
                        - int(round(i * self.height / n)),
                    )
                    for i in range(n)
                ]
            else:
                sub_height = self.height / n
                return [
                    self.__class__(
                        x=self.x,
                        y=self.y + i * sub_height,
                        width=self.width,
                        height=sub_height,
                    )
                    for i in range(n)
                ]
        elif mode == SplitMode.HORIZONTAL:
            if is_int:
                return [
                    self.__class__(
                        x=self.x + int(round(i * self.width / n)),
                        y=self.y,
                        width=int(round((i + 1) * self.width / n))
                        - int(round(i * self.width / n)),
                        height=self.height,
                    )
                    for i in range(n)
                ]
            else:
                sub_width = self.width / n
                return [
                    self.__class__(
                        x=self.x + i * sub_width,
                        y=self.y,
                        width=sub_width,
                        height=self.height,
                    )
                    for i in range(n)
                ]
        else:
            raise ValueError(f"不支持的切分模式: {mode}")


@dataclass(frozen=True)
class Point:
    """二维像素坐标点。"""

    x: int = 0
    y: int = 0

    def to_sys_input(self) -> SysInputPoint:
        """转换为 sys_input 库的 Point 实例。"""
        return SysInputPoint(x=self.x, y=self.y)

    def to_cv_engine(self) -> CVPoint:
        """转换为 cv_engine 库的 Point 实例。"""
        return CVPoint(x=self.x, y=self.y)

    @classmethod
    def from_cv_engine(cls, pt: CVPoint) -> "Point":
        """从 cv_engine 库的 Point 转换。"""
        return cls(x=pt.x, y=pt.y)


@dataclass(frozen=True)
class RelativePoint:
    """相对比例坐标点 (0.0 ~ 1.0)。"""

    x: float = 0.0
    y: float = 0.0

    def to_absolute(self, window_width: int, window_height: int) -> Point:
        """根据给定的窗口物理像素分辨率，转换为绝对像素 Point。"""
        return Point(
            x=int(round(self.x * window_width)),
            y=int(round(self.y * window_height)),
        )

    @classmethod
    def from_absolute(
        cls, point: Point, window_width: int, window_height: int
    ) -> "RelativePoint":
        """从绝对像素 Point 转换为 0.0 ~ 1.0 的 RelativePoint。"""
        if window_width <= 0 or window_height <= 0:
            raise ValueError("window_width 和 window_height 必须大于 0")
        return cls(
            x=point.x / window_width,
            y=point.y / window_height,
        )


@dataclass(frozen=True)
class Region(BaseRegion):
    """矩形检索/感知区域 (ROI)。"""

    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @property
    def center(self) -> Point:
        """获取矩形中心坐标点。"""
        return Point(x=self.x + self.width // 2, y=self.y + self.height // 2)

    def to_vision_stream(self) -> VisionRegion:
        """转换为 vision_stream 库的 Region 实例。"""
        return VisionRegion(x=self.x, y=self.y, width=self.width, height=self.height)

    def to_cv_engine(self) -> CVRegion:
        """转换为 cv_engine 库的 Region 实例。"""
        return CVRegion(x=self.x, y=self.y, width=self.width, height=self.height)

    @classmethod
    def from_cv_engine(cls, rect: CVRegion) -> "Region":
        """从 cv_engine 库的 Region 转换。"""
        return cls(x=rect.x, y=rect.y, width=rect.width, height=rect.height)

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> "Region":
        """从两个坐标点计算包围矩形 Region。"""
        x = min(p1.x, p2.x)
        y = min(p1.y, p2.y)
        width = abs(p1.x - p2.x)
        height = abs(p1.y - p2.y)
        return cls(x=x, y=y, width=width, height=height)


@dataclass(frozen=True)
class RelativeRegion(BaseRegion):
    """相对比例检索/感知区域 (0.0 ~ 1.0)。"""

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @property
    def center(self) -> RelativePoint:
        """获取矩形中心坐标点。"""
        return RelativePoint(x=self.x + self.width / 2.0, y=self.y + self.height / 2.0)

    def to_absolute(self, window_width: int, window_height: int) -> Region:
        """根据给定的窗口物理像素分辨率，转换为绝对像素 Region。"""
        return Region(
            x=int(round(self.x * window_width)),
            y=int(round(self.y * window_height)),
            width=int(round(self.width * window_width)),
            height=int(round(self.height * window_height)),
        )

    @classmethod
    def from_absolute(
        cls, region: Region, window_width: int, window_height: int
    ) -> "RelativeRegion":
        """从绝对像素 Region 转换为 0.0 ~ 1.0 的 RelativeRegion。"""
        if window_width <= 0 or window_height <= 0:
            raise ValueError("window_width 和 window_height 必须大于 0")
        return cls(
            x=region.x / window_width,
            y=region.y / window_height,
            width=region.width / window_width,
            height=region.height / window_height,
        )


@dataclass(frozen=True)
class ImageFrame:
    """图像单帧画面模型。"""

    data: bytes
    width: int
    height: int
    channels: int = 4
    timestamp: float = 0.0
    stride: int = 0

    @classmethod
    def from_vision_stream(cls, res: VisionImageResult) -> "ImageFrame":
        """从 vision_stream 的 ImageResult 转换。"""
        return cls(
            data=res.data,
            width=res.width,
            height=res.height,
            channels=res.channels,
            timestamp=res.timestamp,
            stride=res.stride,
        )

    @cached_property
    def mat(self) -> MatLike:
        nparr = np.frombuffer(self.data, dtype=np.uint8)
        bytes_per_pixel = self.channels
        effective_stride = (
            self.stride if self.stride > 0 else self.width * bytes_per_pixel
        )
        stride_width = effective_stride // bytes_per_pixel
        matrix = nparr.reshape((self.height, stride_width, self.channels))

        return matrix[:, : self.width, :]

    async def save(self, path: Path | str) -> None:
        """将 ImageFrame 异步保存为磁盘图片文件，自动创建父级目录。

        Args:
            path: 目标保存路径 (Path 对象或路径字符串)。

        Raises:
            RuntimeError: 图像保存写入失败。
        """
        import asyncio

        dest_path = Path(path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        mat = self.mat
        if self.channels == 4:
            bgr = cv2.cvtColor(mat, cv2.COLOR_BGRA2BGR)
        else:
            bgr = mat

        loop = asyncio.get_running_loop()
        ok: bool = await loop.run_in_executor(
            None, cv2.imwrite, str(dest_path), bgr
        )
        if not ok:
            raise RuntimeError(f"[ImageFrame.save] 写入图片文件失败: {dest_path}")


@dataclass(frozen=True)
class MatchResult:
    """模板匹配命中结果。"""

    score: float
    rect: Region
    center: Point = field(init=False)
    template_name: str | None = None

    def __post_init__(self) -> None:
        """计算中心坐标。"""
        object.__setattr__(self, "center", self.rect.center)

    @property
    def top_left(self) -> Point:
        """获取左上角坐标。"""
        return Point(x=self.rect.x, y=self.rect.y)

    @classmethod
    def from_cv_engine(
        cls, res: CVMatchResult, offset_x: int = 0, offset_y: int = 0
    ) -> "MatchResult":
        """从 cv_engine 的 MatchResult 转换，支持叠加 ROI 全局偏移。"""
        rect = Region.from_cv_engine(res.rect)
        if offset_x != 0 or offset_y != 0:
            rect = Region(
                x=rect.x + offset_x,
                y=rect.y + offset_y,
                width=rect.width,
                height=rect.height,
            )
        return cls(
            score=res.score,
            rect=rect,
            template_name=res.template_name,
        )


@dataclass(frozen=True)
class OcrResult:
    """OCR 文本识别与定位结果。"""

    text: str
    confidence: float
    rect: Region
    box_points: tuple[Point, Point, Point, Point]
    center: Point = field(init=False)

    def __post_init__(self) -> None:
        """计算中心坐标。"""
        object.__setattr__(self, "center", self.rect.center)

    @classmethod
    def from_cv_engine(
        cls, res: CVOcrResult, offset_x: int = 0, offset_y: int = 0
    ) -> "OcrResult":
        """从 cv_engine 的 OcrResult 转换，支持叠加 ROI 全局偏移。"""
        rect = Region.from_cv_engine(res.rect)
        pts = [Point.from_cv_engine(pt) for pt in res.box_points]

        if offset_x != 0 or offset_y != 0:
            rect = Region(
                x=rect.x + offset_x,
                y=rect.y + offset_y,
                width=rect.width,
                height=rect.height,
            )
            pts = [Point(x=pt.x + offset_x, y=pt.y + offset_y) for pt in pts]

        box_tuple = (pts[0], pts[1], pts[2], pts[3])
        return cls(
            text=res.text,
            confidence=res.confidence,
            rect=rect,
            box_points=box_tuple,
        )


@dataclass(frozen=True)
class Element:
    """与图形 UI 相关的元素。"""

    name: str
    region: Region
    image: ImageFrame


@dataclass(frozen=True)
class WindowRectInfo:
    """窗口绝对位置与句柄结构。"""

    hwnd: HWND
    left: int
    top: int
    right: int
    bottom: int
    client_width: int = 0
    client_height: int = 0
    title: str = ""

    @property
    def window_height(self) -> int:
        """整个窗口外框高度 (含标题栏和边框)。"""
        return self.bottom - self.top

    @property
    def window_width(self) -> int:
        """整个窗口外框宽度 (含标题栏和边框)。"""
        return self.right - self.left

    @property
    def height(self) -> int:
        """客户区高度 (优先使用实际 GetClientRect 高度)。"""
        return self.client_height if self.client_height > 0 else self.window_height

    @property
    def width(self) -> int:
        """客户区宽度 (优先使用实际 GetClientRect 宽度)。"""
        return self.client_width if self.client_width > 0 else self.window_width
