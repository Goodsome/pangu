"""动作节点：关闭师父 NPC 对话框。"""

import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action, BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class CloseDialog(Action):

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        await blackboard.client.main_hud.close_dialog()
        return NodeStatus.SUCCESS
