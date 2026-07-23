"""vision_stream 门面层。

统一暴露对外 API、数据模型、异常以及契约接口。
"""

from vision_stream.backends import Win32DXGIBackend, Win32PrintWindowBackend
from vision_stream.constants import CaptureStrategy, ColorFormat
from vision_stream.exceptions import (
    BackendError,
    CaptureFailedError,
    DXGIError,
    UnsupportedPlatformError,
    VisionStreamError,
    WindowNotFoundError,
)
from vision_stream.interfaces import IWindowVisionBackend
from vision_stream.models import HWND, ImageBytes, ImageResult, Region

__all__ = [
    # 统一接口契约
    "IWindowVisionBackend",
    # 数据模型与类型
    "Region",
    "ImageResult",
    "HWND",
    "ImageBytes",
    "ColorFormat",
    "CaptureStrategy",
    # 异常定义
    "VisionStreamError",
    "BackendError",
    "WindowNotFoundError",
    "CaptureFailedError",
    "DXGIError",
    "UnsupportedPlatformError",
    # 实现层 Backend
    "Win32PrintWindowBackend",
    "Win32DXGIBackend",
]
