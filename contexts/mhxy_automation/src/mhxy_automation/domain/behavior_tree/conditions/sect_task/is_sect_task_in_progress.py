"""条件节点：师门任务是否处于执行中状态。"""

from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_client.models.sect_task import SectTaskStatus


@dataclass
class IsSectTaskInProgress(BaseNode):
    """检查黑板中缓存的 task_info 是否为 IN_PROGRESS 状态。

    返回值：
        SUCCESS : task_info 已存在且 status == IN_PROGRESS
        FAILURE : task_info 为 None，或状态非 IN_PROGRESS
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        if task_info is None:
            return NodeStatus.FAILURE
        if task_info.status == SectTaskStatus.IN_PROGRESS:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
