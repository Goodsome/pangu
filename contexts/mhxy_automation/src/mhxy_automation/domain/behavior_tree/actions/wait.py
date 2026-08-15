import time
from dataclasses import dataclass, field
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class Wait(Action):
    duration: float = 0.1  # 等待秒数
    _start_time: float | None = field(default=None, init=False, repr=False)

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        now = time.monotonic()

        if self._start_time is None:
            self._start_time = now
            return NodeStatus.RUNNING

        # 计算已逝去的时间
        elapsed = now - self._start_time
        if elapsed >= self.duration:
            # 等待完成，顺便清理状态以便下次使用
            self._start_time = None
            return NodeStatus.SUCCESS

        return NodeStatus.RUNNING

    @override
    def reset(self) -> None:
        """如果等待过程中被更高优先级的逻辑打断，必须重置计时器。"""
        self._start_time = None
