from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_client.models.sect_task import TaskType


@dataclass
class IsSendMailTask(BaseNode):

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        if task_info is None:
            return NodeStatus.FAILURE
        if task_info.task_type == TaskType.SEND_MAIL:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
