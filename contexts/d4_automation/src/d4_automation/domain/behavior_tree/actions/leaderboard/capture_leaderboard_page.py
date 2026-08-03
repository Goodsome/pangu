"""Action: 截取当页天梯榜记录区域并保存图片。"""

import logging
from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_automation.infrastructure.image_io import save_image
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
                ctx = blackboard.leaderboard
                frame = await screen.capture_records_region()

                page_dir = ctx.page_output_dir()
                save_path = page_dir / f"leaderboard_{ctx.current_page:03d}.png"

                await save_image(frame, save_path)
                logger.info(
                    "[CaptureLeaderboardPage] 第 %d 页榜单截图已保存 → %s",
                    ctx.current_page,
                    save_path,
                )
                return NodeStatus.SUCCESS
            case _:
                logger.warning(
                    "[CaptureLeaderboardPage] 当前面板非 LeaderboardScreen，跳过"
                )
                return NodeStatus.FAILURE
