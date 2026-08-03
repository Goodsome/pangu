"""Condition: 当前页是否还有未处理的行。"""

from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus


from d4_client import LeaderboardScreen


@dataclass
class HasMoreRows(BaseNode):
    """检查当前页是否还有未处理的行（screen.current_row < screen.row_count）。

    前置条件：blackboard.current_panel 为 LeaderboardScreen。
    返回：
      SUCCESS → 还有行需要处理
      FAILURE → 当前页已全部处理完毕或非 LeaderboardScreen
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case LeaderboardScreen() as screen:
                if screen.current_row < screen.row_count:
                    return NodeStatus.SUCCESS
                return NodeStatus.FAILURE
            case _:
                return NodeStatus.FAILURE
