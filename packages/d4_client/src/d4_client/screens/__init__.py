"""d4_client POM (Page Object Model) 屏幕对象层。"""

from client_core import AutoCalibratingScreen
from d4_client.screens.inventory import InventoryPanel
from d4_client.screens.leaderboard import LeaderboardScreen
from d4_client.screens.main_hud import MainHUD
from d4_client.screens.player_config import PlayerConfigScreen
from d4_client.screens.social import SocialPanel

D4Panel = (
    MainHUD | InventoryPanel | SocialPanel | LeaderboardScreen | PlayerConfigScreen
)

__all__ = [
    "AutoCalibratingScreen",
    "D4Panel",
    "MainHUD",
    "InventoryPanel",
    "SocialPanel",
    "LeaderboardScreen",
    "PlayerConfigScreen",
]
