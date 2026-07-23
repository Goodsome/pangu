"""Win32 后台窗口消息注入后端实现 (PostMessage / SendMessage)。

依赖内部维护的 HWND 句柄状态进行非前台抢占式的系统消息注入。
"""

from dataclasses import dataclass
import sys
import time
from typing import Callable

from sys_input.constants import (
    VirtualKeyCode,
    WindowMessage,
)
from sys_input.exceptions import InputSimulationError, UnsupportedPlatformError
from sys_input.models import HWND, MouseButton, Point

# ---------------------------------------------------------------------------
# Win32 C types 与 API 绑定 (只在 win32 平台下实际加载)
# ---------------------------------------------------------------------------
_PostMessageW: Callable[[int, int, int, int], int] | None = None

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    _user32 = ctypes.windll.user32  # type: ignore
    _PostMessageW = _user32.PostMessageW
    _PostMessageW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    _PostMessageW.restype = wintypes.BOOL


def _make_lparam(x: int, y: int) -> int:
    """把 (x, y) 坐标打包为 Win32 32 位 LPARAM 参数。"""
    return ((y & 0xFFFF) << 16) | (x & 0xFFFF)


@dataclass
class Win32MessageBackend:
    """依赖内部 HWND 句柄状态的 Win32 消息注入实现。"""

    hwnd: HWND

    def __post_init__(self) -> None:
        if sys.platform != "win32":
            pass

    def key_down(self, vk_code: VirtualKeyCode | int) -> None:
        """向内部 HWND 窗口发送 WM_KEYDOWN 消息。"""
        if sys.platform != "win32" or _PostMessageW is None:
            raise UnsupportedPlatformError("Win32MessageBackend 仅支持 Windows 系统")

        res = bool(_PostMessageW(self.hwnd, WindowMessage.WM_KEYDOWN, int(vk_code), 1))
        if not res:
            import ctypes

            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"PostMessageW WM_KEYDOWN 失败 (HWND={self.hwnd}, VK={vk_code})",
                code=err,
            )

    def key_up(self, vk_code: VirtualKeyCode | int) -> None:
        """向内部 HWND 窗口发送 WM_KEYUP 消息。"""
        if sys.platform != "win32" or _PostMessageW is None:
            raise UnsupportedPlatformError("Win32MessageBackend 仅支持 Windows 系统")

        lparam = 0xC0000001
        res = bool(
            _PostMessageW(self.hwnd, WindowMessage.WM_KEYUP, int(vk_code), lparam)
        )
        if not res:
            import ctypes

            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"PostMessageW WM_KEYUP 失败 (HWND={self.hwnd}, VK={vk_code})", code=err
            )

    def mouse_move(self, point: Point) -> None:
        """向内部 HWND 窗口发送 WM_MOUSEMOVE 消息。"""
        if sys.platform != "win32" or _PostMessageW is None:
            raise UnsupportedPlatformError("Win32MessageBackend 仅支持 Windows 系统")

        lparam = _make_lparam(point.x, point.y)
        res = bool(_PostMessageW(self.hwnd, WindowMessage.WM_MOUSEMOVE, 0, lparam))
        if not res:
            import ctypes

            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"PostMessageW WM_MOUSEMOVE 失败 (HWND={self.hwnd}, pos=({point.x}, {point.y}))",
                code=err,
            )

    def mouse_down(
        self, point: Point | None = None, button: MouseButton = MouseButton.LEFT
    ) -> None:
        """向内部 HWND 窗口发送鼠标按键按下消息。"""
        if sys.platform != "win32" or _PostMessageW is None:
            raise UnsupportedPlatformError("Win32MessageBackend 仅支持 Windows 系统")

        lparam = _make_lparam(point.x, point.y) if point is not None else 0

        match button:
            case MouseButton.LEFT:
                msg = WindowMessage.WM_LBUTTONDOWN
                wparam = 0x0001  # MK_LBUTTON
            case MouseButton.RIGHT:
                msg = WindowMessage.WM_RBUTTONDOWN
                wparam = 0x0002  # MK_RBUTTON
            case MouseButton.MIDDLE:
                msg = WindowMessage.WM_MBUTTONDOWN
                wparam = 0x0010  # MK_MBUTTON

        res = bool(_PostMessageW(self.hwnd, msg, wparam, lparam))
        if not res:
            import ctypes

            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"PostMessageW mouse_down 失败 (HWND={self.hwnd}, button={button})",
                code=err,
            )

    def mouse_up(
        self, point: Point | None = None, button: MouseButton = MouseButton.LEFT
    ) -> None:
        """向内部 HWND 窗口发送鼠标按键抬起消息。"""
        if sys.platform != "win32" or _PostMessageW is None:
            raise UnsupportedPlatformError("Win32MessageBackend 仅支持 Windows 系统")

        lparam = _make_lparam(point.x, point.y) if point is not None else 0

        match button:
            case MouseButton.LEFT:
                msg = WindowMessage.WM_LBUTTONUP
            case MouseButton.RIGHT:
                msg = WindowMessage.WM_RBUTTONUP
            case MouseButton.MIDDLE:
                msg = WindowMessage.WM_MBUTTONUP

        res = bool(_PostMessageW(self.hwnd, msg, 0, lparam))
        if not res:
            import ctypes

            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"PostMessageW mouse_up 失败 (HWND={self.hwnd}, button={button})",
                code=err,
            )

    def mouse_click(
        self,
        point: Point | None = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval_ms: int = 0,
    ) -> None:
        """向内部 HWND 窗口发送鼠标点击消息 (支持连击和间隔)。"""
        if clicks < 1:
            raise ValueError("clicks 次数必须至少为 1")

        for i in range(clicks):
            self.mouse_down(point=point, button=button)
            self.mouse_up(point=point, button=button)
            if i < clicks - 1 and interval_ms > 0:
                time.sleep(interval_ms / 1000.0)

    def scroll(self, amount: int, point: Point | None = None) -> None:
        """向内部 HWND 窗口发送 WM_MOUSEWHEEL 滚轮消息。"""
        if sys.platform != "win32" or _PostMessageW is None:
            raise UnsupportedPlatformError("Win32MessageBackend 仅支持 Windows 系统")

        lparam = _make_lparam(point.x, point.y) if point is not None else 0
        wheel_delta = amount * 120
        wparam = (wheel_delta & 0xFFFF) << 16

        res = bool(
            _PostMessageW(self.hwnd, WindowMessage.WM_MOUSEWHEEL, wparam, lparam)
        )
        if not res:
            import ctypes

            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"PostMessageW WM_MOUSEWHEEL 失败 (HWND={self.hwnd}, amount={amount})",
                code=err,
            )
