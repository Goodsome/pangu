"""视觉流异常定义层。

预定义强类型异常，为 Rust FFI 映射及底层 C++ / DirectX / Win32 系统异常桥接做准备。
"""

from typing import override


class VisionStreamError(Exception):
    """vision_stream 库基础异常类型。"""

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


class BackendError(VisionStreamError):
    """后端驱动/系统 API 抓取底层异常。"""


class WindowNotFoundError(BackendError):
    """目标窗口句柄 (HWND) 未找到或已失效异常。"""


class CaptureFailedError(BackendError):
    """图像帧抓取失败异常。"""


class DXGIError(BackendError):
    """DirectX / DXGI Output Duplication 驱动异常。"""


class UnsupportedPlatformError(VisionStreamError):
    """当前操作系统平台不受支持异常。"""
