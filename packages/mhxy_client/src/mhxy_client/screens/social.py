"""梦幻西游 社交/好友面板 (SocialPanel) 页面对象模型。"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from client_core import AutoCalibratingScreen
from sys_input import VirtualKeyCode

if TYPE_CHECKING:
    from mhxy_client.screens.main_hud import MainHUD


@dataclass
class SocialPanel(AutoCalibratingScreen):
    """梦幻西游 社交/好友面板 POM。"""

    screen_name: str = "SocialPanel"

    @override
    async def is_visible(self) -> bool:
        """检查当前是否处于社交面板。"""
        return True

    async def close(self) -> "MainHUD":
        from mhxy_client.screens.main_hud import MainHUD

        await self.window.key_press(VirtualKeyCode.VK_ESCAPE)
        main_hud = MainHUD(window=self.window)
        await main_hud.wait_until_visible()
        return main_hud
