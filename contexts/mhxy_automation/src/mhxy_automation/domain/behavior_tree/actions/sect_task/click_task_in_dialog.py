from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class ClickTaskInDialog(Action):
    """点击对话中的任务"""

    _triggered: bool = False

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        if self._triggered:
            return NodeStatus.RUNNING
        
        task_info = blackboard.sect_task.task_info
        if task_info.has_item:
            option = "给予"
        else:
            option = "师门任务"
        await blackboard.client.main_hud.choose_option_in_dialog(task_info.task_target, option)
        self._triggered = True
        return NodeStatus.RUNNING

    @override
    def reset(self) -> None:
        self._triggered = False