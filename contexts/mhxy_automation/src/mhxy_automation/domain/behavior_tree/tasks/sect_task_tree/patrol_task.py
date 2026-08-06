"""巡逻师门任务分支树构建。"""

from mhxy_automation.domain.behavior_tree.actions.sect_task.click_target_in_task_panel import (
    ClickTargetInTaskPanel,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_task_type import (
    CheckTaskType,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_dialog_visible import (
    IsDialogVisible,
)
from mhxy_automation.domain.behavior_tree.core import BaseNode, Ensure, MemorySequence
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    ensure_close_dialog,
)
from mhxy_client.models.sect_task import TaskType


def build_patrol_task() -> BaseNode:
    """构建巡逻师门任务分支树。"""
    ensure_win = Ensure(
        condition=IsDialogVisible(),
        action=ClickTargetInTaskPanel(),
    )
    return MemorySequence(
        children=[
            CheckTaskType(task_type=TaskType.PATROL),
            ensure_win,
            ensure_close_dialog,
            ensure_win,
        ]
    )
