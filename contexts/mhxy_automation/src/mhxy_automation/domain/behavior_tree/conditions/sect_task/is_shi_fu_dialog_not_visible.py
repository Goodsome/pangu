"""条件节点：师父 NPC 对话框是否已关闭。"""

import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class IsShiFuDialogNotVisible(BaseNode):
    """检查师父（镇元大仙）NPC 对话框是否已关闭（不可见）。

    IsShiFuDialogVisible 的逻辑取反：对话框不存在时返回 SUCCESS，
    用于「确保对话框已关闭」的 Selector 守卫节点。

    返回值：
        SUCCESS : 对话框不可见（已关闭）
        FAILURE : 对话框仍然可见
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        dialog = blackboard.client.main_hud.dialogs.zhen_yuan_da_xian
        visible = await dialog.check_visible()
        if not visible:
            logger.debug("[IsShiFuDialogNotVisible] 对话框已关闭")
            return NodeStatus.SUCCESS
        logger.debug("[IsShiFuDialogNotVisible] 对话框仍然可见")
        return NodeStatus.FAILURE
