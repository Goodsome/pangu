"""vision_stream backends 实现层子模块。

提供具体的底层图像抓取驱动实现 (Win32 PrintWindow, Win32 DXGI 等)。
"""

from vision_stream.backends.win32_dxgi import Win32DXGIBackend
from vision_stream.backends.win32_printwindow import Win32PrintWindowBackend

__all__ = [
    "Win32PrintWindowBackend",
    "Win32DXGIBackend",
]
