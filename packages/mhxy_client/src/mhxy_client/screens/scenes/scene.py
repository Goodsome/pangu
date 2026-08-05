from typing import override

from mhxy_client.models.npcs.npc import Npc
from mhxy_client.screens.base import BaseScreen
from mhxy_client.screens.dialogs.base import NpcDialog


class Scene(BaseScreen):
    screen_name: str
    
    @override
    async def check_visible(self) -> bool:
        element = await self.locate_element(
            element_key="dialog_name",
            target_text=self.screen_name,
            roi=self.config.map_name_roi
        )
        return element is not None
        
    async def interact_with_npc(self, npc: Npc) -> NpcDialog:
        await self.mouse_click(target_roi=npc.scene_location)
        dialog = npc.dialog(
            window=self.window,
            npc_name=npc.name
        )
        await dialog.wait_until_visible()
        return dialog
        
    