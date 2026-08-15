from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class BuyItem(RunningAction):
    expire_time: float = 3

    @override
    async def on_start(self, blackboard: Blackboard) -> None:
        await blackboard.main_hud.panels.shop_panel.buy()

    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        return NodeStatus.RUNNING
