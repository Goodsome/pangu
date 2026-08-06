from dataclasses import dataclass, field
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class ClickTargetInTaskPanel(Action):
    """点击任务面板中的目标<[fim-middle]>"""
    
    _has_clicked: bool = field(default=False, init=False, repr=False)
    
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info

        if self._has_clicked:
            return NodeStatus.RUNNING
            
        await blackboard.client.main_hud.click_target_in_task_panel(task_info.task_target)
        self._has_clicked = True
        return NodeStatus.RUNNING

    @override
    def reset(self) -> None:
        self._has_clicked = False