"""梦幻西游 道具/背包面板 (InventoryPanel) 页面对象模型。"""

from dataclasses import dataclass
from typing import override

from mhxy_client.screens.base import BaseScreen


@dataclass
class InventoryPanel(BaseScreen):
    """梦幻西游 道具/背包面板 POM。"""

    screen_name: str = "InventoryPanel"

    @override
    async def check_visible(self) -> bool:
        """检查当前是否处于道具/背包面板。"""
        ele = await self.locate_element(
            element_key="inventory_title",
            target_text="道具行囊",
            roi=self.config.inventory_title_roi
        )
        self.is_visible: bool = ele is not None
        return self.is_visible
