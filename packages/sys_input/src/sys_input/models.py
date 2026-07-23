"""系统输入数据层。

定义纯数据结构 (Dataclass) 和类型别名 (TypeAlias)。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias

from sys_input.constants import VirtualKeyCode

# ---------------------------------------------------------------------------
# 类型别名 (TypeAlias)
# ---------------------------------------------------------------------------
HWND: TypeAlias = int
ScanCode: TypeAlias = int


# ---------------------------------------------------------------------------
# 枚举定义
# ---------------------------------------------------------------------------
class MouseButton(str, Enum):
    """鼠标按键枚举。"""

    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class KeyState(str, Enum):
    """按键状态枚举。"""

    DOWN = "down"
    UP = "up"


# ---------------------------------------------------------------------------
# 数据结构 (纯标准库 Dataclass)
# ---------------------------------------------------------------------------
@dataclass
class Point:
    """二维坐标点。"""

    x: int = 0
    y: int = 0


@dataclass
class MouseEvent:
    """鼠标事件模型。"""

    button: MouseButton
    state: KeyState
    position: Point = field(default_factory=Point)


@dataclass
class KeyEvent:
    """键盘事件模型。"""

    vk_code: VirtualKeyCode | int
    state: KeyState
    scan_code: ScanCode = 0
