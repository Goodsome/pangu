"""暗黑破坏神 4 社交界面 (SocialScreen) 页面对象模型。"""

from dataclasses import dataclass
from typing import override, TYPE_CHECKING

from client_core import RelativeRegion
from d4_client.screens.base import AutoCalibratingScreen
from sys_input import VirtualKeyCode

if TYPE_CHECKING:
    from d4_client.screens.main_hud import MainHUD

_ADD_FRIEND_ROI = RelativeRegion(
    x=0.7,
    y=0.8,
    width=0.2,
    height=0.2,
)


@dataclass
class SocialPanel(AutoCalibratingScreen):
    """暗黑破坏神 4 社交界面 POM。"""

    screen_name: str = "SocialScreen"

    @override
    async def is_visible(self) -> bool:
        """检查当前是否处于社交界面。"""
        add_friend_located = await self.locate_element(
            element_key="add_friend",
            target_text="添加好友",
            roi=_ADD_FRIEND_ROI,
        )
        return add_friend_located is not None

    async def close(self) -> MainHUD:
        from d4_client.screens.main_hud import MainHUD

        await self.window.key_press(VirtualKeyCode.VK_ESCAPE)
        main_hud = MainHUD(window=self.window)
        await main_hud.wait_until_visible()
        return main_hud
