import logging

from dataclasses import dataclass
from typing import override

from client_core import RelativeRegion
from mhxy_client.screens.base import BaseScreen
from sys_input import MouseButton

logger = logging.getLogger(__name__)

@dataclass
class NpcDialog(BaseScreen):

    npc_name: str = ""
    dialog_name_roi: RelativeRegion = RelativeRegion(x=0.1663, y=0.4630, width=0.1145, height=0.0483)
    
    @override
    async def check_visible(self) -> bool:
        element = await self.locate_element(
            element_key="dialog_name",
            target_text=self.npc_name,
            roi=self.dialog_name_roi
        )
        return element is not None

    async def close_dialog(self) -> None:
        await self.window.mouse_click(button=MouseButton.RIGHT)

    async def choose_option(self, option_name: str) -> None:
        element = await self.locate_element(
            element_key=option_name,
            target_text=option_name,
            roi=self.config.dialog_roi,
        )
        if element is None:
            raise RuntimeError(f"未能定位到选项元素: {option_name}")
        await self.mouse_click(element.region.center)
        
    async def claim_task(self) -> None:
        await self.choose_option("师门任务")

    async def give(self) -> None:
        await self.choose_option("给予")