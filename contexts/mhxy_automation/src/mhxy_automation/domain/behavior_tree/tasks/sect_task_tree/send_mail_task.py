"""送信师门任务分支树构建。"""

from dataclasses import dataclass, field

from mhxy_automation.domain.behavior_tree.actions.sect_task.click_target_in_task_panel import (
    ClickTargetInTaskPanel,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_task_in_dialog import (
    ClickTaskInDialog,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.confirm_give import (
    ConfirmGive,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.refresh_task_info import (
    RefreshTaskInfo,
)
from mhxy_automation.domain.behavior_tree.actions.wait import Wait
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_task_type import (
    CheckTaskType,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_panel_visible import (
    IsPanelVisible,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_target_dialog_visible import (
    IsTargetDialogVisible,
)
from mhxy_automation.domain.behavior_tree.core import (
    Action,
    BaseNode,
    Condition,
    Ensure,
    MemorySequence,
    RunningAction,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    EnsureCloseDialog,
)
from mhxy_client.models.sect_task import TaskType


@dataclass
class EnsureTargetDialog(Ensure):
    condition: Condition = field(default_factory=lambda: IsTargetDialogVisible())
    action: RunningAction | Action = field(
        default_factory=lambda: ClickTargetInTaskPanel()
    )


@dataclass
class EnsureGivenPanel(Ensure):
    condition: Condition = field(
        default_factory=lambda: IsPanelVisible(panel_name="given")
    )
    action: RunningAction | Action = field(default_factory=lambda: ClickTaskInDialog())


@dataclass
class EnsureGive(Ensure):
    condition: Condition = field(default_factory=lambda: IsTargetDialogVisible())
    action: RunningAction | Action = field(default_factory=lambda: ConfirmGive())


def build_send_mail_tree() -> BaseNode:
    """构建送信师门任务分支树。"""
    return MemorySequence(
        children=[
            CheckTaskType(task_type=TaskType.SEND_MAIL),
            EnsureTargetDialog(),
            EnsureGivenPanel(),
            EnsureGive(),
            EnsureCloseDialog(),
            Wait(),
            RefreshTaskInfo(),
        ]
    )
