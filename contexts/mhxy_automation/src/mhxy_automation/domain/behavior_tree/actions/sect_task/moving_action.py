from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import RunningAction
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class MovingAction(RunningAction, ABC):
    stationary_timeout: float = 10
    _stationary_start_time: float | None = field(default=None, init=False, repr=False)

    @override
    async def on_start(self, blackboard: Blackboard) -> None:

        self._stationary_start_time = None
        await self._on_start(blackboard)

    @abstractmethod
    async def _on_start(self, blackboard: Blackboard) -> None: ...

    @override
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        is_moving = await blackboard.client.main_hud.is_moving()
        now = time.monotonic()
        if is_moving:
            self._stationary_start_time = None
            return NodeStatus.RUNNING

        if self._stationary_start_time is None:
            self._stationary_start_time = now
            return NodeStatus.RUNNING

        elapsed_stationary_time = now - self._stationary_start_time
        if elapsed_stationary_time >= self.stationary_timeout:
            self._stationary_start_time = None
            return NodeStatus.SUCCESS

        return NodeStatus.RUNNING

    @override
    def on_reset(self) -> None:
        self._stationary_start_time = None
