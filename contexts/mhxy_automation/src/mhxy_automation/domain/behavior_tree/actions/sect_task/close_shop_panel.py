import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action, BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class CloseShopPanel(Action):

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        await blackboard.client.main_hud.panels.shop_panel.close()
        return NodeStatus.SUCCESS
