"""Interface CLI: helltides 榜单抓取注入命令。"""

from __future__ import annotations

import asyncio
import logging

from d4_injestion.container import Container

logger = logging.getLogger(__name__)


async def _async_main() -> None:
    container = Container()
    use_case = container.injest_helltides_use_case()
    try:
        result = await use_case.execute()
        logger.info(
            "注入完成: total=%d succeeded=%d failed=%d degraded=%d",
            result.total,
            result.succeeded,
            result.failed,
            result.degraded,
        )
    except Exception as e:
        logger.exception("注入流程发生异常: %s", e)
    finally:
        await use_case.aclose()


def injest_helltides() -> None:
    """从 helltides.com 抓取 D4 Tower 榜单并注入 d4_leaderboard。"""
    asyncio.run(_async_main())
