from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus


class ConfirmGive(RunningAction):
    """确认赠送任务"""

    _triggered: bool = False

    @override
    async def on_start(self, blackboard: Blackboard) -> None:
        await blackboard.client.main_hud.panels.given_panel.confirm_give()

    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        return NodeStatus.RUNNING
