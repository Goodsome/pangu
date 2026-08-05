"""梦幻西游 道具/背包面板 (InventoryPanel) 页面对象模型。"""

from dataclasses import dataclass
from typing import override

from client_core.models import SplitMode
from mhxy_client.models.map import Map
from mhxy_client.screens.base import BaseScreen
from sys_input import MouseButton, VirtualKeyCode


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

    async def open(self):
        if self.is_visible:
            return
        await self.window.hotkey([VirtualKeyCode.VK_MENU, VirtualKeyCode.VK_E])
        await self.wait_until_visible()
        
    async def use_item(self, row: int, col: int):
        if not 0 <= row < 4 or not 0 <= col < 5:
            raise ValueError(f"Invalid row/col: {row}/{col}")
        grid_roi = self.config.inventory_grid_roi
        unit_grid_roi = grid_roi.split(n=4, mode=SplitMode.HORIZONTAL)[row].split(n=5, mode=SplitMode.VERTICAL)[col]
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"{grid_roi=}, {unit_grid_roi=}")
        await self.mouse_click(target_roi=unit_grid_roi, button=MouseButton.RIGHT)

    async def use_fei_xing_fu(self, target: Map):
        if not self.is_visible:
            await self.open()
        
        await self.use_item(row=0, col=4)
        match target:
            case Map.CHANG_AN:
                await self.mouse_click(target_roi=self.config.feixingfu_map_changan_roi)
            case _:
                raise ValueError(f"Invalid target: {target}")