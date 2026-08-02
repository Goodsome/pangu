# -*- coding: utf-8 -*-
"""MhxyClient 自动查找与组装工厂模块 (factory.py)。

根据窗口标题 ("梦幻西游") 检索可见游戏窗口列表 list[HWND]，
并按屏幕几何网格位置 (1, 2 / 3, 4 从左到右、从上到下) 进行智能排序组装 MhxyClient。
"""

import sys
from typing import Final

from mhxy_client.client import MhxyClient
from mhxy_client.exceptions import WindowNotFoundError
from mhxy_client.models import WindowRectInfo
from mhxy_client.window import MhxyWindow
from sys_input import HWND, InputBackend, Win32HardwareBackend, Win32MessageBackend
from vision_stream import Win32DXGIBackend, Win32PrintWindowBackend

# 默认窗口检索关键词："梦幻" (\u68a6\u5e7b) 确保能匹配 "梦幻西游", "梦幻西游 ONLINE" 等
DEFAULT_TITLE_KEYWORD: Final[str] = "\u68a6\u5e7b"

# 梦幻西游官方客户端固定窗口类名 (ClassName)
DEFAULT_MHXY_CLASS_NAME: Final[str] = "XYForWClass"

# 需要排除的非游戏客户端常见标题关键词 (防止误将浏览器标签页、编辑器当成游戏窗口)
EXCLUDED_TITLE_KEYWORDS: Final[tuple[str, ...]] = (
    "Chrome",
    "Edge",
    "Firefox",
    "Browser",
    "Visual Studio",
    "VS Code",
    "豆包",
    "搜狗",
    "百度",
)


def find_mhxy_window_rects(
    title_keyword: str = DEFAULT_TITLE_KEYWORD,
    class_name_keyword: str | None = DEFAULT_MHXY_CLASS_NAME,
) -> list[WindowRectInfo]:
    """获取匹配特定标题与类名的所有可见梦幻西游游戏窗口位置列表。

    优先筛选匹配梦幻西游官方类名 (XYForWClass) 的窗口；自动排除浏览器等无关非游戏窗口。
    跨平台兼容：在 Windows 平台通过 Win32 EnumWindows 枚举；在非 Windows 平台返回空列表。
    """
    if sys.platform != "win32":
        return []

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    all_matched_windows: list[tuple[WindowRectInfo, str]] = []

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def enum_windows_callback(hwnd: HWND, _lparam: int) -> bool:
        try:
            if not user32.IsWindowVisible(hwnd):
                return True

            length: int = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True

            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            window_title: str = str(buffer.value)

            # 1. 检查标题是否包含排除关键词 (如 Chrome / Edge 等浏览器)
            if any(ex in window_title for ex in EXCLUDED_TITLE_KEYWORDS):
                return True

            # 2. 检查标题是否包含游戏关键词
            if title_keyword in window_title:
                class_buffer = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_buffer, 256)
                class_name: str = str(class_buffer.value)

                dwmapi = ctypes.windll.dwmapi
                dwm_rect = wintypes.RECT()
                has_dwm = (
                    dwmapi.DwmGetWindowAttribute(
                        hwnd, 9, ctypes.byref(dwm_rect), ctypes.sizeof(dwm_rect)
                    )
                    == 0
                )
                rect = dwm_rect if has_dwm else wintypes.RECT()
                if not has_dwm:
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))

                client_rect = wintypes.RECT()
                user32.GetClientRect(hwnd, ctypes.byref(client_rect))
                cw = client_rect.right - client_rect.left
                ch = client_rect.bottom - client_rect.top

                info = WindowRectInfo(
                    hwnd=hwnd,
                    left=rect.left,
                    top=rect.top,
                    right=rect.right,
                    bottom=rect.bottom,
                    client_width=cw,
                    client_height=ch,
                    title=window_title,
                )
                all_matched_windows.append((info, class_name))
        except Exception:
            pass
        return True

    cb = WNDENUMPROC(enum_windows_callback)
    user32.EnumWindows(cb, 0)

    if not all_matched_windows:
        return []

    # 优先强过滤：如果有精准匹配 class_name_keyword (如 XYForWClass) 的游戏窗口
    if class_name_keyword:
        class_matched = [
            info
            for info, cls_n in all_matched_windows
            if class_name_keyword.lower() in cls_n.lower()
        ]
        if class_matched:
            return class_matched

    return [info for info, _ in all_matched_windows]


def sort_window_rects(
    windows: list[WindowRectInfo], row_tolerance: int = 50
) -> list[WindowRectInfo]:
    """按网格几何位置对窗口列表进行智能排序 (1, 2 / 3, 4)。

    排序规则：
    1. 优先按 Y 轴 (Top 坐标) 进行分行（容差范围内算作同一行）；
    2. 同一行内按 X 轴 (Left 坐标) 从左到右升序排列。
    """
    if not windows:
        return []

    # 先按 top 升序排序
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


