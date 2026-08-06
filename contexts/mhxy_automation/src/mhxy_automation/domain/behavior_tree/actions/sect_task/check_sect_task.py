"""动作节点：检查师门任务状态并写入黑板。"""

import logging
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)


@dataclass
class CheckSectTask(BaseNode):
    """调用 OCR 检查师门任务状态，将解析结果写入 blackboard.sect_task.task_info。

    本节点始终返回 SUCCESS——"检查"动作本身总能完成，
    任务是否处于目标状态由后续条件节点判断。

    副作用：
        blackboard.sect_task.task_info 被更新为最新解析结果（或 None）。

    返回值：
        SUCCESS : 检查动作已完成（不论任务状态如何）
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        if blackboard.sect_task.has_task_info():
            return NodeStatus.SUCCESS
        
        hud = blackboard.client.main_hud
        try:
            task_info = await hud.check_sect_task()
        except Exception:
            logger.exception("[CheckSectTask] 检查师门任务时发生异常")
            blackboard.sect_task.set_task_info(None)
            return NodeStatus.FAILURE

        blackboard.sect_task.set_task_info(task_info)
        logger.info(
            "[CheckSectTask] 任务状态: %s, 描述: %s",
            task_info.status,
            task_info.full_description,
        )
        return NodeStatus.SUCCESS
