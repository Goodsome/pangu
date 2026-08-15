"""Decepticons CLI 入口。

用法示例：
    # 单帧执行（调试用）
    uv run decepticons run-task --one-tick

    # 持续循环执行
    uv run decepticons run-task

    # 指定窗口索引
    uv run decepticons run-task --idx 1 --one-tick
"""

import logging
from pathlib import Path

from mhxy_automation.interfaces.run_sect_task import run_sect_task
import typer
from foundation.logging_setup import configure_logging

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
    pretty_exceptions_enable=False,
)
app.command("run-task")(run_sect_task)


def main() -> None:
    logger = logging.getLogger(__name__)
    try:
        app()
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
