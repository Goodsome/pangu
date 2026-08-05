
from client_core import RelativeRegion
from mhxy_client.screens.panels.panel import Panel


class ShopPanel(Panel):
    screen_name: str = "购买"
    title_roi: RelativeRegion = RelativeRegion(x=0.4655, y=0.1991, width=0.0690, height=0.0347)
    shopping_grid_roi: RelativeRegion = RelativeRegion(x=0.3239, y=0.2549, width=0.3510, height=0.3424)
    buy_roi: RelativeRegion = RelativeRegion(x=0.4446, y=0.8130, width=0.1121, height=0.0377)
    
    async def choose_item(self, row: int, col: int):
        unit_grid_roi = self.shopping_grid_roi.get_unit(
            row=4,
            col=5,
            row_index=row,
            col_index=col,
        )
        await self.mouse_click(unit_grid_roi.center)

    async def buy(self):
        await self.mouse_click(self.buy_roi.center)