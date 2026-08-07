"""应用层用例：运行师门任务自动化。"""

import asyncio
import logging
from dataclasses import dataclass, field

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree import (
    build_sect_task_tree,
)
from mhxy_client.factory import create_mhxy_client_by_index

logger = logging.getLogger(__name__)

# 持续循环模式下每帧之间的间隔时间
_TICK_INTERVAL_SEC: float = 1


@dataclass
class RunSectTask:
    """运行师门任务自动化用例。

    支持两种执行模式：

    one_tick=True  : 执行单帧，输出本帧状态后退出（调试用）。
    one_tick=False : 持续循环驱动行为树，直到任务完成或被中断。
    """
    input_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    
    async def execute(
        self,
        window_index: int = 0,
        one_tick: bool = False,
    ) -> None:
        client = create_mhxy_client_by_index(window_index)

        async with client:
            client.activate()
            blackboard = Blackboard(client=client)
            tree = build_sect_task_tree()

            if one_tick:
                await client.begin_frame()
                status = await tree.tick(blackboard)
                logger.info("[RunSectTask] 单帧执行完毕，状态: %s", status)
                return

            try:
                while True:
                    async with self.input_lock:
                        # client.activate()
                        await client.begin_frame()
                        status = await tree.tick(blackboard)
                        
                    await asyncio.sleep(_TICK_INTERVAL_SEC)
            except asyncio.CancelledError:
                logger.info("[RunSectTask] 任务被取消")

    async def execute_batch(
        self, 
        window_indices: list[int], 
        one_tick: bool = False
    ) -> None:
        """批量运行多个窗口的师门任务。"""
        
        # 使用 Python 3.11+ 推荐的 TaskGroup 管理并发
        try:
            async with asyncio.TaskGroup() as tg:
                for index in window_indices:
                    # 为每个窗口创建一个独立的并发任务
                    tg.create_task(
                        self.execute(window_index=index, one_tick=one_tick),
                        name=f"WindowTask-{index}"
                    )
            logger.info("[RunSectTask] 所有窗口任务已安全结束。")
        except* Exception as e:
            # TaskGroup 会收集所有抛出的异常，可以使用 except* 语法处理 ExceptionGroup
            logger.error("[RunSectTask] 批量执行中发生异常: %s", e)