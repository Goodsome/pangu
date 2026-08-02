# pyright: reportAny=false, reportIncompatibleVariableOverride=false, reportUnannotatedClassAttribute=false
"""Win32 前台物理外设模拟后端实现 (SendInput)。

不依赖 HWND 句柄，直接在系统全局底层模拟硬件按键和鼠标输入。
"""

import asyncio
from dataclasses import dataclass
import sys
from typing import Callable, final

from sys_input.constants import (
    INPUT_KEYBOARD,
    INPUT_MOUSE,
    KEYEVENTF_KEYUP,
    MOUSEEVENTF_ABSOLUTE,
    MOUSEEVENTF_LEFTDOWN,
    MOUSEEVENTF_LEFTUP,
    MOUSEEVENTF_MIDDLEDOWN,
    MOUSEEVENTF_MIDDLEUP,
    MOUSEEVENTF_MOVE,
    MOUSEEVENTF_RIGHTDOWN,
    MOUSEEVENTF_RIGHTUP,
    MOUSEEVENTF_WHEEL,
    VirtualKeyCode,
)
from sys_input.exceptions import InputSimulationError, UnsupportedPlatformError
from sys_input.models import MouseButton, Point

# ---------------------------------------------------------------------------
# Win32 C types / Structures / API 绑定 (只在 win32 平台下定义)
# ---------------------------------------------------------------------------
_SendInput: Callable[..., int] | None = None
_SetCursorPos: Callable[[int, int], int] | None = None

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    @final
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    @final
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    @final
    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        ]

    @final
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]

    @final
    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("union", _INPUT_UNION),
        ]

    _user32 = ctypes.windll.user32  # type: ignore

    _SendInput = _user32.SendInput
    _SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    _SendInput.restype = wintypes.UINT

    _SetCursorPos = _user32.SetCursorPos
    _SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
    _SetCursorPos.restype = wintypes.BOOL


