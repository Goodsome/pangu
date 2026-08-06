"""梦幻西游自动化黑板 (Blackboard) 聚合根。

Blackboard 是行为树各节点之间共享状态的载体，每帧 tick 时传递给根节点。
"""

from dataclasses import dataclass, field

from mhxy_client import MhxyClient
from mhxy_client.models import SectTaskInfo


@dataclass
class SectTaskContext:
    """师门任务跨帧状态上下文。

    仅存储需要跨帧共享的**领域数据**（如 OCR 解析结果），
    不存储任何具体节点的执行状态（节点状态由节点自身通过 reset() 管理）。
    """

    _task_info: SectTaskInfo | None = None
    """最近一次 check_sect_task 的解析结果，None 表示尚未检查。"""

    @property
    def task_info(self):
        if self._task_info is None:
            raise ValueError("Task info is not available")
        return self._task_info

    def set_task_info(self, task_info: SectTaskInfo | None):
        self._task_info = task_info
        
    def clear_task_info(self):
        self._task_info = None

    def has_task_info(self) -> bool:
        return self._task_info is not None

@dataclass
class MainHudContext:
    target_npc: str | None = None

@dataclass
class Blackboard:
    """行为树黑板，持有 MhxyClient 与任务专用上下文。

    每帧开始前须先调用 client.begin_frame() 刷新画面缓存，
    再将本 Blackboard 传入行为树根节点的 tick()。
    """

    client: MhxyClient
    sect_task: SectTaskContext = field(default_factory=SectTaskContext)
    main_ctx: MainHudContext = field(default_factory=MainHudContext)

    @property
    def main_hud(self):
        return self.client.main_hud