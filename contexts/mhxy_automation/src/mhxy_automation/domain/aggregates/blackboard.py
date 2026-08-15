"""梦幻西游自动化黑板 (Blackboard) 聚合根。

Blackboard 是行为树各节点之间共享状态的载体，每帧 tick 时传递给根节点。
"""

import asyncio
from dataclasses import dataclass, field

from mhxy_client import MhxyClient
from mhxy_client.models import SectTaskInfo

_INIT_FINISH_COUNTS = {
    "0": 0,
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 0,
}

@dataclass
class SectTaskContext:
    """师门任务跨帧状态上下文。

    仅存储需要跨帧共享的**领域数据**（如 OCR 解析结果），
    不存储任何具体节点的执行状态（节点状态由节点自身通过 reset() 管理）。
    """

    _task_info: SectTaskInfo | None = None
    finish_count: int = 0

    @property
    def task_info(self):
        if self._task_info is None:
            raise ValueError("Task info is not available")
        return self._task_info

    def set_task_info(self, task_info: SectTaskInfo | None):
        self._task_info = task_info

    def has_task_info(self) -> bool:
        return self._task_info is not None

    @property
    def finished(self) -> bool:
        return self.finish_count >= 20


@dataclass
class MainHudContext:
    current_map: str | None = None
    current_house: str | None = None
    target_npc: str | None = None


@dataclass
class Blackboard:
    """行为树黑板，持有 MhxyClient 与任务专用上下文。

    每帧开始前须先调用 client.begin_frame() 刷新画面缓存，
    再将本 Blackboard 传入行为树根节点的 tick()。
    """

    client: MhxyClient
    input_lock: asyncio.Lock
    sect_task: SectTaskContext = field(default_factory=SectTaskContext)
    main_ctx: MainHudContext = field(default_factory=MainHudContext)

    _holds_input_lock: bool = False

    def __post_init__(self):
        window_idx = self.client.window.idx
        self.sect_task.finish_count = _INIT_FINISH_COUNTS[str(window_idx)]

    @property
    def main_hud(self):
        return self.client.main_hud

    async def acquire_input_lock(self):
        if self._holds_input_lock:
            return
        await self.input_lock.acquire()
        self._holds_input_lock = True

        self.client.activate()

    async def release_input_lock(self):
        if not self._holds_input_lock:
            return
        self.input_lock.release()
        self._holds_input_lock = False