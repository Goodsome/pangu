from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_client import SectTaskStatus


@dataclass
class IsTaskStatus(Condition):
    status: SectTaskStatus

    @override
    @property
    def name(self) -> str:
        return f"IsTaskStatus({self.status.name})"

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        if task_info.status == self.status:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
