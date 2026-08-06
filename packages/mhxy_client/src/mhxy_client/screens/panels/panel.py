from typing import override

from client_core import RelativeRegion
from mhxy_client.screens.base import BaseScreen


class Panel(BaseScreen):
    
    title_roi: RelativeRegion
    
    @override
    async def check_visible(self) -> bool:
        result = await self.window.get_text(roi=self.title_roi)
        return result == self.screen_name