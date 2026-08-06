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
    CloseDialog,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.buy_item import BuyItem
from mhxy_automation.domain.behavior_tree.actions.sect_task.choose_item import ChooseItem
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_target_in_task_panel import ClickTargetInTaskPanel
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_task_in_dialog import ClickTaskInDialog
from mhxy_automation.domain.behavior_tree.actions.sect_task.confirm_give import ConfirmGive
from mhxy_automation.domain.behavior_tree.actions.sect_task.go_to_shop import GoToShop
from mhxy_automation.domain.behavior_tree.actions.sect_task.go_to_shop_map import GoToShopMap
from mhxy_automation.domain.behavior_tree.actions.sect_task.open_shop_dialog import OpenShopDialog
from mhxy_automation.domain.behavior_tree.actions.sect_task.open_shop_panel import OpenShopPanel
from mhxy_automation.domain.behavior_tree.actions.sect_task.refresh_task_info import RefreshTaskInfo
from mhxy_automation.domain.behavior_tree.actions.sect_task.return_shi_meng import ReturnShiMeng
from mhxy_automation.domain.behavior_tree.conditions.sect_task import (
    IsSectTaskClaimable,
    IsSectTaskInProgress,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_shop import CheckShop
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_shop_map import CheckShopMap
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_task_type import CheckTaskType
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_current_map import IsInMap
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_dialog_visible import IsDialogVisible
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_panel_visible import IsPanelVisible
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_shop_dialog_visible import IsShopDialogVisible
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_shop_panel_visible import IsShopPanelVisible
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_task_status import IsTaskStatus
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_send_mail_task import IsSendMailTask
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_target_dialog_visible import IsTargetDialogVisible
from mhxy_automation.domain.behavior_tree.core import BaseNode, Ensure, IfThenElse, Not, Selector, Sequence, When
from mhxy_client import SectTaskStatus
from mhxy_client.models.sect_task import TaskType

ensure_shifu_dialog = Ensure(
    condition=IsDialogVisible("镇元大仙"),
    action=ClickTargetInTaskPanel(),
)

ensure_close_dialog = Ensure(
    condition=Not(IsDialogVisible()),
    action=CloseDialog(),
)

def build_shopping_tree() -> BaseNode:
    ensure_to_shop_map = Ensure(
        condition=CheckShopMap(),
        action=GoToShopMap(),
    )
    ensure_to_shop = Ensure(
        condition=CheckShop(),
        action=GoToShop(),
    )
    ensure_open_shop_dialog = Ensure(
        condition=IsShopDialogVisible(),
        action=OpenShopDialog(),
    )
    ensure_open_shop_panel = Ensure(
        condition=IsShopPanelVisible(),
        action=OpenShopPanel(),
    )
    shopping = Sequence(
        children=[
            CheckTaskType(TaskType.SHOPPING),
            ensure_to_shop_map,
            ensure_to_shop,
            ensure_open_shop_dialog,
            ensure_open_shop_panel,
            ChooseItem(),
            BuyItem(),
        ]
    )
    return shopping
    

def build_report_tree(
    ensure_shifu_dialog: Ensure,
) -> BaseNode:
    
    ensure_in_shi_meng = Ensure(
        condition=IsInMap(["五庄观", "乾坤殿"]),
        action=ReturnShiMeng(),
    )
    ensure_given_panel = Ensure(
        condition=IsPanelVisible("given"),
        action=ClickTaskInDialog(),
    )
    give_item = Sequence(
        children=[
            ensure_given_panel,
            ConfirmGive()
        ]
    )
    report_or_give = IfThenElse(
        condition=CheckTaskType(task_type=TaskType.SHOPPING),
        if_node=give_item,
        else_node=ClickTaskInDialog(),
    )
    return Sequence(
        children=[
            IsTaskStatus(status=SectTaskStatus.REPORT),
            ensure_in_shi_meng,
            ensure_shifu_dialog,
            ClickTaskInDialog(),
            report_or_give,
            ensure_close_dialog,
            RefreshTaskInfo(),
        ]
    )

def build_send_mail_tree() -> BaseNode:
    
    ensure_dialog = Ensure(
        condition=IsTargetDialogVisible(),
        action=ClickTargetInTaskPanel(),
    )
    ensure_given_panel = Ensure(
        condition=IsPanelVisible("given"),
        action=ClickTaskInDialog(),
    )
    ensure_give = Ensure(
        condition=IsTargetDialogVisible(),
        action=ConfirmGive(),
    )
    
    return Sequence(
        children=[
            IsSendMailTask(),
            ensure_dialog,
            ensure_given_panel,
            ensure_give,
            ensure_close_dialog,
            RefreshTaskInfo(),
        ]
    )
    
def build_sect_task_tree() -> BaseNode:
    """装配师门任务行为树并返回根节点。"""
    # 1. CLAIMABLE 状态分支：寻路找师父并领取任务
    claim_task_branch = Sequence(
        children=[
            IsSectTaskClaimable(),
            ensure_shifu_dialog,
            ClaimSectTask(),
            ensure_close_dialog,
            RefreshTaskInfo(),
        ]
    )
    dispatch_task = Selector(
        children=[
            build_send_mail_tree(),
            build_shopping_tree(),
        ]
    )
    in_progress_branch = Sequence(
        children=[
            IsSectTaskInProgress(),
            dispatch_task,
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
                    build_report_tree(ensure_shifu_dialog),
                ]
            ),
        ]
    )
