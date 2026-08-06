"""Decepticons CLI 入口。

用法示例：
    # 单帧执行（调试用）
    uv run decepticons run-task --one-tick

    # 持续循环执行
    uv run decepticons run-task

    # 指定窗口索引
    uv run decepticons run-task --idx 1 --one-tick
"""

import asyncio
import logging
from pathlib import Path
from typing import Annotated

import typer
from foundation.logging_setup import configure_logging
from mhxy_automation.application.use_cases.run_sect_task import RunSectTask

configure_logging(
    app_name="decepticons",
    log_dir=Path.cwd() / "logs",
    log_level=logging.INFO,
    console_output=True,
)

app = typer.Typer(
    name="decepticons",
    help="Decepticons — 梦幻西游自动化机器人",
    add_completion=False,
)


@app.command("run-task")
def run_task(
    window_index: Annotated[
        int,
        typer.Option("--idx", "-i", help="游戏窗口索引（从 0 开始）"),
    ] = 0,
    one_tick: Annotated[
        bool,
        typer.Option("--one-tick", help="仅执行单帧 tick 后退出（调试模式）"),
    ] = False,
) -> None:
    """执行师门任务自动化。

    默认为持续循环模式；添加 --one-tick 则仅执行一帧后退出。
    """
    use_case = RunSectTask()
    asyncio.run(use_case.execute(window_index=window_index, one_tick=one_tick))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
