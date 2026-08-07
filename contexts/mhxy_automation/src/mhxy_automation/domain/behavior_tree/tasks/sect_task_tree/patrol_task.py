"""巡逻师门任务分支树构建。"""

from mhxy_automation.domain.behavior_tree.actions.sect_task.refresh_task_info import (
    RefreshTaskInfo,
)
from mhxy_automation.domain.behavior_tree.actions.wait import Wait
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_task_type import (
    CheckTaskType,
)
from mhxy_automation.domain.behavior_tree.core import BaseNode, MemorySequence
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    EnsureCloseDialog,
    EnsureShifuDialog,
)
from mhxy_client.models.sect_task import TaskType


def build_patrol_task() -> BaseNode:
    """构建巡逻师门任务分支树。"""
    return MemorySequence(
        children=[
            CheckTaskType(task_type=TaskType.PATROL),
            EnsureShifuDialog(),
            EnsureCloseDialog(),
            EnsureShifuDialog(),
            EnsureCloseDialog(),
            Wait(),
            RefreshTaskInfo(),
        ]
    )
