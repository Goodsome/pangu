from typing import override

from client_core import RelativeRegion
from mhxy_client.screens.base import BaseScreen


class Panel(BaseScreen):
    
    title_roi: RelativeRegion
    
    @override
    async def check_visible(self) -> bool:
        element = await self.locate_element(
            element_key=self.screen_name,
            target_text=self.screen_name,
            roi=self.title_roi,
        )
        return element is not None
        