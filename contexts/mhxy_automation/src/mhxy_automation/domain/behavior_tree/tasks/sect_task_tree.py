"""师门任务行为树装配工厂。

本模块负责将各节点组装成完整的师门任务执行树。

树结构
------

Sequence [师门任务总流程]
├── CheckSectTask              # Action: OCR 检查任务状态并写入黑板
├── IsSectTaskClaimable        # Condition: 任务是否处于可领取状态？
│   FAILURE → 整棵树 FAILURE（当前不需要操作）
└── Selector [等待/触发师父对话框]
    ├── IsShiFuDialogVisible   # Condition: 对话框已出现 → SUCCESS → 完成
    └── TriggerGoToShiFu       # Action: 点击「师父」超链接 → RUNNING

单帧执行时序
-----------
第 1 帧: CheckSectTask → CLAIMABLE
         → Selector: IsShiFuDialogVisible=FAILURE → TriggerGoToShiFu → RUNNING
         → Selector RUNNING → Sequence RUNNING
第 N 帧: CheckSectTask → CLAIMABLE
         → Selector: IsShiFuDialogVisible=SUCCESS
         → Selector SUCCESS → Sequence SUCCESS

关键：Selector 的语义是「遇到第一个非 FAILURE 就停」，
      IsShiFuDialogVisible FAILURE 时才会继续尝试 TriggerGoToShiFu。
"""

from mhxy_automation.domain.behavior_tree.actions.sect_task import (
    CheckSectTask,
    TriggerGoToShiFu,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task import (
    IsSectTaskClaimable,
    IsShiFuDialogVisible,
)
from mhxy_automation.domain.behavior_tree.core import BaseNode, Selector, Sequence


def build_sect_task_tree() -> BaseNode:
    """装配师门任务行为树并返回根节点。"""
    wait_or_trigger_shifu = Selector(
        children=[
            IsShiFuDialogVisible(),
            TriggerGoToShiFu(),
        ]
    )

    return Sequence(
        children=[
            CheckSectTask(),
            IsSectTaskClaimable(),
            wait_or_trigger_shifu,
        ]
    )
