"""师门任务通用保障节点 (Ensure)。"""

from dataclasses import dataclass, field

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
from mhxy_automation.domain.behavior_tree.core import (
    Action,
    Condition,
    Ensure,
    Not,
    RunningAction,
)


@dataclass
class EnsureInShiMeng(Ensure):
    condition: Condition = field(default_factory=lambda: IsInShiMengMap())
    action: RunningAction | Action = field(default_factory=lambda: ReturnShiMeng())


@dataclass
class EnsureShifuDialog(Ensure):
    condition: Condition = field(default_factory=lambda: IsDialogVisible())
    action: RunningAction | Action = field(
        default_factory=lambda: ClickTargetInTaskPanel()
    )


@dataclass
class EnsureCloseDialog(Ensure):
    condition: Condition = field(default_factory=lambda: Not(IsDialogVisible()))
    action: RunningAction | Action = field(default_factory=lambda: CloseDialog())
