"""d4_client 领域数据模型层与防腐转换器 (Anti-Corruption Layer)。

定义 d4_client 自有的纯数据模型，隔离底层 sys_input, vision_stream, cv_engine 库的数据类型细节。
"""
from functools import cached_property
import numpy as np

from dataclasses import dataclass, field

from cv_engine import MatLike
from cv_engine.models import (
    MatchResult as CVMatchResult,
    OcrResult as CVOcrResult,
    Point as CVPoint,
    Region as CVRegion,
)
from sys_input.models import Point as SysInputPoint
from vision_stream.models import (
    ImageResult as VisionImageResult,
    Region as VisionRegion,
)


@dataclass(frozen=True)
class Point:
    """d4_client 领域二维像素坐标点。"""

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
        """从 cv_engine 库的 Point 转换为 d4_client Point。"""
        return cls(x=pt.x, y=pt.y)


@dataclass(frozen=True)
class Region:
    """d4_client 领域矩形检索/感知区域 (ROI)。"""

    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @property
    def center(self) -> Point:
        """获取矩形中心坐标点。"""
        return Point(x=self.x + self.width // 2, y=self.y + self.height // 2)

    @property
    def right(self) -> int:
        """获取右边界 X 坐标。"""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """获取下边界 Y 坐标。"""
        return self.y + self.height

    def to_vision_stream(self) -> VisionRegion:
        """转换为 vision_stream 库的 Region 实例。"""
        return VisionRegion(x=self.x, y=self.y, width=self.width, height=self.height)

    def to_cv_engine(self) -> CVRegion:
        """转换为 cv_engine 库的 Region 实例。"""
        return CVRegion(x=self.x, y=self.y, width=self.width, height=self.height)

    @classmethod
    def from_cv_engine(cls, rect: CVRegion) -> "Region":
        """从 cv_engine 库的 Region 转换为 d4_client Region。"""
        return cls(x=rect.x, y=rect.y, width=rect.width, height=rect.height)


@dataclass(frozen=True)
class ImageFrame:
    """d4_client 领域图像单帧画面模型。"""

    data: bytes
    width: int
    height: int
    channels: int = 4
    timestamp: float = 0.0
    stride: int = 0

    @classmethod
    def from_vision_stream(cls, res: VisionImageResult) -> "ImageFrame":
        """从 vision_stream 的 ImageResult 转换为 d4_client ImageFrame。"""
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
        stride_width = self.stride // bytes_per_pixel
        matrix = nparr.reshape((self.height, stride_width, self.channels))
        
        return matrix[:, :self.width, :]


@dataclass(frozen=True)
class MatchResult:
    """d4_client 领域模板匹配命中结果。"""

    score: float
    rect: Region
    center: Point = field(init=False)
    template_name: str | None = None

    def __post_init__(self) -> None:
        """计算中心坐标。"""
        object.__setattr__(self, "center", self.rect.center)

    @classmethod
    def from_cv_engine(cls, res: CVMatchResult) -> "MatchResult":
        """从 cv_engine 的 MatchResult 转换。"""
        return cls(
            score=res.score,
            rect=Region.from_cv_engine(res.rect),
            template_name=res.template_name,
        )


@dataclass(frozen=True)
class OcrResult:
    """d4_client 领域 OCR 文本识别与定位结果。"""

    text: str
    confidence: float
    rect: Region
    box_points: tuple[Point, Point, Point, Point]
    center: Point = field(init=False)

    def __post_init__(self) -> None:
        """计算中心坐标。"""
        object.__setattr__(self, "center", self.rect.center)

    @classmethod
    def from_cv_engine(cls, res: CVOcrResult) -> "OcrResult":
        """从 cv_engine 的 OcrResult 转换。"""
        pts = tuple(Point.from_cv_engine(pt) for pt in res.box_points)
        box_tuple = (pts[0], pts[1], pts[2], pts[3])
        return cls(
            text=res.text,
            confidence=res.confidence,
            rect=Region.from_cv_engine(res.rect),
            box_points=box_tuple,
        )


@dataclass(frozen=True)
class Element:
    name: str
    region: Region
    image: ImageFrame
    