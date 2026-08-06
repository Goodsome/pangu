"""师门任务行为树装配工厂。

本模块负责将各节点组装成完整的师门任务执行树。

树结构
------

Sequence [师门任务总主控]
├── CheckSectTask                      # Action: OCR 检查任务状态并写入黑板
└── Selector [按任务状态分发执行]
    ├── Sequence [IN_PROGRESS 任务执行分支]
    │   ├── IsSectTaskInProgress        # Condition: 状态是否为 IN_PROGRESS？
    │   └── Selector [关闭对话框保障]
    │       ├── IsShiFuDialogNotVisible # Condition: 对话框已关闭 → SUCCESS
    │       └── CloseShiFuDialog        # Action: 对话框仍打开 → 右键关闭
    │
    └── Sequence [CLAIMABLE 任务领取分支]
        ├── IsSectTaskClaimable        # Condition: 状态是否为 CLAIMABLE？
        ├── Selector [等待/触发师父对话框]
        │   ├── IsShiFuDialogVisible   # Condition: 对话框已出现 → SUCCESS
        │   └── TriggerGoToShiFu       # Action: 点击「师父」超链接 → RUNNING
        └── ClaimSectTask              # Action: 点击「师门任务」选项，领取任务
"""

from mhxy_automation.domain.behavior_tree.actions.sect_task import (
    CheckSectTask,
    ClaimSectTask,
    CloseShiFuDialog,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_target_in_task_panel import ClickTargetInTaskPanel
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_task_in_dialog import ClickTaskInDialog
from mhxy_automation.domain.behavior_tree.actions.sect_task.confirm_give import ConfirmGive
from mhxy_automation.domain.behavior_tree.actions.sect_task.go_to_shop_map import GoToShopMap
from mhxy_automation.domain.behavior_tree.actions.sect_task.return_shi_meng import ReturnShiMeng
from mhxy_automation.domain.behavior_tree.conditions.sect_task import (
    IsSectTaskClaimable,
    IsSectTaskInProgress,
    IsShiFuDialogNotVisible,
    IsShiFuDialogVisible,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_shopping_map import CheckShoppingMap
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_task_type import CheckTaskType
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_current_map import IsInMap
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_task_status import IsTaskStatus
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_send_mail_task import IsSendMailTask
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_target_dialog_visible import IsTargetDialogVisible
from mhxy_automation.domain.behavior_tree.core import BaseNode, Ensure, Selector, Sequence
from mhxy_client import SectTaskStatus
from mhxy_client.models.sect_task import TaskType


def build_shopping_tree() -> BaseNode:
    ensure_to_shop_map = Ensure(
        condition=CheckShoppingMap(),
        action=GoToShopMap(),
    )
    shopping = Sequence(
        children=[
            CheckTaskType(TaskType.SHOPPING),
            ensure_to_shop_map,
        ]
    )
    return shopping
    

def build_sect_task_tree() -> BaseNode:
    """装配师门任务行为树并返回根节点。"""
    # 1. CLAIMABLE 状态分支：寻路找师父并领取任务
    wait_or_trigger_shifu = Selector(
        children=[
            IsShiFuDialogVisible(),
            ClickTargetInTaskPanel(),
        ]
    )
    claim_task_branch = Sequence(
        children=[
            IsSectTaskClaimable(),
            wait_or_trigger_shifu,
            ClaimSectTask(),
        ]
    )

    # 2. IN_PROGRESS 状态分支：关对话框 + 执行后续子任务
    close_dialog_if_needed = Selector(
        children=[
            IsShiFuDialogNotVisible(),
            CloseShiFuDialog(),
        ]
    )
    go_to_target = Ensure(
        condition=IsTargetDialogVisible(),
        action=ClickTargetInTaskPanel(),
    )
    send_mail = Sequence(
        children=[
            IsSendMailTask(),
            go_to_target,
            ClickTaskInDialog(),
            ConfirmGive(),
        ]
    )
    dispatch_task = Selector(
        children=[
            send_mail,
            build_shopping_tree(),
        ]
    )
    in_progress_branch = Sequence(
        children=[
            IsSectTaskInProgress(),
            close_dialog_if_needed,
            dispatch_task,
        ]
    )

    return_shi_meng = Ensure(
        condition=IsInMap(["五庄观", "镇元殿"]),
        action=ReturnShiMeng(),
    )

    report_task_branch = Sequence(
        children=[
            IsTaskStatus(status=SectTaskStatus.REPORT),
            # close dialog
            return_shi_meng,
            wait_or_trigger_shifu,
            ClickTaskInDialog(),
        ]
    )

    # 3. 根节点：每次先刷新状态，再进入分支分发
    return Sequence(
        children=[
            CheckSectTask(),
            Selector(
                children=[
                    claim_task_branch,
                    in_progress_branch,
                    report_task_branch,
                ]
            ),
        ]
    )
