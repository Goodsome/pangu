import asyncio
from dataclasses import dataclass, field
from typing import override
import logging

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)

@dataclass
class CriticalSection(BaseNode):
    """
    临界区（排他性连贯执行）节点。
    用于包裹需要一气呵成的 UI 交互动作。
    """
    child: BaseNode
    
    # 内部状态：记录当前节点是否持有全局锁
    _held_lock: asyncio.Lock | None = field(default=None, init=False, repr=False)

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        # 1. 首次进入，或者当前没有锁，尝试获取锁
        if self._held_lock is None:
            logger.debug(f"[{self.name}] 正在请求全局键鼠锁...")
            await blackboard.input_lock.acquire()
            self._held_lock = blackboard.input_lock
            
            # 拿到锁后，激活当前窗口并给足缓冲时间，防止串键
            blackboard.client.activate()
            await asyncio.sleep(0.05)
            logger.debug(f"[{self.name}] 已获取锁，窗口已激活。")

        # 2. 带着锁执行内部连贯逻辑
        status = await self.child.tick(blackboard)

        # 3. 只要没在 RUNNING，说明这套动作干完了（或者失败了），释放锁
        if status != NodeStatus.RUNNING:
            self._release_lock()

        return status

    @override
    def _reset(self) -> None:
        """【极度关键】如果这套连贯动作被更高层打断，必须释放锁，否则全局死锁"""
        self._release_lock()
        self.child.reset()
        
    def _release_lock(self) -> None:
        if self._held_lock is not None:
            self._held_lock.release()
            self._held_lock = None
            logger.debug(f"[{self.name}] 释放了全局键鼠锁。")