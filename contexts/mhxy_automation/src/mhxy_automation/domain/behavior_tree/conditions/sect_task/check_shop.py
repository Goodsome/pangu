from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ITEM_KNOWLEDGE_DB, ShopRoute


@dataclass
class CheckShop(Condition):
    
    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        shop_route: ShopRoute | None = ITEM_KNOWLEDGE_DB.get(task_info.task_target)
        if shop_route is None:
            raise ValueError(f"Unknown shop route for task target: {task_info.task_target}")
        if blackboard.main_ctx.current_house is not None:
            current_house = blackboard.main_ctx.current_house
        else:
            current_house = await blackboard.client.main_hud.get_current_map()
            blackboard.main_ctx.current_house = current_house
        if current_house == shop_route["shop"]:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
