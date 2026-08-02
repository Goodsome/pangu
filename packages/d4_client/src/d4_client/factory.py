"""D4Client 自动查找与组装工厂模块 (factory.py)。

根据窗口标题 ("暗黑破坏神IV") 检索可见游戏窗口列表 list[HWND]，
并按屏幕几何网格位置 (1, 2 / 3, 4 从左到右、从上到下) 进行智能排序组装 D4Client。
"""

from dataclasses import dataclass
import sys

from cv_engine import OcrEngine, TemplateMatcher
from d4_client.client import D4Client
from d4_client.window import D4Window
from sys_input import HWND, Win32MessageBackend
from vision_stream import Win32DXGIBackend, Win32PrintWindowBackend


@dataclass(frozen=True)
class WindowRectInfo:
    """窗口绝对位置与句柄结构。"""

    hwnd: HWND
    left: int
    top: int
    right: int
    bottom: int
    client_width: int = 0
    client_height: int = 0

    @property
    def window_height(self) -> int:
        """整个窗口外框高度 (含标题栏和边框)。"""
        return self.bottom - self.top

    @property
    def window_width(self) -> int:
        """整个窗口外框宽度 (含标题栏和边框)。"""
        return self.right - self.left

    @property
    def height(self) -> int:
        """客户区高度 (优先使用实际 GetClientRect 高度)。"""
        return self.client_height if self.client_height > 0 else self.window_height

    @property
    def width(self) -> int:
        """客户区宽度 (优先使用实际 GetClientRect 宽度)。"""
        return self.client_width if self.client_width > 0 else self.window_width


def find_d4_window_rects(title_keyword: str = "暗黑破坏神IV") -> list[WindowRectInfo]:
    """获取匹配特定标题关键词的所有可见窗口位置列表。

    跨平台兼容：在 Windows 平台通过 Win32 EnumWindows 枚举；在非 Win 平台返回空列表。
    """
    if sys.platform != "win32":
        return []

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32

    # 声明 DPI 感知，确保获取真实物理像素 (Physical Pixels) 而非 DPI 缩放后的逻辑像素
    try:
        user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass

    windows: list[WindowRectInfo] = []

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def enum_windows_callback(hwnd: HWND, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True

        length: int = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True

        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        window_title: str = str(buffer.value)

        if title_keyword in window_title:
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))

            client_rect = wintypes.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(client_rect))
            cw = client_rect.right - client_rect.left
            ch = client_rect.bottom - client_rect.top

            windows.append(
                WindowRectInfo(
                    hwnd=hwnd,
                    left=rect.left,
                    top=rect.top,
                    right=rect.right,
                    bottom=rect.bottom,
                    client_width=cw,
                    client_height=ch,
                )
            )
        return True

    user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
    return windows


def sort_window_rects(
    windows: list[WindowRectInfo], row_tolerance: int = 50
) -> list[WindowRectInfo]:
    """按网格几何位置对窗口列表进行智能排序 (1, 2 / 3, 4)。

    排序规则：
    1. 优先按 Y 轴 (Top 坐标) 进行分行（容差范围内算作同一行）；
    2. 同一行内按 X 轴 (Left 坐标) 从左到右从低到高排列。
    """
    if not windows:
        return []

    # 先按 top 严格升序排序
    sorted_by_top = sorted(windows, key=lambda w: w.top)

    # 进行分行分组
    rows: list[list[WindowRectInfo]] = []
    for win in sorted_by_top:
        placed = False
        for row in rows:
            # 如果当前窗口的 top 与该行代表窗口 top 相差不超过 row_tolerance 像素
            if abs(win.top - row[0].top) <= row_tolerance:
                row.append(win)
                placed = True
                break
        if not placed:
            rows.append([win])

    # 对每一行内的窗口按照 left (X 轴) 从小到大排序
    sorted_result: list[WindowRectInfo] = []
    for row in rows:
        row_sorted = sorted(row, key=lambda w: w.left)
        sorted_result.extend(row_sorted)

    return sorted_result


