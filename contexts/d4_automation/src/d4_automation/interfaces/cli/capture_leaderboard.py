"""Interface CLI: 天梯榜数据采集命令。"""

import asyncio
import signal
from pathlib import Path
from typing import Annotated

import typer

from d4_automation.application.use_cases.capture_leaderboard import CaptureLeaderboard


async def _async_main(window_index: int, config: Path | None) -> None:
    use_case = CaptureLeaderboard()
    cancel_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, cancel_event.set)

    await use_case.execute(
        window_index=window_index,
        cancel_event=cancel_event,
        config_path=config,
    )


def capture_leaderboard(
    window_index: Annotated[
        int, typer.Option("--idx", "-i", help="游戏窗口索引（从 0 开始）")
    ] = 0,
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            "-c",
            help="自定义 capture_task.yaml 路径，默认使用内置配置",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ] = None,
) -> None:
    """采集天梯榜截图：按配置逐页截取榜单及玩家装备/技能/巅峰/护身符 tooltip。"""
    asyncio.run(_async_main(window_index, config))
