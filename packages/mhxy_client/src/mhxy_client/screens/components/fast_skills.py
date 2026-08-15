from mhxy_client.models.map import Map
from sys_input import VirtualKeyCode
from mhxy_client.screens.base import BaseScreen


class FastSkills(BaseScreen):
    """梦幻西游 快速技能面板 POM。"""

    async def use_fei_xing_fu(self, target: str):
        await self.window.key_press(VirtualKeyCode.VK_F2)
        
        match target:
            case Map.CHANG_AN:
                await self.mouse_click(target_roi=self.config.feixingfu_map_changan_roi)
            case _:
                raise ValueError(f"Invalid target: {target}")
