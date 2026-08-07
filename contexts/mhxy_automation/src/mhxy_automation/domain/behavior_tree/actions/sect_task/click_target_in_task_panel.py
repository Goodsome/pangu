from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.actions.sect_task.moving_action import (
    MovingAction,
)


@dataclass
class ClickTargetInTaskPanel(MovingAction):
    """点击任务面板中的目标"""

    expire_time: float = 60

    @override
    async def _on_start(self, blackboard: Blackboard) -> None:
        task_info = blackboard.sect_task.task_info
        await blackboard.client.main_hud.click_target_in_task_panel(
            task_info.task_target
        )
