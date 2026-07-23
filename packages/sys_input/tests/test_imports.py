import dataclasses
import sys
import pytest

from sys_input import (
    InputBackend,
    KeyEvent,
    KeyState,
    Point,
    VirtualKeyCode,
    Win32HardwareBackend,
    Win32MessageBackend,
)
from sys_input.exceptions import UnsupportedPlatformError


def test_dataclass_models() -> None:
    assert dataclasses.is_dataclass(Point)
    assert dataclasses.is_dataclass(KeyEvent)
    assert dataclasses.is_dataclass(Win32MessageBackend)
    assert dataclasses.is_dataclass(Win32HardwareBackend)

    p = Point(x=100, y=200)
    assert p.x == 100
    assert p.y == 200

    ke = KeyEvent(vk_code=VirtualKeyCode.VK_RETURN, state=KeyState.DOWN)
    assert ke.vk_code == 0x0D
    assert isinstance(ke.vk_code, int)


def test_virtual_key_code_int_enum() -> None:
    assert VirtualKeyCode.VK_A == 0x41
    assert isinstance(VirtualKeyCode.VK_A, int)


def test_unified_protocol_duck_typing() -> None:
    msg_backend = Win32MessageBackend(hwnd=123456)
    hw_backend = Win32HardwareBackend()

    assert isinstance(msg_backend, InputBackend)
    assert isinstance(hw_backend, InputBackend)

    assert msg_backend.hwnd == 123456


@pytest.mark.anyio
async def test_non_windows_platform_behavior_async() -> None:
    msg_backend = Win32MessageBackend(hwnd=123456)
    hw_backend = Win32HardwareBackend()

    if sys.platform != "win32":
        with pytest.raises(UnsupportedPlatformError):
            await msg_backend.key_down(VirtualKeyCode.VK_A)

        with pytest.raises(UnsupportedPlatformError):
            await hw_backend.mouse_move(Point(x=10, y=20))

        with pytest.raises(UnsupportedPlatformError):
            await msg_backend.mouse_down(Point(x=10, y=20))

        with pytest.raises(UnsupportedPlatformError):
            await hw_backend.scroll(1)
