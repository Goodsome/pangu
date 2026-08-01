"""Condition: 当前页是否还有未处理的行。"""

from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus


@dataclass
class HasMoreRows(BaseNode):
    """检查当前页是否还有未处理的行（current_row < 10）。

    返回：
      SUCCESS → 还有行需要处理
      FAILURE → 当前页 10 行已全部处理完毕
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        if blackboard.leaderboard.has_more_rows:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
