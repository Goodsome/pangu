"""动作节点：点击任务追踪面板中的「师父」超链接触发寻路。"""

import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class TriggerGoToShiFu(BaseNode):
    """点击任务追踪面板中的「师父」超链接，触发游戏内自动寻路。

    本节点仅负责**发起点击动作**，不等待寻路结果（单帧语义）。
    寻路是否完成由后续帧的 IsShiFuDialogVisible 条件节点判断。

    前置条件（由外部 Sequence 保证）：
        blackboard.sect_task.task_info 不为 None 且状态为 CLAIMABLE。

    返回值：
        RUNNING : 点击已发出，等待下帧确认对话框出现
        FAILURE : task_info 或 action_point 为 None，无法执行点击
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        if task_info is None or task_info.action_point is None:
            logger.warning("[TriggerGoToShiFu] task_info 或 action_point 为 None，无法点击")
            return NodeStatus.FAILURE

        # 已经触发过寻路，本帧直接等待，不再重复点击
        if blackboard.sect_task.go_to_shi_fu_triggered:
            logger.debug("[TriggerGoToShiFu] 寻路已触发，等待对话框出现")
            return NodeStatus.RUNNING

        logger.info(
            "[TriggerGoToShiFu] 点击「师父」超链接 @ %s，触发寻路",
            task_info.action_point,
        )
        await blackboard.client.main_hud.go_to_shi_fu()
        blackboard.sect_task.go_to_shi_fu_triggered = True
        return NodeStatus.RUNNING
