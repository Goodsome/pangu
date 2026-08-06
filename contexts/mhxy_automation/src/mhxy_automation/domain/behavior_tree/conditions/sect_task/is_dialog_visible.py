from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class IsDialogVisible(Condition):
    target_npc: str | None = None

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        ctx = blackboard.main_ctx
        npc_name = self.target_npc or ctx.target_npc 
        if npc_name is None:
            raise ValueError("npc_name is None")
        visible = await blackboard.main_hud.check_dialog_visible(npc_name=npc_name)
        if visible:
            if self.target_npc:
                ctx.target_npc = self.target_npc
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.FAILURE