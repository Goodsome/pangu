from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus


class IsTargetDialogVisible(Condition):
    """检查目标（默认：师门任务目标）的 NPC 对话框是否已在当前帧出现。"""

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        visible = await blackboard.client.main_hud.check_dialog_visible(task_info.task_target)
        if visible:
            blackboard.main_ctx.target_npc = task_info.task_target
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.FAILURE

    