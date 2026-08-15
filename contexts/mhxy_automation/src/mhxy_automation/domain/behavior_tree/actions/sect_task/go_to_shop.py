from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.actions.sect_task.moving_action import (
    MovingAction,
)
from mhxy_automation.domain.models.shop_route import ShopRoute


@dataclass
class GoToShop(MovingAction):
    expire_time: float = 60

    @override
    async def _on_start(self, blackboard: Blackboard) -> None:

        task_info = blackboard.sect_task.task_info
        shop_route = ShopRoute.from_item_name(task_info.task_target)
        await blackboard.client.main_hud.go_to_shop(target=shop_route.shop)
