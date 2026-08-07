from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ShopRoute


class IsShopDialogVisible(Condition):
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        shop_route = ShopRoute.from_item_name(task_info.task_target)
        visible = await blackboard.client.main_hud.check_dialog_visible(
            shop_route.npc_name
        )
        if visible:
            blackboard.main_ctx.target_npc = shop_route.npc_name
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.FAILURE
