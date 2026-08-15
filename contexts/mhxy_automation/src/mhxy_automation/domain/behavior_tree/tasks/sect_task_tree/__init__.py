"""师门任务行为树装配模块。"""

from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.patrol_task import (
    build_patrol_task,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.report_task import (
    build_report_tree,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.root_tree import (
    build_sect_task_tree,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.send_mail_task import (
    build_send_mail_tree,
)
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree.shopping_task import (
    build_shopping_tree,
)

__all__ = [
    "build_patrol_task",
    "build_report_tree",
    "build_sect_task_tree",
    "build_send_mail_tree",
    "build_shopping_tree",
]
