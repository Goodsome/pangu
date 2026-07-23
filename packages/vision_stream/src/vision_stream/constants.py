"""视觉流常量层。

定义图像色彩格式 (RGB, BGRA) 以及抓取策略和底层 Win32 API 标志位。
"""

from enum import Enum


class ColorFormat(str, Enum):
    """图像色彩排列格式。"""

    RGB = "RGB"
    RGBA = "RGBA"
    BGR = "BGR"
    BGRA = "BGRA"
    GRAY = "GRAY"


class CaptureStrategy(str, Enum):
    """图像抓取策略。"""

    PRINT_WINDOW = "print_window"
    DXGI = "dxgi"
    AUTO = "auto"


# ---------------------------------------------------------------------------
# Win32 PrintWindow 标志位 (PrintWindow API Flags)
# ---------------------------------------------------------------------------
PW_CLIENTONLY: int = 0x00000001
"""仅抓取客户区 (Client Area)，去除标题栏和边框。"""

PW_RENDERFULLCONTENT: int = 0x00000002
"""强制使用 DWM / DirectComposition 渲染完整内容 (适用于 Win8/Win10+)。"""


# ---------------------------------------------------------------------------
# DXGI 捕获相关常量定义
# ---------------------------------------------------------------------------
DXGI_ERROR_UNSUPPORTED: int = 0x887A0004
DXGI_ERROR_ACCESS_LOST: int = 0x887A0026
DXGI_ERROR_WAIT_TIMEOUT: int = 0x887A0001
