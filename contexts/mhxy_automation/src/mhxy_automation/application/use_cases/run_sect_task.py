"""应用层用例：运行师门任务自动化。"""

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path

from foundation.logging_setup import client_file_logging, set_current_client_index
from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import BaseNode
from mhxy_automation.domain.behavior_tree.tasks.sect_task_tree import (
    build_sect_task_tree,
)
from mhxy_automation.domain.enums.node_status import NodeStatus
from mhxy_client.factory import create_mhxy_client_by_index
from sys_input import VirtualKeyCode, is_key_pressed

logger = logging.getLogger(__name__)

# 持续循环模式下每帧之间的间隔时间
_TICK_INTERVAL_SEC: float = 0.2


@dataclass
class RunSectTask:
    """运行师门任务自动化用例。

    支持两种执行模式：

    one_tick=True  : 执行单帧，输出本帧状态后退出（调试用）。
    one_tick=False : 持续循环驱动行为树，直到任务完成或按 F12 触发退出。
    """

    input_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    stop_event: asyncio.Event = field(default_factory=asyncio.Event)

    async def execute(
        self,
        window_index: int = 0,
    ) -> None:
        set_current_client_index(window_index)
        client = create_mhxy_client_by_index(window_index)

        async with client:
            blackboard = Blackboard(client=client, input_lock=self.input_lock)
            tree = build_sect_task_tree()

            try:
                while not self.stop_event.is_set():
                    if is_key_pressed(VirtualKeyCode.VK_F12):
                        logger.info("[RunSectTask] 检测到 F12 按键，主动退出任务")
                        self.stop_event.set()
                        break

                    async with self.input_lock:
                        client.activate()
                        await client.begin_frame()
                        await tree.tick(blackboard)
                        await asyncio.sleep(0.1)

                    await self.sleep()

            except asyncio.CancelledError:
                logger.info("[RunSectTask] 任务被取消")
                
    async def execute_v2(
        self,
        window_index: int = 0,
    ) -> None:
        set_current_client_index(window_index)
        client = create_mhxy_client_by_index(window_index)

        async with client:
            blackboard = Blackboard(client=client, input_lock=self.input_lock)
            tree = build_sect_task_tree()

            try:
                while not self.stop_event.is_set():
                    if is_key_pressed(VirtualKeyCode.VK_F12):
                        logger.info("[RunSectTask] 检测到 F12 按键，主动退出任务")
                        self.stop_event.set()
                        break

                    await client.begin_frame()
                    await blackboard.acquire_input_lock()
                    
                    status = await tree.tick(blackboard)
                    
                    # if status != NodeStatus.RUNNING:
                        # await blackboard.release_input_lock()
                    
                    await self.sleep()

            except asyncio.CancelledError:
                logger.info("[RunSectTask] 任务被取消")

    async def sleep(self) -> None:
        sleep_remaining = _TICK_INTERVAL_SEC
        step_interval = 0.05
        while sleep_remaining > 0 and not self.stop_event.is_set():
            if is_key_pressed(VirtualKeyCode.VK_F12):
                logger.info("[RunSectTask] 检测到 F12 按键，主动退出任务")
                self.stop_event.set()
                break
            await asyncio.sleep(step_interval)
            sleep_remaining -= step_interval

    async def execute_batch(
        self,
        window_indices: list[int],
        one_tick: bool = False,
        log_dir: Path | str = "logs",
    ) -> None:
        """批量运行多个窗口的师门任务，并将每个 client 的日志分别写入各自的 log 文件中。"""
        self.stop_event.clear()
        with client_file_logging(window_indices, log_dir=log_dir):
            logger.info(
                "[RunSectTask] 开始批量执行窗口任务: %s，日志目录: %s",
                window_indices,
                log_dir,
            )
            if not one_tick:
                logger.info("[RunSectTask] 提示：随时按 F12 可主动停止任务")
            try:
                # 使用 Python 3.11+ 推荐的 TaskGroup 管理并发
                async with asyncio.TaskGroup() as tg:
                    for index in window_indices:
                        # 为每个窗口创建一个独立的并发任务
                        _ = tg.create_task(
                            self.execute_v2(window_index=index),
                            name=f"WindowTask-{index}",
                        )
                logger.info("[RunSectTask] 所有窗口任务已安全结束。")
            except Exception:
                # TaskGroup 会收集所有抛出的异常，可以使用 except* 语法处理 ExceptionGroup
                logger.exception("[RunSectTask] 批量执行中发生异常")

    async def _run_one_tick(self, tree: BaseNode, blackboard: Blackboard) -> None:
        blackboard.client.activate()
        await blackboard.client.begin_frame()
        await tree.tick(blackboard)
        await asyncio.sleep(_TICK_INTERVAL_SEC)
