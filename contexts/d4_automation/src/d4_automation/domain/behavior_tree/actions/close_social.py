from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import MainHUD, SocialPanel


@dataclass
class CloseSocial(BaseNode):

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        panel = blackboard.current_panel
        match panel:
            case SocialPanel():
                main_hud = await panel.close()
                blackboard.update_panel(main_hud)
                return NodeStatus.SUCCESS
            case _:
                return NodeStatus.FAILURE