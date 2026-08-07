from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class BuyItem(Action):

    _triggered: bool = False
    
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        if self._triggered:
            return NodeStatus.RUNNING

        await blackboard.main_hud.panels.shop_panel.buy()
        self._triggered = True
        return NodeStatus.RUNNING

    @override
    def _reset(self) -> None:
        self._triggered = False
