from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_client.models.sect_task import TaskType


@dataclass
class CheckTaskType(Condition):
    task_type: TaskType

    @property
    def name(self) -> str:
        return f"CheckTaskType({self.task_type})"
    
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        if task_info.task_type == self.task_type:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
