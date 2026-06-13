"""通用日志配置模块 为应用程序各个组件提供统一的日志配置方案"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def add_sdk_logger(logger: logging.Logger):
    sdk_logger = logging.getLogger("event_hub")
    for handler in logger.handlers:
        sdk_logger.addHandler(handler)
    sdk_logger.setLevel(logging.INFO)
    sdk_logger.propagate = False
    return logger


def setup_logging(
    logger_name: str = "task_graph",
    log_file: str = "app.log",
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    log_format: str | None = None,
    date_format: str | None = None,
    console_output: bool = True,
) -> logging.Logger:
    """
    配置日志系统

    Args:
        logger_name: 日志记录器名称
        log_file: 日志文件名，存放在项目根目录的logs目录下
        log_level: 日志级别，默认INFO
        max_bytes: 单个日志文件最大大小，默认10MB
        backup_count: 保留的日志文件备份数量，默认5个
        log_format: 自定义日志格式，默认包含时间、日志名、级别和消息
        date_format: 自定义时间格式，默认"%Y-%m-%d %H:%M:%S"
        console_output: 是否同时输出到控制台，默认True

    Returns:
        配置好的Logger实例
    """
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.propagate = False
    if logger.handlers:
        return logger
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    logger = add_sdk_logger(logger)
    return logger


def setup_mcp_logging() -> logging.Logger:
    """为MCP服务配置日志"""
    return setup_logging(logger_name="codegen", log_file="mcp.log")


def setup_cli_logging() -> logging.Logger:
    """为CLI服务配置日志"""
    logger = setup_logging(
        logger_name="codegen", log_file="cli.log", console_output=True
    )
    return logger
