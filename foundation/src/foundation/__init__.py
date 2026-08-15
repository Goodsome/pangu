"""foundation 基础通用工具包。"""

from foundation.logging_setup import (
    ClientLogFilter,
    client_file_logging,
    configure_logging,
    current_client_index,
    set_current_client_index,
)

__all__ = [
    "ClientLogFilter",
    "client_file_logging",
    "configure_logging",
    "current_client_index",
    "set_current_client_index",
]
