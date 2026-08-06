from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_automation.domain.models.shop_route import ITEM_KNOWLEDGE_DB


@dataclass
class OpenShopPanel(Action):

    _triggered: bool = False
    
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        if self._triggered:
            return NodeStatus.RUNNING
            
        task_info = blackboard.sect_task.task_info
        shop_route = ITEM_KNOWLEDGE_DB.get(task_info.task_target)
        if shop_route is None:
            raise ValueError(f"Unknown shop route for task target: {task_info.task_target}")

        await blackboard.main_hud.choose_option_in_dialog(
            dialog_name=shop_route['npc_name'],
            option="购买"
        )
        self._triggered = True
        return NodeStatus.RUNNING

    @override
    def reset(self) -> None:
        self._triggered = False
