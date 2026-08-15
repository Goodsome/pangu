
from dataclasses import dataclass

from client_core import RelativeRegion
from mhxy_client.screens.panels.panel import Panel
from sys_input.models import MouseButton


@dataclass
class ShopPanel(Panel):
    screen_name: str = "购买"
    title_roi: RelativeRegion = RelativeRegion(x=0.4729, y=0.2021, width=0.0579, height=0.0347)
    shopping_grid_roi: RelativeRegion = RelativeRegion(x=0.3239, y=0.2549, width=0.3510, height=0.3424)
    buy_roi: RelativeRegion = RelativeRegion(x=0.4446, y=0.8130, width=0.1121, height=0.0377)
    
    async def choose_item(self, row: int, col: int):
        unit_grid_roi = self.shopping_grid_roi.get_unit(
            row=4,
            col=5,
            row_index=row,
            col_index=col,
        )
        await self.mouse_click(target_roi=unit_grid_roi)

    async def buy(self):
        await self.mouse_click(target_roi=self.buy_roi)

    async def close(self):
        await self.mouse_click(target_roi=self.title_roi, button=MouseButton.RIGHT)