"""师门任务行为树总装配逻辑。"""

from mhxy_automation.domain.behavior_tree.actions.raise_error import RaiseError
from mhxy_automation.domain.behavior_tree.actions.sect_task import CheckSectTask
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_task_status import IsTaskStatus
from mhxy_automation.domain.behavior_tree.core import BaseNode, Selector, Sequence
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.claim_task import (
    build_claim_task,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.patrol_task import (
    build_patrol_task,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.report_task import (
    build_report_tree,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.send_mail_task import (
    build_send_mail_tree,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.shopping_task import (
    build_shopping_tree,
)
from mhxy_client.models.sect_task import SectTaskStatus


def build_sect_task_tree() -> BaseNode:
    """装配师门任务行为树并返回根节点。"""
    dispatch_task = Selector(
        children=[
            build_send_mail_tree(),
            build_shopping_tree(),
            build_patrol_task(),
            RaiseError(message="un processed task type"),
        ]
    )
    in_progress_branch = Sequence(
        children=[
            IsTaskStatus(SectTaskStatus.IN_PROGRESS),
            dispatch_task,
        ]
    )

    # 根节点：每次先刷新状态，再进入分支分发
    return Sequence(
        children=[
            CheckSectTask(),
            Selector(
                children=[
                    build_claim_task(),
                    in_progress_branch,
                    build_report_tree(),
                    RaiseError(message="task status error")
                ]
            ),
        ]
    )
