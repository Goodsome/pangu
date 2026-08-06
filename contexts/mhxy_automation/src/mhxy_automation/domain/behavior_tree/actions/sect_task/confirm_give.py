from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


class ConfirmGive(Action):
    """确认赠送任务"""

    _triggered: bool = False
    
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        if self._triggered:
            return NodeStatus.RUNNING
        await blackboard.client.main_hud.panels.given_panel.confirm_give()
        self._triggered = True
        return NodeStatus.RUNNING
        
    @override
    def reset(self) -> None:
        self._triggered = False