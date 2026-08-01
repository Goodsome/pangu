"""Action: 点击弹出菜单中的"查看配置"，进入玩家配置页。"""

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
class OpenPlayerConfig(BaseNode):
    """定位并点击"查看配置"菜单项，等待玩家配置页加载完成，更新黑板面板。

    前置条件：blackboard.current_panel 为 LeaderboardScreen，且弹出菜单已展开。
    副作用：blackboard.current_panel → PlayerConfigScreen。
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                logger.info(
                    "[OpenPlayerConfig] 打开排名 %d 的配置页",
                    blackboard.leaderboard.current_rank,
                )
                config_screen = await screen.open_player_config()
                blackboard.update_panel(config_screen)
                cfg = load_capture_task_config()
                await asyncio.sleep(cfg.timing.after_open_config)
                return NodeStatus.SUCCESS
            case _:
                logger.warning("[OpenPlayerConfig] 当前面板非 LeaderboardScreen，跳过")
                return NodeStatus.FAILURE
