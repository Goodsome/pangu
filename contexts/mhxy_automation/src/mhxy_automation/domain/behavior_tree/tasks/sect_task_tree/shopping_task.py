"""买物师门任务分支树构建。"""

from dataclasses import dataclass, field

from mhxy_automation.domain.behavior_tree.actions.sect_task.buy_item import BuyItem
from mhxy_automation.domain.behavior_tree.actions.sect_task.choose_item import (
    ChooseItem,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_target_in_task_panel import ClickTargetInTaskPanel
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_task_in_dialog import ClickTaskInDialog
from mhxy_automation.domain.behavior_tree.actions.sect_task.close_shop_panel import (
    CloseShopPanel,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.go_to_shop import GoToShop
from mhxy_automation.domain.behavior_tree.actions.sect_task.go_to_shop_map import (
    GoToShopMap,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.open_shop_dialog import (
    OpenShopDialog,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.open_shop_panel import (
    OpenShopPanel,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.refresh_task_info import (
    RefreshTaskInfo,
)
from mhxy_automation.domain.behavior_tree.actions.wait import Wait
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_shop import (
    CheckShop,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_shop_map import (
    CheckShopMap,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.check_task_type import (
    CheckTaskType,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_dialog_visible import (
    IsDialogVisible,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_shop_dialog_visible import (
    IsShopDialogVisible,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_shop_panel_visible import (
    IsShopPanelVisible,
)
from mhxy_automation.domain.behavior_tree.core import (
    Action,
    BaseNode,
    Condition,
    Ensure,
    MemorySequence,
    Not,
    RunningAction,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    EnsureCloseDialog,
)
from mhxy_client.models.sect_task import TaskType


@dataclass
class EnsureToShopMap(Ensure):
    condition: Condition = field(default_factory=lambda: CheckShopMap())
    action: RunningAction | Action = field(default_factory=lambda: GoToShopMap())


@dataclass
class EnsureToShop(Ensure):
    condition: Condition = field(default_factory=lambda: CheckShop())
    action: RunningAction | Action = field(default_factory=lambda: GoToShop())


@dataclass
class EnsureOpenShopDialog(Ensure):
    condition: Condition = field(default_factory=lambda: IsShopDialogVisible())
    action: RunningAction | Action = field(default_factory=lambda: OpenShopDialog())


@dataclass
class EnsureOpenShopPanel(Ensure):
    condition: Condition = field(default_factory=lambda: IsShopPanelVisible())
    # action: RunningAction | Action = field(default_factory=lambda: OpenShopPanel())
    action: RunningAction | Action = field(default_factory=lambda: ClickTargetInTaskPanel())


@dataclass
class EnsureBuyItem(Ensure):
    condition: Condition = field(default_factory=lambda: IsDialogVisible())
    action: RunningAction | Action = field(default_factory=lambda: BuyItem())


@dataclass
class EnsureCloseShopPanel(Ensure):
    condition: Condition = field(default_factory=lambda: Not(IsShopPanelVisible()))
    action: RunningAction | Action = field(default_factory=lambda: CloseShopPanel())


def build_shopping_tree() -> BaseNode:
    """构建买物师门任务分支树。"""
    return MemorySequence(
        children=[
            CheckTaskType(TaskType.SHOPPING),
            # EnsureToShopMap(),
            # EnsureToShop(),
            # Wait(duration=3),
            # EnsureOpenShopDialog(),
            EnsureOpenShopPanel(),
            # ChooseItem(),
            EnsureBuyItem(),
            EnsureCloseDialog(),
            EnsureCloseShopPanel(),
            RefreshTaskInfo(),
        ]
    )
