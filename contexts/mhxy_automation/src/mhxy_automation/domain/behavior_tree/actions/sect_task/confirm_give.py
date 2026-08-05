from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


class ConfirmGive(Action):
    """确认赠送任务"""

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        await blackboard.client.main_hud.panels.given_panel.confirm_give()
        blackboard.sect_task.clear_task_info()
        return NodeStatus.SUCCESS