from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action, RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ShopRoute


@dataclass
class GoToShop(RunningAction):

    _triggered: bool = False
    
    @override
    async def on_start(self, blackboard: Blackboard) -> None:
            
        task_info = blackboard.sect_task.task_info
        shop_route = ShopRoute.from_item_name(task_info.task_target)

        await blackboard.client.main_hud.go_to_shop(target=shop_route.shop)

    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        is_moving = await blackboard.client.main_hud.is_moving()
        if not is_moving:
            return NodeStatus.SUCCESS
        return NodeStatus.RUNNING