@dataclass
class Win32HardwareBackend:
    """不依赖 HWND 的 Win32 硬件级 SendInput 模拟实现。"""

    def __post_init__(self) -> None:
        if sys.platform != "win32":
            pass

    async def key_down(self, vk_code: VirtualKeyCode | int) -> None:
        """全局模拟物理按键按下。"""
        if sys.platform != "win32" or _SendInput is None:
            raise UnsupportedPlatformError("Win32HardwareBackend 仅支持 Windows 系统")

        import ctypes

        inp = INPUT()  # type: ignore
        inp.type = INPUT_KEYBOARD  # type: ignore
        inp.union.ki.wVk = int(vk_code)  # type: ignore
        inp.union.ki.dwFlags = 0  # type: ignore

        res = int(_SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)))
        if res == 0:
            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"SendInput key_down 失败 (VK={vk_code})", code=err
            )

    async def key_up(self, vk_code: VirtualKeyCode | int) -> None:
        """全局模拟物理按键抬起。"""
        if sys.platform != "win32" or _SendInput is None:
            raise UnsupportedPlatformError("Win32HardwareBackend 仅支持 Windows 系统")

        import ctypes

        inp = INPUT()  # type: ignore
        inp.type = INPUT_KEYBOARD  # type: ignore
        inp.union.ki.wVk = int(vk_code)  # type: ignore
        inp.union.ki.dwFlags = KEYEVENTF_KEYUP  # type: ignore

        res = int(_SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)))
        if res == 0:
            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"SendInput key_up 失败 (VK={vk_code})", code=err
            )

    async def mouse_move(self, point: Point) -> None:
        """全局移动鼠标光标位置。"""
        if (
            sys.platform != "win32"
            or _SetCursorPos is None
            or _SendInput is None
        ):
            raise UnsupportedPlatformError("Win32HardwareBackend 仅支持 Windows 系统")

        res = bool(_SetCursorPos(point.x, point.y))
        if not res:
            # 当 SetCursorPos 被 Win32 UIPI 限制拦截时，回退至基于 SendInput MOUSEEVENTF_ABSOLUTE 模式合成物理光标移动
            import ctypes

            user32 = ctypes.windll.user32
            sw = int(user32.GetSystemMetrics(0)) or 1920
            sh = int(user32.GetSystemMetrics(1)) or 1080
            dx = int((point.x * 65535) / sw)
            dy = int((point.y * 65535) / sh)

            inp = INPUT()  # type: ignore
            inp.type = INPUT_MOUSE  # type: ignore
            inp.union.mi.dx = dx  # type: ignore
            inp.union.mi.dy = dy  # type: ignore
            inp.union.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE  # type: ignore

            send_res = int(_SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)))
            if send_res == 0:
                err = ctypes.GetLastError()
                raise InputSimulationError(
                    f"SetCursorPos 与 SendInput mouse_move 均失败 pos=({point.x}, {point.y})",
                    code=err,
                )

    async def mouse_down(
        self, point: Point | None = None, button: MouseButton = MouseButton.LEFT
    ) -> None:
        """全局模拟鼠标按键按下。"""
        if sys.platform != "win32" or _SendInput is None:
            raise UnsupportedPlatformError("Win32HardwareBackend 仅支持 Windows 系统")

        if point is not None:
            await self.mouse_move(point)

        match button:
            case MouseButton.LEFT:
                flag = MOUSEEVENTF_LEFTDOWN
            case MouseButton.RIGHT:
                flag = MOUSEEVENTF_RIGHTDOWN
            case MouseButton.MIDDLE:
                flag = MOUSEEVENTF_MIDDLEDOWN

        import ctypes

        inp = INPUT()  # type: ignore
        inp.type = INPUT_MOUSE  # type: ignore
        inp.union.mi.dwFlags = flag  # type: ignore

        res = int(_SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)))
        if res == 0:
            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"SendInput mouse_down 失败 (button={button})", code=err
            )

    async def mouse_up(
        self, point: Point | None = None, button: MouseButton = MouseButton.LEFT
    ) -> None:
        """全局模拟鼠标按键抬起。"""
        if sys.platform != "win32" or _SendInput is None:
            raise UnsupportedPlatformError("Win32HardwareBackend 仅支持 Windows 系统")

        if point is not None:
            await self.mouse_move(point)

        match button:
            case MouseButton.LEFT:
                flag = MOUSEEVENTF_LEFTUP
            case MouseButton.RIGHT:
                flag = MOUSEEVENTF_RIGHTUP
            case MouseButton.MIDDLE:
                flag = MOUSEEVENTF_MIDDLEUP

        import ctypes

        inp = INPUT()  # type: ignore
        inp.type = INPUT_MOUSE  # type: ignore
        inp.union.mi.dwFlags = flag  # type: ignore

        res = int(_SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)))
        if res == 0:
            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"SendInput mouse_up 失败 (button={button})", code=err
            )

    async def mouse_click(
        self,
        point: Point | None = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval_ms: int = 0,
    ) -> None:
        """全局模拟鼠标点击 (支持连击与间隔)。"""
        if clicks < 1:
            raise ValueError("clicks 次数必须至少为 1")

        for i in range(clicks):
            await self.mouse_down(point=point, button=button)
            await self.mouse_up(point=point, button=button)
            if i < clicks - 1 and interval_ms > 0:
                await asyncio.sleep(interval_ms / 1000.0)

    async def scroll(self, amount: int, point: Point | None = None) -> None:
        """全局模拟滚轮滚动。"""
        if sys.platform != "win32" or _SendInput is None:
            raise UnsupportedPlatformError("Win32HardwareBackend 仅支持 Windows 系统")

        if point is not None:
            await self.mouse_move(point)

        import ctypes

        inp = INPUT()  # type: ignore
        inp.type = INPUT_MOUSE  # type: ignore
        inp.union.mi.dwFlags = MOUSEEVENTF_WHEEL  # type: ignore
        inp.union.mi.mouseData = amount  # type: ignore

        res = int(_SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)))
        if res == 0:
            err = ctypes.GetLastError()
            raise InputSimulationError(
                f"SendInput scroll 失败 (amount={amount})", code=err
            )
