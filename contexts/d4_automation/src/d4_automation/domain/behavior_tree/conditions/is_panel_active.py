from dataclasses import dataclass
from typing import override
from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import D4Panel


@dataclass
class IsPanelActive(BaseNode):
    expected_panel: type[D4Panel]

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        if isinstance(blackboard.current_panel, self.expected_panel):
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
