from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import MainHUD


@dataclass
class OpenSocial(BaseNode):

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        panel = blackboard.current_panel
        match panel:
            case MainHUD():
                social_panel = await panel.open_social()
                blackboard.update_panel(social_panel)
                return NodeStatus.SUCCESS
            case _:
                return NodeStatus.FAILURE