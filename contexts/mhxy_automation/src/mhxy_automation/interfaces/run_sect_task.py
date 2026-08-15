import asyncio
import logging
from typing import Annotated

from mhxy_automation.application.use_cases.run_sect_task import RunSectTask
import typer

logger = logging.getLogger(__name__)


def run_sect_task(
    window_index: Annotated[
        int,
        typer.Option("--idx", "-i", help="游戏窗口索引（从 0 开始）"),
    ] = 0,
    one_tick: Annotated[
        bool,
        typer.Option("--one-tick", help="仅执行单帧 tick 后退出（调试模式）"),
    ] = False,
    batch: Annotated[
        int,
        typer.Option("--batch", help="批量执行模式（不循环）"),
    ] = 0,
) -> None:
    """执行师门任务自动化。

    默认为持续循环模式；添加 --one-tick 则仅执行一帧后退出。
    """
    use_case = RunSectTask()
    if batch > 0:
        asyncio.run(use_case.execute_batch(window_indices=list(range(batch))))
    else:
        asyncio.run(use_case.execute(window_index=window_index))
