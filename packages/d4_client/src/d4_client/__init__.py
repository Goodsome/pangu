"""d4_client 门面层。

暴露 D4Client 聚合根主入口、D4Client 工厂构建函数、D4Window、AutoCalibratingScreen、MainHUD、InventoryPanel、SocialPanel 页面对象以及领域模型。
"""

from d4_client.client import D4Client
from d4_client.factory import (
    WindowRectInfo,
    create_d4_client_by_index,
    create_d4_client_for_rect,
    create_d4_clients,
    find_d4_hwnds,
    find_d4_window_rects,
    sort_window_rects,
)
from d4_client.models import (
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
    RelativeRegion,
)
from d4_client.screens import (
    AutoCalibratingScreen,
    D4Panel,
    InventoryPanel,
    MainHUD,
    SocialPanel,
)
from d4_client.window import D4Window

__all__ = [
    "D4Client",
    "D4Panel",
    "WindowRectInfo",
    "create_d4_clients",
    "create_d4_client_by_index",
    "create_d4_client_for_rect",
    "find_d4_hwnds",
    "find_d4_window_rects",
    "sort_window_rects",
    "D4Window",
    "AutoCalibratingScreen",
    "MainHUD",
    "InventoryPanel",
    "SocialPanel",
    "Point",
    "Region",
    "RelativeRegion",
    "MatchResult",
    "OcrResult",
    "ImageFrame",
]
