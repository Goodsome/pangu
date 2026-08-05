"""mhxy_client POM (Page Object Model) 屏幕对象层。"""

from mhxy_client.screens.inventory import InventoryPanel
from mhxy_client.screens.main_hud import MainHUD
from mhxy_client.screens.social import SocialPanel

MhxyPanel = MainHUD | InventoryPanel | SocialPanel

__all__ = [
    "MhxyPanel",
    "MainHUD",
    "InventoryPanel",
    "SocialPanel",
]
