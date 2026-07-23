"""系统输入契约层。

定义统一的输入后端 Protocol 接口契约。
"""

from typing import Protocol, runtime_checkable

from sys_input.constants import VirtualKeyCode
from sys_input.models import MouseButton, Point


@runtime_checkable
class InputBackend(Protocol):
    """统一系统输入后端接口契约。

    解耦底层具体实现（无论是基于 HWND 的后台消息注入还是前台物理 SendInput 模拟）。
    """

    def key_down(self, vk_code: VirtualKeyCode | int) -> None:
        """模拟/发送按键按下。"""
        ...

    def key_up(self, vk_code: VirtualKeyCode | int) -> None:
        """模拟/发送按键抬起。"""
        ...

    def mouse_move(self, point: Point) -> None:
        """模拟/发送鼠标光标移动。"""
        ...

    def mouse_down(
        self, point: Point | None = None, button: MouseButton = MouseButton.LEFT
    ) -> None:
        """模拟/发送鼠标按键按下。"""
        ...

    def mouse_up(
        self, point: Point | None = None, button: MouseButton = MouseButton.LEFT
    ) -> None:
        """模拟/发送鼠标按键抬起。"""
        ...

    def mouse_click(
        self,
        point: Point | None = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval_ms: int = 0,
    ) -> None:
        """模拟/发送鼠标点击（支持连击和时间间隔）。"""
        ...

    def scroll(self, amount: int, point: Point | None = None) -> None:
        """模拟/发送鼠标滚轮滚动（amount 正数为向上，负数为向下）。"""
        ...
