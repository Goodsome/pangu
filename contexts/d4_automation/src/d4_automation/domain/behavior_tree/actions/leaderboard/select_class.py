"""Action: 选择天梯榜职业。"""

import asyncio
import logging
from dataclasses import dataclass
from typing import override

from d4_automation.config import load_capture_task_config
from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import LeaderboardScreen

logger = logging.getLogger(__name__)


@dataclass
class SelectClass(BaseNode):
    """点击顶部职业按钮，切换天梯榜到目标职业。

    前置条件：blackboard.current_panel 为 LeaderboardScreen。
    副作用：更新 blackboard.leaderboard.player_class。
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                cfg = load_capture_task_config()
                player_class = cfg.player_class
                logger.info("[SelectClass] 切换职业 → %s", player_class)
                await screen.select_class(player_class)
                blackboard.leaderboard.player_class = player_class
                await asyncio.sleep(cfg.timing.after_select_class)
                return NodeStatus.SUCCESS
            case _:
                logger.warning("[SelectClass] 当前面板非 LeaderboardScreen，跳过")
                return NodeStatus.FAILURE