def find_mhxy_hwnds(
    title_keyword: str = DEFAULT_TITLE_KEYWORD,
    class_name_keyword: str | None = DEFAULT_MHXY_CLASS_NAME,
    row_tolerance: int = 50,
) -> list[HWND]:
    """按屏幕位置网格 (1, 2 / 3, 4) 顺序返回梦幻西游游戏窗口 HWND 列表。"""
    rects = find_mhxy_window_rects(
        title_keyword=title_keyword, class_name_keyword=class_name_keyword
    )
    sorted_rects = sort_window_rects(rects, row_tolerance=row_tolerance)
    return [w.hwnd for w in sorted_rects]


def create_mhxy_client_for_rect(
    rect: WindowRectInfo,
    render_full_content: bool = True,
    client_only: bool = True,
    ocr_lang: str = "ch",
    use_gpu: bool = False,
    use_dxgi: bool = True,
    init_cv_engines: bool = False,
    use_hardware_input: bool = True,
) -> MhxyClient:
    """基于 WindowRectInfo 构建独立的 MhxyClient 实例。"""
    input_backend: InputBackend
    if use_hardware_input:
        input_backend = Win32HardwareBackend()
    else:
        input_backend = Win32MessageBackend(hwnd=rect.hwnd)

    if use_dxgi:
        vision_backend: Win32DXGIBackend | Win32PrintWindowBackend = Win32DXGIBackend(
            hwnd=rect.hwnd,
            client_only=client_only,
        )
    else:
        vision_backend = Win32PrintWindowBackend(
            hwnd=rect.hwnd,
            render_full_content=render_full_content,
            client_only=client_only,
        )

    template_matcher = None
    ocr_engine = None
    if init_cv_engines:
        from cv_engine import OcrEngine, TemplateMatcher

        template_matcher = TemplateMatcher()
        ocr_engine = OcrEngine(lang=ocr_lang, use_gpu=use_gpu)

    window = MhxyWindow(
        hwnd=rect.hwnd,
        input_backend=input_backend,
        vision_backend=vision_backend,
        template_matcher=template_matcher,
        ocr_engine=ocr_engine,
        width=rect.width,
        height=rect.height,
        title=rect.title,
    )

    return MhxyClient(hwnd=rect.hwnd, window=window)


def create_mhxy_client_by_index(
    index: int = 0,
    title_keyword: str = DEFAULT_TITLE_KEYWORD,
    class_name_keyword: str | None = DEFAULT_MHXY_CLASS_NAME,
    render_full_content: bool = True,
    client_only: bool = True,
    ocr_lang: str = "ch",
    use_gpu: bool = False,
    use_dxgi: bool = True,
    row_tolerance: int = 50,
    init_cv_engines: bool = False,
    use_hardware_input: bool = True,
) -> MhxyClient:
    """根据屏幕按网格位置排序后的 WindowRectInfo 列表，按索引创建单个 MhxyClient 实例。

    Raises:
        WindowNotFoundError: 未查找到满足条件的窗口或索引超出范围
    """
    rects = find_mhxy_window_rects(
        title_keyword=title_keyword, class_name_keyword=class_name_keyword
    )
    sorted_rects = sort_window_rects(rects, row_tolerance=row_tolerance)

    if not sorted_rects or index < 0 or index >= len(sorted_rects):
        raise WindowNotFoundError(
            f"找不到索引为 {index} 的梦幻西游窗口 (找到窗口总数: {len(sorted_rects)})"
        )

    return create_mhxy_client_for_rect(
        rect=sorted_rects[index],
        render_full_content=render_full_content,
        client_only=client_only,
        ocr_lang=ocr_lang,
        use_gpu=use_gpu,
        use_dxgi=use_dxgi,
        init_cv_engines=init_cv_engines,
        use_hardware_input=use_hardware_input,
    )


def create_mhxy_clients(
    title_keyword: str = DEFAULT_TITLE_KEYWORD,
    class_name_keyword: str | None = DEFAULT_MHXY_CLASS_NAME,
    render_full_content: bool = True,
    client_only: bool = True,
    ocr_lang: str = "ch",
    use_gpu: bool = False,
    use_dxgi: bool = True,
    row_tolerance: int = 50,
    init_cv_engines: bool = False,
    use_hardware_input: bool = True,
) -> list[MhxyClient]:
    """批量检索并智能排序创建所有梦幻西游窗口对应的 MhxyClient 实例列表。"""
    rects = find_mhxy_window_rects(
        title_keyword=title_keyword, class_name_keyword=class_name_keyword
    )
    sorted_rects = sort_window_rects(rects, row_tolerance=row_tolerance)

    return [
        create_mhxy_client_for_rect(
            rect=rect,
            render_full_content=render_full_content,
            client_only=client_only,
            ocr_lang=ocr_lang,
            use_gpu=use_gpu,
            use_dxgi=use_dxgi,
            init_cv_engines=init_cv_engines,
            use_hardware_input=use_hardware_input,
        )
        for rect in sorted_rects
    ]
