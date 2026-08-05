"""师门任务行为树装配工厂。

本模块负责将各节点组装成完整的师门任务执行树。

树结构
------

Sequence [师门任务总流程]
├── CheckSectTask              # Action: OCR 检查任务状态并写入黑板
├── IsSectTaskClaimable        # Condition: 任务是否处于可领取状态？
│   FAILURE → 整棵树 FAILURE（当前不需要操作）
├── Selector [等待/触发师父对话框]
│   ├── IsShiFuDialogVisible   # Condition: 对话框已出现 → SUCCESS → 继续
│   └── TriggerGoToShiFu       # Action: 点击「师父」超链接 → RUNNING
└── ClaimSectTask              # Action: 点击「师门任务」选项，领取任务

单帧执行时序
-----------
第 1 帧: CheckSectTask → CLAIMABLE
         → Selector: IsShiFuDialogVisible=FAILURE → TriggerGoToShiFu → RUNNING
第 N 帧: CheckSectTask → CLAIMABLE
         → Selector: IsShiFuDialogVisible=SUCCESS
         → ClaimSectTask: 首次点击 → RUNNING
第 N+1 帧: CheckSectTask → CLAIMABLE (游戏尚未响应)
           → Selector: IsShiFuDialogVisible=SUCCESS (对话框仍在)
           → ClaimSectTask: _has_claimed=True → 静默 RUNNING
第 M 帧:  CheckSectTask → IN_PROGRESS (任务已领取)
           → IsSectTaskClaimable=FAILURE → Sequence FAILURE → 本轮结束
"""

from mhxy_automation.domain.behavior_tree.actions.sect_task import (
    CheckSectTask,
    ClaimSectTask,
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
            ClaimSectTask(),
        ]
    )
