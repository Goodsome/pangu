"""梦幻西游 道具/背包面板 (InventoryPanel) 页面对象模型。"""

from dataclasses import dataclass
from typing import override

from client_core import AutoCalibratingScreen


@dataclass
class InventoryPanel(AutoCalibratingScreen):
    """梦幻西游 道具/背包面板 POM。"""

    screen_name: str = "InventoryPanel"

    @override
    async def is_visible(self) -> bool:
        """检查当前是否处于道具/背包面板。"""
        return True
