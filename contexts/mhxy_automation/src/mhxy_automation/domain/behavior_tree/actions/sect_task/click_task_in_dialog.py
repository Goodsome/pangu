from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


class ClickTaskInDialog(Action):
    """点击对话中的任务"""

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        await blackboard.client.main_hud.choose_option_in_dialog(task_info.task_target, "师门任务")
        return NodeStatus.SUCCESS