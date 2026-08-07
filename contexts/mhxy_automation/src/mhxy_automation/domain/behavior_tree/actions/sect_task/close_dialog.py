"""动作节点：关闭师父 NPC 对话框。"""

import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action, RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class CloseDialog(RunningAction):

    @override
    async def on_start(self, blackboard: Blackboard) -> None:
        await blackboard.client.main_hud.close_dialog()

    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        return NodeStatus.RUNNING