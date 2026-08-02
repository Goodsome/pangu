"""mhxy_client: 梦幻西游 客户端 SDK 模块。"""

from mhxy_client.client import MhxyClient
from mhxy_client.exceptions import MhxyClientError, WindowNotFoundError
from mhxy_client.factory import (
    create_mhxy_client_by_index,
    create_mhxy_client_for_rect,
    create_mhxy_clients,
    find_mhxy_hwnds,
    find_mhxy_window_rects,
    sort_window_rects,
)
from mhxy_client.models import (
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
    RelativeRegion,
    WindowRectInfo,
)
from client_core import Window
from sys_input import MouseButton, VirtualKeyCode

__all__ = [
    "ImageFrame",
    "MatchResult",
    "MhxyClient",
    "MhxyClientError",
    "MouseButton",
    "OcrResult",
    "Point",
    "Region",
    "RelativeRegion",
    "VirtualKeyCode",
    "Window",
    "WindowNotFoundError",
    "WindowRectInfo",
    "create_mhxy_client_by_index",
    "create_mhxy_client_for_rect",
    "create_mhxy_clients",
    "find_mhxy_hwnds",
    "find_mhxy_window_rects",
    "sort_window_rects",
]
