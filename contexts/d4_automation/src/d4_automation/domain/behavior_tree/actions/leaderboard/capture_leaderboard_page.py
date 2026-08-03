"""Action: 截取当页天梯榜记录区域并保存图片。"""

import logging
from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import LeaderboardScreen

logger = logging.getLogger(__name__)


@dataclass
class CaptureLeaderboardPage(BaseNode):
    """截取当前页的 10 条记录区域并保存为 PNG 图片。

    前置条件：blackboard.current_panel 为 LeaderboardScreen。
    副作用：在页码目录下创建 leaderboard_{page:03d}.png。
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                output_dir = (
                    blackboard.leaderboard.output_base_dir
                    / screen.current_class.value
                    / f"page_{screen.current_page:03d}"
                )
                save_path = output_dir / f"leaderboard_{screen.current_page:03d}.png"

                await screen.capture_records_region(save_path)
                logger.info(
                    "[CaptureLeaderboardPage] 第 %d 页榜单截图已保存 → %s",
                    screen.current_page,
                    save_path,
                )
                return NodeStatus.SUCCESS
            case _:
                logger.warning(
                    "[CaptureLeaderboardPage] 当前面板非 LeaderboardScreen，跳过"
                )
                return NodeStatus.FAILURE
