
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action, RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ShopRoute


@dataclass
class GoToShopMap(RunningAction):

    _triggered: bool = False
    
    @override
    async def on_start(self, blackboard: Blackboard) -> None:
        task_info = blackboard.sect_task.task_info
        shop_route = ShopRoute.from_item_name(task_info.task_target)

        await blackboard.client.main_hud.inventory.use_fei_xing_fu(target=shop_route.city_map)
        blackboard.main_ctx.current_map = shop_route.city_map

    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        return NodeStatus.RUNNING
