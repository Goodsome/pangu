"""d4_client 门面层。

暴露 D4Client 聚合根主入口、D4Window、AutoCalibratingScreen、MainHUD、InventoryScreen、SocialScreen 页面对象以及领域模型。
"""

from d4_client.client import D4Client
from d4_client.models import (
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
)
from d4_client.screens import (
    AutoCalibratingScreen,
    InventoryScreen,
    MainHUD,
    SocialScreen,
)
from d4_client.window import D4Window

__all__ = [
    "D4Client",
    "D4Window",
    "AutoCalibratingScreen",
    "MainHUD",
    "InventoryScreen",
    "SocialScreen",
    "Point",
    "Region",
    "MatchResult",
    "OcrResult",
    "ImageFrame",
]
