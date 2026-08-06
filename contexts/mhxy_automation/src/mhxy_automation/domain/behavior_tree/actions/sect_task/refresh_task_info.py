from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


class RefreshTaskInfo(Action):

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = await blackboard.main_hud.check_sect_task()
        blackboard.sect_task.set_task_info(task_info)
        return NodeStatus.SUCCESS