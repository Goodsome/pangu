"""Condition: 当前面板是否为天梯榜页面。"""

from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import LeaderboardScreen


@dataclass
class IsLeaderboardVisible(BaseNode):
    """检查当前面板类型是否为 LeaderboardScreen 且页面可见。

    返回：
      SUCCESS → 当前处于天梯榜页面
      FAILURE → 当前不在天梯榜页面
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                visible = await screen.is_visible()
                return NodeStatus.SUCCESS if visible else NodeStatus.FAILURE
            case _:
                return NodeStatus.FAILURE
