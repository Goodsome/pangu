from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class ClickTargetInTaskPanel(RunningAction):
    """点击任务面板中的目标"""

    expire_time: float | None = 60
    
    @override
    async def on_start(self, blackboard: Blackboard) -> None:
        task_info = blackboard.sect_task.task_info
        await blackboard.client.main_hud.click_target_in_task_panel(task_info.task_target)

    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        is_moving = await blackboard.client.main_hud.is_moving()
        if not is_moving:
            return NodeStatus.SUCCESS
        return NodeStatus.RUNNING
