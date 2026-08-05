from typing import override

from mhxy_client.screens.base import BaseScreen
from sys_input import MouseButton

class NpcDialog(BaseScreen):

    npc_name: str
    
    @override
    async def check_visible(self) -> bool:
        element = await self.locate_element(
            element_key="dialog_name",
            target_text=self.npc_name,
            roi=self.config.dialog_name_roi
        )
        return element is not None

    async def claim_task(self) -> None:
        element = await self.locate_element(
            element_key="sect_task",
            target_text="师门任务",
            roi=self.config.claim_task_roi,
        )
        if element is None:
            raise RuntimeError("未能定位到师门任务元素")
        await self.mouse_click(element.region.center)

    async def close_dialog(self) -> None:
        await self.window.mouse_click(button=MouseButton.RIGHT)