
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ITEM_KNOWLEDGE_DB, ShopRoute


@dataclass
class GoToShopMap(Action):

    _triggered: bool = False
    
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        if self._triggered:
            return NodeStatus.RUNNING
            
        task_info = blackboard.sect_task.task_info
        shop_route: ShopRoute | None = ITEM_KNOWLEDGE_DB.get(task_info.task_target)
        if shop_route is None:
            raise ValueError(f"Unknown shop route for task target: {task_info.task_target}")

        await blackboard.client.main_hud.inventory.use_fei_xing_fu(target=shop_route["city_map"])
        self._triggered = True
        blackboard.main_ctx.current_map = shop_route["city_map"]
        return NodeStatus.RUNNING

    @override
    def reset(self) -> None:
        self._triggered = False
