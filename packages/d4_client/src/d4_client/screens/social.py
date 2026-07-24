"""暗黑破坏神 4 社交界面 (SocialScreen) 页面对象模型。"""

from dataclasses import dataclass
from typing import override

from d4_client.screens.base import AutoCalibratingScreen


@dataclass
class SocialScreen(AutoCalibratingScreen):
    """暗黑破坏神 4 社交界面 POM。"""

    screen_name: str = "SocialScreen"

    @override
    async def is_visible(self) -> bool:
        """检查当前是否处于社交界面。"""
        return True
