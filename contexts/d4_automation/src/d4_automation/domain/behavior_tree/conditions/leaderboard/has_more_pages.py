"""Condition: 是否还需要采集更多页。"""

from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus


@dataclass
class HasMorePages(BaseNode):
    """检查当前页码是否未超过目标终止页。

    返回：
      SUCCESS → current_page <= target_end_page，还需继续采集
      FAILURE → 已完成所有目标页的采集
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        if blackboard.leaderboard.has_more_pages:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
