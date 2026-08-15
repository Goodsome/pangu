from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus


class IsShopPanelVisible(Condition):
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        visible = await blackboard.client.main_hud.panels.shop_panel.check_visible()
        if visible:
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.FAILURE
