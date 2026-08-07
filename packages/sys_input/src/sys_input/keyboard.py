# pyright: reportAny=false
"""系统外设键盘状态查询。"""

import sys

from sys_input.constants import VirtualKeyCode


def is_key_pressed(vk_code: VirtualKeyCode | int) -> bool:
    """检查系统底层指定的虚拟按键当前是否被按下 (Win32 API GetAsyncKeyState)。

    Args:
        vk_code: 虚拟按键码，如 VirtualKeyCode.VK_F12 或 0x7B。

    Returns:
        bool: 如果当前按键处于按下状态返回 True，否则返回 False。
    """
    if sys.platform != "win32":
        return False
    import ctypes

    vk = int(vk_code)
    return bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)
