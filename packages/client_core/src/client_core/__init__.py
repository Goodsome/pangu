"""client_core 基础客户端与窗口操控抽象库。"""

from client_core.models import (
    BaseRegion,
    Element,
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
    RelativePoint,
    RelativeRegion,
    SplitMode,
    WindowRectInfo,
)
from client_core.window import BaseWindow, Window, activate_window, client_to_screen

__all__ = [
    "BaseRegion",
    "BaseWindow",
    "Element",
    "ImageFrame",
    "MatchResult",
    "OcrResult",
    "Point",
    "Region",
    "RelativePoint",
    "RelativeRegion",
    "SplitMode",
    "Window",
    "WindowRectInfo",
    "activate_window",
    "client_to_screen",
]
