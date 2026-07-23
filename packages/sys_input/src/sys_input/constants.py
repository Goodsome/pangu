"""系统输入库常量层。

存放 Windows 虚拟键码 (VirtualKeyCode)、消息宏 (WindowMessage) 和 SendInput 模拟标志等常量。
"""

from enum import IntEnum
from typing import Final


class WindowMessage(IntEnum):
    """Windows 消息宏 (WM_*)。"""

    WM_NULL = 0x0000
    WM_CREATE = 0x0001
    WM_DESTROY = 0x0002
    WM_MOVE = 0x0003
    WM_SIZE = 0x0005
    WM_ACTIVATE = 0x0006
    WM_SETFOCUS = 0x0007
    WM_KILLFOCUS = 0x0008

    # 键盘消息
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    WM_CHAR = 0x0102
    WM_SYSKEYDOWN = 0x0104
    WM_SYSKEYUP = 0x0105

    # 鼠标消息
    WM_MOUSEMOVE = 0x0200
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_LBUTTONDBLCLK = 0x0203
    WM_RBUTTONDOWN = 0x0204
    WM_RBUTTONUP = 0x0205
    WM_RBUTTONDBLCLK = 0x0206
    WM_MBUTTONDOWN = 0x0207
    WM_MBUTTONUP = 0x0208
    WM_MBUTTONDBLCLK = 0x0209
    WM_MOUSEWHEEL = 0x020A


class VirtualKeyCode(IntEnum):
    """Windows 虚拟键码 (VK_*) 枚举。"""

    VK_LBUTTON = 0x01
    VK_RBUTTON = 0x02
    VK_CANCEL = 0x03
    VK_MBUTTON = 0x04

    VK_BACK = 0x08
    VK_TAB = 0x09
    VK_CLEAR = 0x0C
    VK_RETURN = 0x0D
    VK_SHIFT = 0x10
    VK_CONTROL = 0x11
    VK_MENU = 0x12  # ALT
    VK_PAUSE = 0x13
    VK_CAPITAL = 0x14  # CAPS LOCK
    VK_ESCAPE = 0x1B
    VK_SPACE = 0x20
    VK_PRIOR = 0x21  # PAGE UP
    VK_NEXT = 0x22  # PAGE DOWN
    VK_END = 0x23
    VK_HOME = 0x24
    VK_LEFT = 0x25
    VK_UP = 0x26
    VK_RIGHT = 0x27
    VK_DOWN = 0x28

    VK_SELECT = 0x29
    VK_PRINT = 0x2A
    VK_EXECUTE = 0x2B
    VK_SNAPSHOT = 0x2C  # PRINT SCREEN
    VK_INSERT = 0x2D
    VK_DELETE = 0x2E
    VK_HELP = 0x2F

    # 数字 0-9
    VK_0 = 0x30
    VK_1 = 0x31
    VK_2 = 0x32
    VK_3 = 0x33
    VK_4 = 0x34
    VK_5 = 0x35
    VK_6 = 0x36
    VK_7 = 0x37
    VK_8 = 0x38
    VK_9 = 0x39

    # 字母 A-Z
    VK_A = 0x41
    VK_B = 0x42
    VK_C = 0x43
    VK_D = 0x44
    VK_E = 0x45
    VK_F = 0x46
    VK_G = 0x47
    VK_H = 0x48
    VK_I = 0x49
    VK_J = 0x4A
    VK_K = 0x4B
    VK_L = 0x4C
    VK_M = 0x4D
    VK_N = 0x4E
    VK_O = 0x4F
    VK_P = 0x50
    VK_Q = 0x51
    VK_R = 0x52
    VK_S = 0x53
    VK_T = 0x54
    VK_U = 0x55
    VK_V = 0x56
    VK_W = 0x57
    VK_X = 0x58
    VK_Y = 0x59
    VK_Z = 0x5A

    # 功能键 F1-F12
    VK_F1 = 0x70
    VK_F2 = 0x71
    VK_F3 = 0x72
    VK_F4 = 0x73
    VK_F5 = 0x74
    VK_F6 = 0x75
    VK_F7 = 0x76
    VK_F8 = 0x77
    VK_F9 = 0x78
    VK_F10 = 0x79
    VK_F11 = 0x7A
    VK_F12 = 0x7B


# ---------------------------------------------------------------------------
# SendInput 与 Win32 事件标志常量
# ---------------------------------------------------------------------------
INPUT_MOUSE: Final[int] = 0
INPUT_KEYBOARD: Final[int] = 1
INPUT_HARDWARE: Final[int] = 2

KEYEVENTF_EXTENDEDKEY: Final[int] = 0x0001
KEYEVENTF_KEYUP: Final[int] = 0x0002
KEYEVENTF_UNICODE: Final[int] = 0x0004
KEYEVENTF_SCANCODE: Final[int] = 0x0008

MOUSEEVENTF_MOVE: Final[int] = 0x0001
MOUSEEVENTF_LEFTDOWN: Final[int] = 0x0002
MOUSEEVENTF_LEFTUP: Final[int] = 0x0004
MOUSEEVENTF_RIGHTDOWN: Final[int] = 0x0008
MOUSEEVENTF_RIGHTUP: Final[int] = 0x00010
MOUSEEVENTF_MIDDLEDOWN: Final[int] = 0x0020
MOUSEEVENTF_MIDDLEUP: Final[int] = 0x0040
MOUSEEVENTF_WHEEL: Final[int] = 0x0800
MOUSEEVENTF_ABSOLUTE: Final[int] = 0x8000


# ---------------------------------------------------------------------------
# 常用宏快捷常量引用 (支持 direct import)
# ---------------------------------------------------------------------------
WM_KEYDOWN: Final = WindowMessage.WM_KEYDOWN
WM_KEYUP: Final = WindowMessage.WM_KEYUP
WM_CHAR: Final = WindowMessage.WM_CHAR
WM_MOUSEMOVE: Final = WindowMessage.WM_MOUSEMOVE
WM_LBUTTONDOWN: Final = WindowMessage.WM_LBUTTONDOWN
WM_LBUTTONUP: Final = WindowMessage.WM_LBUTTONUP

VK_LBUTTON: Final = VirtualKeyCode.VK_LBUTTON
VK_RETURN: Final = VirtualKeyCode.VK_RETURN
VK_SHIFT: Final = VirtualKeyCode.VK_SHIFT
VK_CONTROL: Final = VirtualKeyCode.VK_CONTROL
VK_ESCAPE: Final = VirtualKeyCode.VK_ESCAPE
VK_SPACE: Final = VirtualKeyCode.VK_SPACE
