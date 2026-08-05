"""动作节点：关闭师父 NPC 对话框。"""

import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class CloseShiFuDialog(BaseNode):
    """右键关闭师父（镇元大仙）NPC 对话框。

    关闭操作是瞬时的，直接返回 SUCCESS。

    返回值：
        SUCCESS : 关闭指令已发出
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        dialog = blackboard.client.main_hud.dialogs.zhen_yuan_da_xian
        logger.info("[CloseShiFuDialog] 关闭师父对话框")
        await dialog.close_dialog()
        return NodeStatus.SUCCESS
