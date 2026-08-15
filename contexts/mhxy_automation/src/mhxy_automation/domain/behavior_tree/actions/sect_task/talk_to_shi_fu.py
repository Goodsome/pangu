from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus
from typing_extensions import override


class TalkToShiFu(RunningAction):
    expire_time: float = 10
    
    @override
    async def on_start(self, blackboard: Blackboard) -> None:
        task_info = blackboard.sect_task.task_info
        await blackboard.client.main_hud.click_target_in_task_panel(
            task_info.task_target
        )
    
    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        return NodeStatus.RUNNING
