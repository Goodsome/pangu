from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ShopRoute


@dataclass
class GoToShop(Action):

    _triggered: bool = False
    
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        if self._triggered:
            return NodeStatus.RUNNING
            
        task_info = blackboard.sect_task.task_info
        shop_route = ShopRoute.from_item_name(task_info.task_target)

        await blackboard.client.main_hud.go_to_shop(target=shop_route.shop)
        self._triggered = True
        return NodeStatus.RUNNING

    @override
    def _reset(self) -> None:
        self._triggered = False
