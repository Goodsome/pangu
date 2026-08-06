"""条件节点：师父对话框是否已出现。"""

import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode, Condition
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class IsShiFuDialogVisible(Condition):
    """检查师父（默认：镇元大仙）的 NPC 对话框是否已在当前帧出现。

    通过调用 client.main_hud.dialogs.zhen_yuan_da_xian.check_visible()
    进行 OCR 检查。该调用消耗当前帧缓存数据，不触发新帧捕获。

    返回值：
        SUCCESS : 对话框已出现（寻路完成，到达师父处）
        FAILURE : 对话框尚未出现
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        dialog = blackboard.client.main_hud.dialogs.zhen_yuan_da_xian
        visible = await dialog.check_visible()
        if visible:
            logger.info("[IsShiFuDialogVisible] 镇元大仙对话框已出现")
            return NodeStatus.SUCCESS
        logger.debug("[IsShiFuDialogVisible] 对话框尚未出现，继续等待")
        return NodeStatus.FAILURE
