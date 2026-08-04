"""Interface CLI: 榜单截图注入命令。"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Annotated

import typer

from d4_injestion.container import Container

logger = logging.getLogger(__name__)

_DEFAULT_BASE_DIR = Path("output/screenshots")


async def _async_main(base_dir: Path) -> None:
    container = Container()
    use_case = container.injest_use_case()
    try:
        result = await use_case.execute(base_dir)
        logger.info(
            "注入完成: total=%d succeeded=%d failed=%d",
            result.total,
            result.succeeded,
            result.failed,
        )
    except Exception as e:
        logger.exception("注入流程发生异常: %s", e)
    finally:
        await use_case.aclose()


def injest_leaderboard(
    base_dir: Annotated[
        Path,
        typer.Option("--dir", "-d", help="截图根目录 (如 output/screenshots)"),
    ] = _DEFAULT_BASE_DIR,
) -> None:
    """OCR 识别 output/screenshots 下榜单截图并注入 d4_leaderboard。"""
    asyncio.run(_async_main(base_dir))
