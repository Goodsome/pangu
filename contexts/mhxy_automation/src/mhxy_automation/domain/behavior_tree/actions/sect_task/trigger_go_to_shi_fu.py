"""动作节点：点击任务追踪面板中的「师父」超链接触发寻路。"""

import logging
from dataclasses import dataclass, field
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

    内部状态
    --------
    _has_triggered : 是否已发出过点击，防止在寻路途中反复触发点击。
                     由框架在寻路完成（Selector 的更高优先级条件成功）时
                     通过 reset() 自动清理。

    前置条件（由外部 Sequence 保证）：
        blackboard.sect_task.task_info 不为 None 且状态为 CLAIMABLE。

    返回值：
        RUNNING : 点击已发出（或已在等待中）
        FAILURE : task_info 或 action_point 为 None，无法执行点击
    """

    _has_triggered: bool = field(default=False, init=False, repr=False)

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        task_info = blackboard.sect_task.task_info
        if task_info.action_point is None:
            logger.warning(
                "[TriggerGoToShiFu] action_point 为 None，无法点击"
            )
            return NodeStatus.FAILURE

        if self._has_triggered:
            logger.debug("[TriggerGoToShiFu] 寻路已触发，等待对话框出现")
            return NodeStatus.RUNNING

        logger.info(
            "[TriggerGoToShiFu] 点击「师父」超链接 @ %s，触发寻路",
            task_info.action_point,
        )
        await blackboard.client.main_hud.go_to_shi_fu()
        self._has_triggered = True
        return NodeStatus.RUNNING

    @override
    def _reset(self) -> None:
        self._has_triggered = False
