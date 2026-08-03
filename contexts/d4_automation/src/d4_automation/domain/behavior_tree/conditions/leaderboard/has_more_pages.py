"""Condition: 是否还需要采集更多页。"""

from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus


from d4_client import LeaderboardScreen


@dataclass
class HasMorePages(BaseNode):
    """检查当前页码是否未超过目标终止页。

    前置条件：blackboard.current_panel 为 LeaderboardScreen。
    返回：
      SUCCESS → screen.current_page <= target_end_page，还需继续采集
      FAILURE → 已完成所有目标页的采集或当前非 LeaderboardScreen
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                if screen.current_page <= blackboard.leaderboard.target_end_page:
                    return NodeStatus.SUCCESS
                return NodeStatus.FAILURE
            case _:
                return NodeStatus.FAILURE
