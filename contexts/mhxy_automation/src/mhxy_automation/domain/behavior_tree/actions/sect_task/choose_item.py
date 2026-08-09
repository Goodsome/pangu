from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ShopRoute


@dataclass
class ChooseItem(Action):

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:

        task_info = blackboard.sect_task.task_info
        shop_route = ShopRoute.from_item_name(task_info.task_target)

        await blackboard.main_hud.panels.shop_panel.choose_item(
            row=shop_route.item_location[0],
            col=shop_route.item_location[1],
        )
        return NodeStatus.SUCCESS
