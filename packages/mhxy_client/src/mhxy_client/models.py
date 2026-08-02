"""mhxy_client 领域数据模型层与防腐转换层 (ACL)。"""

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
import re
from typing import TYPE_CHECKING

import numpy as np

from sys_input import HWND
from sys_input.models import Point as SysInputPoint
from vision_stream.models import (
    ImageResult as VisionImageResult,
    Region as VisionRegion,
)

if TYPE_CHECKING:
    from cv_engine.models import (
        MatchResult as CVMatchResult,
        OcrResult as CVOcrResult,
        Point as CVPoint,
        Region as CVRegion,
    )

# 梦幻西游客户端真实窗口标题正则解析: 梦幻西游 ONLINE - (畅玩服[天下无双] - 游易幽寒[39200278])
MHXY_TITLE_PATTERN = re.compile(
    r"梦幻西游\s*ONLINE\s*-\s*\((?P<server>.+?)\s*-\s*(?P<role_name>.+?)\[(?P<role_id>\d+)\]\)",
    re.IGNORECASE,
)


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

    @property
    def server_name(self) -> str:
        """从窗口标题中提取的服务器/大区名称 (如 '畅玩服[天下无双]')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("server").strip() if m else ""

    @property
    def role_name(self) -> str:
        """从窗口标题中提取的角色名字 (如 '游易幽寒')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_name").strip() if m else ""

    @property
    def role_id(self) -> str:
        """从窗口标题中提取的角色数字 ID (如 '39200278')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_id").strip() if m else ""


@dataclass(frozen=True)
class Point:
    """mhxy_client 领域二维像素坐标点。"""

    x: int = 0
    y: int = 0

    def to_sys_input(self) -> SysInputPoint:
        """转换为 sys_input 库的 Point 实例。"""
        return SysInputPoint(x=self.x, y=self.y)

    def to_cv_engine(self) -> "CVPoint":
        """转换为 cv_engine 库的 Point 实例。"""
        from cv_engine.models import Point as CVPoint

        return CVPoint(x=self.x, y=self.y)

    @classmethod
    def from_cv_engine(cls, pt: "CVPoint") -> "Point":
        """从 cv_engine 库的 Point 转换为 mhxy_client Point。"""
        return cls(x=pt.x, y=pt.y)


@dataclass(frozen=True)
class Region:
    """mhxy_client 领域矩形检索/感知区域 (ROI)。"""

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

    def to_cv_engine(self) -> "CVRegion":
        """转换为 cv_engine 库的 Region 实例。"""
        from cv_engine.models import Region as CVRegion

        return CVRegion(x=self.x, y=self.y, width=self.width, height=self.height)

    @classmethod
    def from_cv_engine(cls, reg: "CVRegion") -> "Region":
        """从 cv_engine 库的 Region 转换为 mhxy_client Region。"""
        return cls(x=reg.x, y=reg.y, width=reg.width, height=reg.height)


@dataclass(frozen=True)
class RelativeRegion:
    """mhxy_client 领域相对百分比检索/感知区域 (0.0 ~ 1.0)。"""

    x: float = 0.0
    y: float = 0.0
    width: float = 1.0
    height: float = 1.0

    def to_absolute(self, window_width: int, window_height: int) -> Region:
        """将相对比例换算为游戏窗口下的绝对像素 Region。"""
        abs_x = int(self.x * window_width)
        abs_y = int(self.y * window_height)
        abs_w = int(self.width * window_width)
        abs_h = int(self.height * window_height)

        # 边界裁剪防溢出
        abs_x = max(0, min(abs_x, window_width))
        abs_y = max(0, min(abs_y, window_height))
        abs_w = max(0, min(abs_w, window_width - abs_x))
        abs_h = max(0, min(abs_h, window_height - abs_y))

        return Region(x=abs_x, y=abs_y, width=abs_w, height=abs_h)


@dataclass
class ImageFrame:
    """mhxy_client 领域图像单帧画面模型。"""

    data: bytes = b""
    width: int = 0
    height: int = 0
    channels: int = 4
    timestamp: float = 0.0
    stride: int = 0
    _mat: np.ndarray[tuple[int, ...], np.dtype[np.uint8]] | None = field(
        default=None, repr=False
    )

    @classmethod
    def from_vision_stream(cls, res: VisionImageResult) -> "ImageFrame":
        """从 vision_stream 的 ImageResult 转换为 mhxy_client ImageFrame。"""
        return cls(
            data=res.data,
            width=res.width,
            height=res.height,
            channels=res.channels,
            timestamp=res.timestamp,
            stride=res.stride,
        )

    @cached_property
    def mat(self) -> np.ndarray[tuple[int, ...], np.dtype[np.uint8]] | None:
        """解构并缓存图像矩阵 (OpenCV MatLike)。"""
        if self._mat is not None:
            return self._mat
        if not self.data or self.width <= 0 or self.height <= 0:
            return None
        nparr = np.frombuffer(self.data, dtype=np.uint8)
        bytes_per_pixel = self.channels
        stride_width = self.stride // bytes_per_pixel
        matrix = nparr.reshape((self.height, stride_width, self.channels))

        return matrix[:, : self.width, :]

    def crop(self, region: Region) -> "ImageFrame":
        """使用 NumPy 矩阵从当前图像帧中精确裁剪出指定 ROI 区域。"""
        if self.mat is None:
            return self

        crop_x = max(0, min(region.x, self.width - 1))
        crop_y = max(0, min(region.y, self.height - 1))
        crop_w = min(region.width, self.width - crop_x)
        crop_h = min(region.height, self.height - crop_y)

        if crop_w <= 0 or crop_h <= 0:
            return ImageFrame()

        cropped_mat = self.mat[crop_y : crop_y + crop_h, crop_x : crop_x + crop_w]
        return ImageFrame(
            data=b"",
            width=crop_w,
            height=crop_h,
            channels=self.channels,
            timestamp=self.timestamp,
            stride=crop_w * self.channels,
            _mat=cropped_mat,
        )

    def save(self, path: str | Path) -> None:
        """将图像帧保存为本地磁盘图片文件。"""
        if self.mat is None:
            return
        import cv2

        save_path = Path(path).resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(save_path), self.mat)


@dataclass(frozen=True)
class MatchResult:
    """mhxy_client 领域模板匹配命中结果。"""

    score: float
    rect: Region
    center: Point = field(init=False)
    template_name: str | None = None

    def __post_init__(self) -> None:
        """计算中心坐标。"""
        object.__setattr__(self, "center", self.rect.center)

    @classmethod
    def from_cv_engine(
        cls, res: "CVMatchResult", offset_x: int = 0, offset_y: int = 0
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
    """mhxy_client 领域 OCR 文本识别与定位结果。"""

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
        cls, res: "CVOcrResult", offset_x: int = 0, offset_y: int = 0
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
