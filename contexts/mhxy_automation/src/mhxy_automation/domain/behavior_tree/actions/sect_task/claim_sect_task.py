"""动作节点：点击师门对话框中的「师门任务」选项，领取任务。"""

import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class ClaimSectTask(BaseNode):
    """点击 NPC 对话框中的「师门任务」选项，触发任务领取。

    领取动作是瞬时的：点击后游戏立即将任务状态切换为 IN_PROGRESS，
    无需等待确认。本节点直接返回 SUCCESS，将流程控制权交还上层。

    前置条件（由外部 Sequence 保证）：
        - 师父 NPC 对话框已出现（IsShiFuDialogVisible 已成功）

    返回值：
        SUCCESS : 点击操作已发出
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        dialog = blackboard.client.main_hud.dialogs.zhen_yuan_da_xian
        logger.info("[ClaimSectTask] 点击「师门任务」选项，领取任务")
        await dialog.claim_task()
        return NodeStatus.SUCCESS
