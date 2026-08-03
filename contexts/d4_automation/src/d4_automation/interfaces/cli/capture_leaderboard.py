"""Interface CLI: 天梯榜数据采集命令。"""

import asyncio
from typing import Annotated

import typer

from d4_automation.application.use_cases.capture_leaderboard import CaptureLeaderboard


async def _async_main(window_index: int) -> None:
    use_case = CaptureLeaderboard()
    cancel_event = asyncio.Event()

    try:
        await use_case.execute(
            window_index=window_index,
            cancel_event=cancel_event,
        )
    except KeyboardInterrupt:
        cancel_event.set()


def capture_leaderboard(
    window_index: Annotated[
        int, typer.Option("--idx", "-i", help="游戏窗口索引（从 0 开始）")
    ] = 0,
) -> None:
    """采集天梯榜截图：按配置逐页截取榜单及玩家装备/技能/巅峰/护身符 tooltip。"""
    asyncio.run(_async_main(window_index))
