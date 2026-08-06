from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class IsPanelVisible(Condition):
    panel_name: str

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        match self.panel_name:
            case "shop":
                visible = await blackboard.client.main_hud.panels.shop_panel.check_visible()
            case "given":
                visible = await blackboard.client.main_hud.panels.given_panel.check_visible()
            case _:
                visible = False
        if visible:
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.FAILURE