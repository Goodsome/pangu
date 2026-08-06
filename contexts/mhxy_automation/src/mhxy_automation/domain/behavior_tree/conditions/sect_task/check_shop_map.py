import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ITEM_KNOWLEDGE_DB, ShopRoute

logger = logging.getLogger(__name__)

@dataclass
class CheckShopMap(Condition):
    
    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        shop_route: ShopRoute | None = ITEM_KNOWLEDGE_DB.get(task_info.task_target)
        if shop_route is None:
            raise ValueError(f"Unknown shop route for task target: {task_info.task_target}")
        current_map = await blackboard.client.main_hud.get_current_map()
        if current_map == shop_route["shop"]:
            return NodeStatus.SUCCESS
        if current_map == shop_route["city_map"]:
            return NodeStatus.SUCCESS
        logger.info(f"Current map: {current_map}, shop route: {shop_route}")
        return NodeStatus.FAILURE
