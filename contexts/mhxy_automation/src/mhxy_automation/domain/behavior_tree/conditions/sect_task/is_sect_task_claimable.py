"""条件节点：师门任务是否处于可领取状态。"""

from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_client.models.sect_task import SectTaskStatus


@dataclass
class IsSectTaskClaimable(BaseNode):
    """检查黑板中缓存的 task_info 是否为 CLAIMABLE 状态。

    本节点为纯内存条件检查，不发起任何 IO 操作，因此不会消耗帧资源。

    返回值：
        SUCCESS : task_info 已存在且 status == CLAIMABLE
        FAILURE : task_info 为 None，或状态非 CLAIMABLE
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        if task_info.status == SectTaskStatus.CLAIMABLE:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
