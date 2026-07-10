"""
通用日志配置模块
为 Pangu 系统的各个 App (CLI, MCP) 提供统一的日志配置方案
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _configure_sdk_loggers(base_handlers: list[logging.Handler], level: int):
    """
    统一接管并重定向第三方 SDK 的日志。
    你原来对 event_hub 的特殊处理，现在可以在这里统一管理。
    """
    sdk_logger = logging.getLogger("event_hub")
    sdk_logger.setLevel(level)
    sdk_logger.propagate = False

    # 避免重复添加 handler
    sdk_logger.handlers.clear()
    for handler in base_handlers:
        sdk_logger.addHandler(handler)

    # 你甚至可以在这里将那些特别吵闹的第三方库静音
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    # logging.getLogger("httpx").setLevel(logging.WARNING)


def configure_logging(
    app_name: str,
    log_dir: Path | str = "logs",
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    log_format: str | None = None,
    date_format: str | None = None,
    console_output: bool = True,
) -> None:  # 👈 注意：不再返回 Logger 实例
    """
    全局配置日志系统。只需要在 App 启动时调用一次。
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    # 1. 我们配置 Root Logger (根日志器)
    # 这样所有没有任何配置的子 Logger 都会自动继承这里的 Handler
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 如果已经配置过，避免重复添加导致打印两次
    if root_logger.handlers:
        root_logger.handlers.clear()

    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 2. 配置文件输出，文件名自动加上应用名 (如 cli.log, mcp.log)
    log_file = log_dir_path / f"{app_name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 3. 配置控制台输出
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 4. 接管第三方 SDK
    # _configure_sdk_loggers(root_logger.handlers, log_level)
