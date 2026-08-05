from client_core import Window
from mhxy_client.screens.panels.give_panel import GivePanel
from mhxy_client.screens.panels.shop_panel import ShopPanel


class Panels:
    
    def __init__(self, window: Window):
        self.window: Window = window
        self.given_panel: GivePanel = GivePanel(window=window)
        self.shop_panel: ShopPanel = ShopPanel(window=window)