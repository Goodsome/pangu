from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class RaiseError(Action):

    message: str

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        raise Exception(self.message)