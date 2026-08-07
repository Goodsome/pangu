"""买物师门任务分支树构建。"""

from mhxy_automation.domain.behavior_tree.actions.sect_task.buy_item import BuyItem
from mhxy_automation.domain.behavior_tree.actions.sect_task.choose_item import (
    ChooseItem,
)
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
    BaseNode,
    Ensure,
    MemorySequence,
    Not,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    EnsureCloseDialog,
)
from mhxy_client.models.sect_task import TaskType


def build_shopping_tree() -> BaseNode:
    """构建买物师门任务分支树。"""
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
    ensure_buy_item = Ensure(
        condition=IsDialogVisible(),
        action=BuyItem(),
    )
    ensure_close_shop_panel = Ensure(
        condition=Not(IsShopPanelVisible()),
        action=CloseShopPanel(),
    )
    return MemorySequence(
        children=[
            CheckTaskType(TaskType.SHOPPING),
            ensure_to_shop_map,
            ensure_to_shop,
            Wait(duration=3),
            ensure_open_shop_dialog,
            ensure_open_shop_panel,
            ChooseItem(),
            ensure_buy_item,
            EnsureCloseDialog(),
            ensure_close_shop_panel,
            RefreshTaskInfo(),
        ]
    )
