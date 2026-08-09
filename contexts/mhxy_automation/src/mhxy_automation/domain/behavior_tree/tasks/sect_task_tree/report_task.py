"""交付/复命师门任务分支树构建。"""

from dataclasses import dataclass, field

from mhxy_automation.domain.behavior_tree.actions.sect_task.click_task_in_dialog import (
    ClickTaskInDialog,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.confirm_give import (
    ConfirmGive,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.refresh_task_info import (
    RefreshTaskInfo,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.report_task_in_dialog import (
    ReportTaskInDialog,
)
from mhxy_automation.domain.behavior_tree.actions.wait import Wait
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_task_type import (
    CheckTaskType,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_dialog_visible import (
    IsDialogVisible,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_panel_visible import (
    IsPanelVisible,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_task_status import (
    IsTaskStatus,
)
from mhxy_automation.domain.behavior_tree.core import (
    BaseNode,
    Condition,
    Ensure,
    IfThenElse,
    MemorySequence,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    EnsureCloseDialog,
    EnsureInShiMeng,
    EnsureShifuDialog,
)
from mhxy_client import SectTaskStatus
from mhxy_client.models.sect_task import TaskType


@dataclass
class ReportOrGive(IfThenElse):
    condition: Condition = field(
        default_factory=lambda: CheckTaskType(TaskType.SHOPPING)
    )
    if_node: BaseNode = field(
        default_factory=lambda: MemorySequence(
            children=[
                Ensure(
                    condition=IsPanelVisible("given"),
                    action=ClickTaskInDialog(),
                ),
                Ensure(
                    condition=IsDialogVisible(),
                    action=ConfirmGive(),
                ),
                EnsureCloseDialog(),
            ]
        )
    )
    else_node: BaseNode = field(default_factory=lambda: ReportTaskInDialog())


def build_report_tree() -> BaseNode:
    """构建交付/复命师门任务分支树。"""
    return MemorySequence(
        children=[
            IsTaskStatus(status=SectTaskStatus.REPORT),
            # EnsureInShiMeng(),
            EnsureShifuDialog(),
            ReportOrGive(),
            Wait(1),
            EnsureCloseDialog(),
            RefreshTaskInfo(),
        ]
    )
