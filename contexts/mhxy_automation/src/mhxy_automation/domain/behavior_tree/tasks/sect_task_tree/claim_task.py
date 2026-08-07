"""领取师门任务分支树构建。"""

from mhxy_automation.domain.behavior_tree.actions.sect_task import ClaimSectTask
from mhxy_automation.domain.behavior_tree.actions.sect_task.refresh_task_info import (
    RefreshTaskInfo,
)
from mhxy_automation.domain.behavior_tree.actions.wait import Wait
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_task_status import (
    IsTaskStatus,
)
from mhxy_automation.domain.behavior_tree.core import BaseNode, MemorySequence
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.common import (
    EnsureCloseDialog,
    EnsureInShiMeng,
    EnsureShifuDialog,
)
from mhxy_client import SectTaskStatus


def build_claim_task() -> BaseNode:
    """构建领取师门任务分支树。"""
    return MemorySequence(
        children=[
            IsTaskStatus(status=SectTaskStatus.CLAIMABLE),
            EnsureCloseDialog(),
            EnsureInShiMeng(),
            EnsureShifuDialog(),
            ClaimSectTask(),
            EnsureCloseDialog(),
            Wait(),
            RefreshTaskInfo(),
        ]
    )
