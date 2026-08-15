"""领取师门任务分支树构建。"""

from dataclasses import dataclass, field

from mhxy_automation.domain.behavior_tree.actions.sect_task import ClaimSectTask
from mhxy_automation.domain.behavior_tree.actions.sect_task.refresh_task_info import (
    RefreshTaskInfo,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.talk_to_shi_fu import TalkToShiFu
from mhxy_automation.domain.behavior_tree.actions.wait import Wait
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_dialog_visible import IsDialogVisible
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_task_status import (
    IsTaskStatus,
)
from mhxy_automation.domain.behavior_tree.core import Action, BaseNode, Condition, Ensure, MemorySequence, RunningAction
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    EnsureCloseDialog,
    EnsureInShiMeng,
)
from mhxy_client import SectTaskStatus

@dataclass
class EnsureTalkToShiFu(Ensure):
    condition: Condition = field(default_factory=lambda: IsDialogVisible())
    action: RunningAction | Action = field(
        default_factory=lambda: TalkToShiFu()
    )

@dataclass
class ClaimTask(MemorySequence):
    children: list[BaseNode] = field(default_factory=list)

    def __post_init__(self):
        self.children = [
            IsTaskStatus(status=SectTaskStatus.CLAIMABLE),
            EnsureCloseDialog(),
            # EnsureInShiMeng(),
            EnsureTalkToShiFu(),
            ClaimSectTask(),
            Wait(),
            EnsureCloseDialog(),
            RefreshTaskInfo(),
        ]
    
    