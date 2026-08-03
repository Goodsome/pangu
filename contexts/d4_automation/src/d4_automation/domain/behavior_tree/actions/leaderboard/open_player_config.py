"""Action: 点击弹出菜单中的"查看配置"，进入玩家配置页。"""

import logging
from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import LeaderboardScreen

logger = logging.getLogger(__name__)


@dataclass
class OpenPlayerConfig(BaseNode):
    """定位并点击"查看配置"菜单项，等待玩家配置页加载完成，更新黑板面板。

    前置条件：blackboard.current_panel 为 LeaderboardScreen，且弹出菜单已展开。
    副作用：blackboard.current_panel → PlayerConfigScreen。
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                config_screen = await screen.open_player_config()
                blackboard.update_panel(config_screen)
                return NodeStatus.SUCCESS
            case _:
                logger.warning("[OpenPlayerConfig] 当前面板非 LeaderboardScreen，跳过")
                return NodeStatus.FAILURE
