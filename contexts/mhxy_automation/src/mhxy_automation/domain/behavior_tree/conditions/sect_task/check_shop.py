from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ShopRoute


@dataclass
class CheckShop(Condition):
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        shop_route = ShopRoute.from_item_name(task_info.task_target)
        current_house = await blackboard.client.main_hud.get_current_map()
        if current_house == shop_route.shop:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
