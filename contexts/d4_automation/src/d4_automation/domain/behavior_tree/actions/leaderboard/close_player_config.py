"""Action: 关闭玩家配置页，返回天梯榜，并推进行索引。"""

import asyncio
import logging
from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import PlayerConfigScreen

logger = logging.getLogger(__name__)


@dataclass
class ClosePlayerConfig(BaseNode):
    """关闭玩家配置查看页，更新黑板面板为 LeaderboardScreen。

    前置条件：blackboard.current_panel 为 PlayerConfigScreen。
    副作用：
      - blackboard.current_panel → LeaderboardScreen
      - leaderboard_screen.current_row += 1
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case PlayerConfigScreen() as screen:
                logger.info(
                    "[ClosePlayerConfig] 关闭页 %d 行 %d 的配置页",
                    screen.page,
                    screen.row + 1,
                )
                leaderboard_screen = await screen.close()
                leaderboard_screen.current_row = screen.row + 1
                blackboard.update_panel(leaderboard_screen)

                return NodeStatus.SUCCESS
            case _:
                logger.warning(
                    "[ClosePlayerConfig] 当前面板非 PlayerConfigScreen，跳过"
                )
                return NodeStatus.FAILURE
