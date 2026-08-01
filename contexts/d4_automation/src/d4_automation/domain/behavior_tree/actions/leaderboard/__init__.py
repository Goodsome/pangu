"""天梯榜采集行为树节点包。"""

from d4_automation.domain.behavior_tree.actions.leaderboard.capture_all_slots import (
    CaptureAllSlots,
)
from d4_automation.domain.behavior_tree.actions.leaderboard.capture_leaderboard_page import (
    CaptureLeaderboardPage,
)
from d4_automation.domain.behavior_tree.actions.leaderboard.click_row import ClickRow
from d4_automation.domain.behavior_tree.actions.leaderboard.close_player_config import (
    ClosePlayerConfig,
)
from d4_automation.domain.behavior_tree.actions.leaderboard.go_next_page import (
    GoNextPage,
)
from d4_automation.domain.behavior_tree.actions.leaderboard.open_player_config import (
    OpenPlayerConfig,
)
from d4_automation.domain.behavior_tree.actions.leaderboard.select_class import (
    SelectClass,
)

__all__ = [
    "CaptureAllSlots",
    "CaptureLeaderboardPage",
    "ClickRow",
    "ClosePlayerConfig",
    "GoNextPage",
    "OpenPlayerConfig",
    "SelectClass",
]
