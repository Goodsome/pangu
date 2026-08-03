from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus


class FinishNode(BaseNode):
    
    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        blackboard.finish()
        return NodeStatus.SUCCESS