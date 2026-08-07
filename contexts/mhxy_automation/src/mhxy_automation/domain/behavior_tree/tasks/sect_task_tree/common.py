"""师门任务通用保障节点 (Ensure)。"""

from dataclasses import dataclass, field
from multiprocessing import Condition

from mhxy_automation.domain.behavior_tree.actions.sect_task import CloseDialog
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_target_in_task_panel import (
    ClickTargetInTaskPanel,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.return_shi_meng import (
    ReturnShiMeng,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_current_map import (
    IsInShiMengMap,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_dialog_visible import (
    IsDialogVisible,
)
from mhxy_automation.domain.behavior_tree.core import Action, Ensure, Not


ensure_in_shi_meng = Ensure(
    condition=IsInShiMengMap(),
    action=ReturnShiMeng(),
)

ensure_shifu_dialog = Ensure(
    condition=IsDialogVisible(),
    action=ClickTargetInTaskPanel(),
)

ensure_close_dialog = Ensure(
    condition=Not(IsDialogVisible()),
    action=CloseDialog(),
)


@dataclass
class EnsureInShiMeng(Ensure):
    condition: Condition = field(default_factory=lambda: IsInShiMengMap())
    action: Action = field(default_factory=lambda: ReturnShiMeng())
    

@dataclass
class EnsureShiFuDialog(Ensure):
    condition: Condition = field(default_factory=lambda: IsDialogVisible())
    action: Action = field(default_factory=lambda: ClickTargetInTaskPanel())

@dataclass
class EnsureCloseDialog(Ensure):
    condition: Condition = field(default_factory=lambda: Not(IsDialogVisible()))
    action: Action = field(default_factory=lambda: CloseDialog())
