from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class ReturnShiMeng(RunningAction):
    @override
    async def on_start(self, blackboard: Blackboard) -> None:
        await blackboard.client.main_hud.return_shi_meng()

    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        return NodeStatus.RUNNING
