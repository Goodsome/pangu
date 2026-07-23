"""sys_input 门面层。

统一暴露对外 API、数据模型、异常以及契约接口。
"""

from sys_input.backends import Win32HardwareBackend, Win32MessageBackend
from sys_input.constants import VirtualKeyCode, WindowMessage
from sys_input.exceptions import (
    BackendError,
    InputSimulationError,
    SysInputError,
    UnsupportedPlatformError,
    WindowNotFoundError,
)
from sys_input.interfaces import InputBackend
from sys_input.models import (
    HWND,
    KeyEvent,
    KeyState,
    MouseButton,
    MouseEvent,
    Point,
    ScanCode,
)

__all__ = [
    # 统一接口契约
    "InputBackend",
    # 数据模型与类型
    "Point",
    "MouseEvent",
    "KeyEvent",
    "MouseButton",
    "KeyState",
    "HWND",
    "VirtualKeyCode",
    "WindowMessage",
    "ScanCode",
    # 异常
    "SysInputError",
    "BackendError",
    "WindowNotFoundError",
    "InputSimulationError",
    "UnsupportedPlatformError",
    # 实现层
    "Win32MessageBackend",
    "Win32HardwareBackend",
]
