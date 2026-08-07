from dataclasses import dataclass, field
import time
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class ReportTaskInDialog(Action):
    """点击对话中的任务"""

    running_time: float = 1
    start_time: float = field(default=0, init=False)

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        
        now = time.monotonic()
        if now - self.start_time < self.running_time:
            return NodeStatus.RUNNING
        
        task_info = blackboard.sect_task.task_info
        option = "师门任务"
        await blackboard.client.main_hud.choose_option_in_dialog(task_info.task_target, option)
        return NodeStatus.SUCCESS
