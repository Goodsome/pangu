"""暗黑破坏神 4 常驻主界面 (MainHUD) 页面对象模型。"""

from dataclasses import dataclass
from typing import override

from d4_client.screens.base import AutoCalibratingScreen
from d4_client.screens.inventory import InventoryPanel
from d4_client.screens.social import SocialPanel
from sys_input import VirtualKeyCode
from d4_client.models import RelativeRegion

_MAP_NAME_ROI = RelativeRegion(
    x=0.9,
    y=0.0,
    width=0.1,
    height=0.05
)


@dataclass
class MainHUD(AutoCalibratingScreen):
    """暗黑 4 主界面常驻 HUD 视角与面板控制对象。"""

    screen_name: str = "MainHUD"

    @override
    async def is_visible(self) -> bool:
        """检查当前界面是否为主 HUD 视角。"""

        results = await self.window.ocr(
            roi=_MAP_NAME_ROI
        )
        for result in results:
            if result.text:
                return True
        return False

    async def open_inventory(self) -> InventoryPanel:
        """按下键盘 'I' 键打开背包面板并返回 InventoryScreen 实例。"""
        await self.window.key_press(VirtualKeyCode.VK_I)
        screen = InventoryPanel(window=self.window)
        await screen.wait_until_visible()
        return screen

    async def open_social(self) -> SocialPanel:
        """按下键盘 'O' 键打开社交面板并返回 SocialScreen 实例。"""
        await self.window.key_press(VirtualKeyCode.VK_O)
        screen = SocialPanel(window=self.window)
        await screen.wait_until_visible()
        return screen
