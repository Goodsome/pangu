"""交付/复命师门任务分支树构建。"""

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
    Ensure,
    IfThenElse,
    MemorySequence,
    Sequence,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    ensure_close_dialog,
    ensure_in_shi_meng,
    ensure_shifu_dialog,
)
from mhxy_automation.domain.enums import NodeStatus
from mhxy_client import SectTaskStatus
from mhxy_client.models.sect_task import TaskType


def build_report_tree() -> BaseNode:
    """构建交付/复命师门任务分支树。"""
    ensure_given_panel = Ensure(
        condition=IsPanelVisible("given"),
        action=ClickTaskInDialog(),
    )
    ensure_give = Ensure(
        condition=IsDialogVisible(),
        action=ConfirmGive(),
    )
    give_item = MemorySequence(
        children=[
            ensure_given_panel,
            ensure_give,
            ensure_close_dialog,
        ]
    )
    report_or_give = IfThenElse(
        condition=CheckTaskType(task_type=TaskType.SHOPPING),
        if_node=give_item,
        else_node=ClickTaskInDialog(default_return=NodeStatus.SUCCESS),
    )
    return MemorySequence(
        children=[
            IsTaskStatus(status=SectTaskStatus.REPORT),
            ensure_in_shi_meng,
            ensure_shifu_dialog,
            report_or_give,
            Wait(),
            RefreshTaskInfo(),
        ]
    )
