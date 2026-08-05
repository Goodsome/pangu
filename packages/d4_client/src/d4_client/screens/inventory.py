"""暗黑破坏神 4 背包面板 (InventoryScreen) 页面对象模型。"""

from dataclasses import dataclass
from typing import override

from client_core import AutoCalibratingScreen


@dataclass
class InventoryPanel(AutoCalibratingScreen):
    """暗黑破坏神 4 背包面板 POM。"""

    screen_name: str = "InventoryScreen"

    @override
    async def check_visible(self) -> bool:
        """检查当前是否处于背包面板。"""
        return True