def find_d4_hwnds(
    title_keyword: str = "暗黑破坏神IV", row_tolerance: int = 50
) -> list[HWND]:
    """按屏幕位置网格 (1, 2 / 3, 4) 顺序返回暗黑 IV 游戏窗口 HWND 列表。"""
    rects = find_d4_window_rects(title_keyword=title_keyword)
    sorted_rects = sort_window_rects(rects, row_tolerance=row_tolerance)
    return [w.hwnd for w in sorted_rects]


def create_d4_client_for_rect(
    rect: WindowRectInfo,
    render_full_content: bool = True,
    client_only: bool = True,
    ocr_lang: str = "ch",
    use_gpu: bool = False,
    use_dxgi: bool = True,
) -> D4Client:
    """基于 WindowRectInfo 构建独立的 D4Client 实例。"""
    input_backend = Win32MessageBackend(hwnd=rect.hwnd)

    if use_dxgi:
        vision_backend: Win32DXGIBackend | Win32PrintWindowBackend = Win32DXGIBackend(
            hwnd=rect.hwnd,
            client_only=client_only,
            use_screen_dc=True,
        )
    else:
        vision_backend = Win32PrintWindowBackend(
            hwnd=rect.hwnd,
            render_full_content=render_full_content,
            client_only=client_only,
        )

    template_matcher = TemplateMatcher()
    ocr_engine = OcrEngine(lang=ocr_lang, use_gpu=use_gpu)

    window = D4Window(
        input_backend=input_backend,
        vision_backend=vision_backend,
        template_matcher=template_matcher,
        ocr_engine=ocr_engine,
        width=rect.width,
        height=rect.height,
    )

    return D4Client(hwnd=rect.hwnd, window=window)


def create_d4_client_by_index(
    index: int = 0,
    title_keyword: str = "暗黑破坏神IV",
    render_full_content: bool = True,
    client_only: bool = True,
    ocr_lang: str = "ch",
    use_gpu: bool = False,
    use_dxgi: bool = True,
) -> D4Client:
    """根据屏幕按网格位置排序后的 WindowRectInfo 列表，按索引创建单个 D4Client 实例。

    Raises:
        IndexError: 未查找到满足条件的窗口或索引超出范围
    """
    rects = find_d4_window_rects(title_keyword=title_keyword)
    sorted_rects = sort_window_rects(rects)
    if not sorted_rects:
        raise IndexError(f"未找到标题包含 '{title_keyword}' 的暗黑 4 游戏窗口")
    if index < 0 or index >= len(sorted_rects):
        raise IndexError(f"窗口索引 [{index}] 超出找到的窗口数量 ({len(sorted_rects)})")

    target_rect = sorted_rects[index]
    return create_d4_client_for_rect(
        rect=target_rect,
        render_full_content=render_full_content,
        client_only=client_only,
        ocr_lang=ocr_lang,
        use_gpu=use_gpu,
        use_dxgi=use_dxgi,
    )


def create_d4_clients(
    title_keyword: str = "暗黑破坏神IV",
    render_full_content: bool = True,
    client_only: bool = True,
    ocr_lang: str = "ch",
    use_gpu: bool = False,
    use_dxgi: bool = True,
) -> list[D4Client]:
    """自动检索系统中所有匹配的暗黑 IV 窗口，并按网格位置顺序构建 list[D4Client]。

    Returns:
        list[D4Client]: 按屏幕排列顺序 (1, 2 / 3, 4) 组织的 D4Client 列表
    """
    rects = find_d4_window_rects(title_keyword=title_keyword)
    sorted_rects = sort_window_rects(rects)
    return [
        create_d4_client_for_rect(
            rect=rect,
            render_full_content=render_full_content,
            client_only=client_only,
            ocr_lang=ocr_lang,
            use_gpu=use_gpu,
            use_dxgi=use_dxgi,
        )
        for rect in sorted_rects
    ]
