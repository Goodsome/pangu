import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus


logger = logging.getLogger(__name__)


@dataclass
class IsDialogVisible(Condition):
    target_npc: str | None = None

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        visible = await blackboard.main_hud.check_dialog_visible()
        if visible:
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.FAILURE
