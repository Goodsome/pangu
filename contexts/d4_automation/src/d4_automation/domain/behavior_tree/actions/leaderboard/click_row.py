"""Action: 点击天梯榜当前行，触发弹出上下文菜单。"""

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
class ClickRow(BaseNode):
    """点击当前行（由 blackboard.leaderboard.current_row 决定）触发弹出菜单。

    前置条件：blackboard.current_panel 为 LeaderboardScreen。
    副作用：无（行索引递增由 CaptureAllSlots/ClosePlayerConfig 之后的节点负责）。
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                ctx = blackboard.leaderboard
                row = ctx.current_row
                logger.info(
                    "[ClickRow] 点击第 %d 行（全局排名 %d）",
                    row + 1,
                    ctx.current_rank,
                )
                await screen.click_row(row)
                cfg = load_capture_task_config()
                await asyncio.sleep(cfg.timing.after_click_row)
                return NodeStatus.SUCCESS
            case _:
                logger.warning("[ClickRow] 当前面板非 LeaderboardScreen，跳过")
                return NodeStatus.FAILURE
