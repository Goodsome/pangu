from client_core import RelativeRegion
from mhxy_client.screens.panels.panel import Panel


class GivePanel(Panel):
    screen_name: str = "给予"
    
    title_roi: RelativeRegion = RelativeRegion(x=0.4667, y=0.3062, width=0.0640, height=0.0347)
    confirm_give_roi: RelativeRegion = RelativeRegion(x=0.2771, y=0.7080, width=0.1268, height=0.0392)

    async def confirm_give(self):
        await self.click(target_roi=self.confirm_give_roi)