"""系统输入库异常定义层。

预定义强类型异常，为 Rust FFI 映射及底层系统错误捕捉做准备。
"""

from typing import override


class SysInputError(Exception):
    """sys_input 库基础异常类型。"""

    message: str
    code: int | None

    def __init__(self, message: str, code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    @override
    def __str__(self) -> str:
        if self.code is not None:
            return f"[{self.code}] {self.message}"
        return self.message


class BackendError(SysInputError):
    """后端驱动/系统 API 调用异常。"""


class WindowNotFoundError(BackendError):
    """目标窗口/句柄未找到异常。"""


class InputSimulationError(BackendError):
    """输入模拟失败异常。"""


class UnsupportedPlatformError(SysInputError):
    """当前操作系统平台不受支持异常。"""
