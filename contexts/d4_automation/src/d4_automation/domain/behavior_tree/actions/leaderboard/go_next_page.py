"""Action: 翻到天梯榜下一页，并推进页码。"""

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
class GoNextPage(BaseNode):
    """点击"下一页"按钮翻页，等待新页加载，重置 screen.current_row。

    前置条件：blackboard.current_panel 为 LeaderboardScreen。
    副作用：
      - screen.next_page() 会递增 screen.current_page
      - screen.current_row 重置为 0
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                logger.info(
                    "[GoNextPage] 翻页 %d → %d",
                    screen.current_page,
                    screen.current_page + 1,
                )
                await screen.next_page()
                screen.current_row = 0

                cfg = load_capture_task_config()
                await asyncio.sleep(cfg.timing.after_next_page)
                return NodeStatus.SUCCESS
            case _:
                logger.warning("[GoNextPage] 当前面板非 LeaderboardScreen，跳过")
                return NodeStatus.FAILURE
