# pyright: reportAny=false, reportIncompatibleVariableOverride=false, reportUnannotatedClassAttribute=false
"""Win32 DXGI / 桌面显存极速抓取后端实现 (Win32DXGIBackend)。

针对 Windows 高性能图形渲染窗口与游戏客户端，
基于 Win32 GDI / D3D 显存直接映射与 Memory BitBlt 抓取像素，提供毫秒级图像流。
"""

import asyncio
from dataclasses import dataclass
import sys
import time
from typing import Any, override

from sys_input import HWND
from vision_stream.constants import ColorFormat
from vision_stream.exceptions import (
    CaptureFailedError,
    DXGIError,
    UnsupportedPlatformError,
    WindowNotFoundError,
)
from vision_stream.interfaces import IWindowVisionBackend
from vision_stream.models import ImageResult, Region


@dataclass
class Win32DXGIBackend(IWindowVisionBackend):
    """Win32 DXGI 显存极速画面捕获后端。"""

    hwnd: HWND
    client_only: bool = True
    use_screen_dc: bool = False

    _initialized: bool = False
    _d3d_device: object | None = None
    _d3d_context: object | None = None
    _dxgi_duplication: object | None = None
    _cached_frame: ImageResult | None = None

    def __post_init__(self) -> None:
        if sys.platform != "win32":
            raise UnsupportedPlatformError(
                f"Win32DXGIBackend 仅支持 Windows 平台，当前平台: {sys.platform}"
            )
        if self.hwnd <= 0:
            raise WindowNotFoundError(f"未绑定有效的窗口句柄: HWND={self.hwnd}")

    @override
    def is_available(self) -> bool:
        """判断当前环境与操作系统是否支持并就绪该后端驱动。"""
        return sys.platform == "win32" and self.hwnd > 0

    @override
    async def begin_frame(self) -> None:
        """显式触发底层视觉后端捕获并缓存单帧画面。"""
        if sys.platform != "win32":
            raise UnsupportedPlatformError(
                f"Win32DXGIBackend 仅支持 Windows 平台，当前平台: {sys.platform}"
            )

        if self.hwnd <= 0:
            raise WindowNotFoundError(f"未绑定有效的窗口句柄: HWND={self.hwnd}")

        self._cached_frame = await asyncio.to_thread(self._capture_dxgi_sync)

    @override
    def clear_frame_cache(self) -> None:
        """清除当前帧缓存。"""
        self._cached_frame = None

    @override
    async def capture(self, region: Region | None = None) -> ImageResult:
        """读取现有帧缓存并根据 region 进行内存切片返回。"""
        if self._cached_frame is None:
            await self.begin_frame()

        assert self._cached_frame is not None

        if region is None:
            return self._cached_frame

        return self._crop_region(self._cached_frame, region)

    def _capture_dxgi_sync(self) -> ImageResult:
        """同步帧捕获流程。"""
        if sys.platform != "win32":
            raise UnsupportedPlatformError("抓取仅支持 Windows 平台")

        if self.hwnd <= 0:
            raise WindowNotFoundError(f"未绑定有效的窗口句柄: HWND={self.hwnd}")

        if not self._initialized:
            self._init_dxgi()

        try:
            return self._acquire_frame_and_map()
        except Exception as e:
            if isinstance(
                e,
                (
                    WindowNotFoundError,
                    UnsupportedPlatformError,
                    DXGIError,
                    CaptureFailedError,
                ),
            ):
                raise
            raise DXGIError(f"显存抓取过程发生异常: {e}") from e

    def _init_dxgi(self) -> None:
        """初始化设备。"""
        import ctypes

        try:
            _ = ctypes.windll.user32
            _ = ctypes.windll.gdi32
            # 开启进程级 High-DPI 感知 (Per-Monitor V2)
            try:
                ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
            except Exception:
                try:
                    ctypes.windll.shcore.SetProcessDpiAwareness(2)
                except Exception:
                    try:
                        ctypes.windll.user32.SetProcessDPIAware()
                    except Exception:
                        pass
        except Exception as e:
            raise DXGIError(f"无法加载 Win32 系统动态库: {e}") from e

        self._initialized = True

    def _acquire_frame_and_map(self) -> ImageResult:
        """从显存/GDI缓冲区捕获当前窗口的真实彩色画面。"""
        import ctypes

        if self.hwnd <= 0:
            raise WindowNotFoundError(f"未绑定有效的窗口句柄: HWND={self.hwnd}")

        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        if not user32.IsWindow(self.hwnd):
            raise WindowNotFoundError(f"目标窗口句柄不存在或已失效: HWND={self.hwnd}")

        # 1. 确定捕获目标源 (Window DC 或 Desktop Screen DC) 与几何尺寸
        src_x, src_y, width, height, use_window_dc, hdc_src = (
            self._resolve_capture_target(user32)
        )

        if width <= 0 or height <= 0:
            if hdc_src:
                user32.ReleaseDC(self.hwnd if use_window_dc else 0, hdc_src)
            raise CaptureFailedError(
                f"捕获窗口物理尺寸无效 ({width}x{height}): HWND={self.hwnd}"
            )

        # 2. 安全的 GDI 内存映射与像素捕获 (使用 try...finally 保证句柄 100% 释放)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_src)
        hbm = gdi32.CreateCompatibleBitmap(hdc_src, width, height)
        old_hbm = gdi32.SelectObject(hdc_mem, hbm)

        try:
            SRCCOPY = 0x00CC0020
            success = bool(
                gdi32.BitBlt(
                    hdc_mem, 0, 0, width, height, hdc_src, src_x, src_y, SRCCOPY
                )
            )
            if not success:
                raise CaptureFailedError(f"从显存拷贝像素失败: HWND={self.hwnd}")

            raw_bytes = self._read_dib_bits(gdi32, hdc_mem, hbm, width, height)
        finally:
            # 清理 GDI 句柄资源
            gdi32.SelectObject(hdc_mem, old_hbm)
            gdi32.DeleteObject(hbm)
            gdi32.DeleteDC(hdc_mem)
            if use_window_dc:
                user32.ReleaseDC(self.hwnd, hdc_src)
            else:
                user32.ReleaseDC(0, hdc_src)

        return ImageResult(
            data=raw_bytes,
            width=width,
            height=height,
            channels=4,
            color_format=ColorFormat.BGRA,
            timestamp=time.time(),
            stride=width * 4,
        )

    def _resolve_capture_target(
        self, user32: Any
    ) -> tuple[int, int, int, int, bool, Any]:
        """判定 capture 来源 (窗口 DC 或 桌面 DC) 及其像素几何边界 (src_x, src_y, width, height)。"""
        import ctypes
        from ctypes import wintypes

        # 途径 A: 单窗口后台客户区捕获 (当 client_only=True 且未强制开启 use_screen_dc)
        if self.client_only and not self.use_screen_dc:
            hdc_win = user32.GetDC(self.hwnd)
            client_rect = wintypes.RECT()
            if user32.GetClientRect(self.hwnd, ctypes.byref(client_rect)):
                w = client_rect.right - client_rect.left
                h = client_rect.bottom - client_rect.top
                if w > 0 and h > 0 and hdc_win:
                    return 0, 0, w, h, True, hdc_win

        # 途径 B: 桌面全局屏幕 DC 捕获并做物理像素裁剪 (用于捕获弹出菜单/独立覆盖层)
        hdc_screen = user32.GetDC(0)
        if not hdc_screen:
            raise CaptureFailedError("获取桌面显存 DC 失败")

        if self.client_only:
            client_rect = wintypes.RECT()
            if not user32.GetClientRect(self.hwnd, ctypes.byref(client_rect)):
                user32.ReleaseDC(0, hdc_screen)
                raise CaptureFailedError(f"获取窗口 ClientRect 失败: HWND={self.hwnd}")

            w = client_rect.right - client_rect.left
            h = client_rect.bottom - client_rect.top

            pt = wintypes.POINT(0, 0)
            user32.ClientToScreen(self.hwnd, ctypes.byref(pt))
            return pt.x, pt.y, w, h, False, hdc_screen

        rect = wintypes.RECT()
        if not user32.GetWindowRect(self.hwnd, ctypes.byref(rect)):
            user32.ReleaseDC(0, hdc_screen)
            raise CaptureFailedError(f"获取窗口 RECT 失败: HWND={self.hwnd}")

        w = rect.right - rect.left
        h = rect.bottom - rect.top
        return rect.left, rect.top, w, h, False, hdc_screen

    @staticmethod
    def _read_dib_bits(
        gdi32: Any, hdc_mem: Any, hbm: Any, width: int, height: int
    ) -> bytes:
        """从 GDI 位图句柄读取 BGRA 字节数据。"""
        import ctypes
        from ctypes import wintypes

        buffer_size = width * height * 4
        buffer = (ctypes.c_ubyte * buffer_size)()

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = 40
        bmi.biWidth = width
        bmi.biHeight = -height  # 负数表示自顶向下的 DIB 内存排布
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0

        gdi32.GetDIBits(
            hdc_mem,
            hbm,
            0,
            height,
            ctypes.byref(buffer),
            ctypes.byref(bmi),
            0,
        )
        return bytes(buffer)

    def _crop_region(self, image: ImageResult, region: Region) -> ImageResult:
        """从 ImageResult 中根据 ROI 区域进行内存字节切片。"""
        src_w = image.width
        src_h = image.height
        raw_bytes = image.data

        crop_x = max(0, min(region.x, src_w - 1))
        crop_y = max(0, min(region.y, src_h - 1))
        crop_w = min(region.width, src_w - crop_x)
        crop_h = min(region.height, src_h - crop_y)

        if crop_w <= 0 or crop_h <= 0:
            raise CaptureFailedError(f"请求剪裁区域超出图像界限: {region}")

        row_stride = image.stride if image.stride > 0 else src_w * 4
        crop_stride = crop_w * 4
        cropped_data = bytearray(crop_h * crop_stride)

        for row in range(crop_h):
            src_offset = (crop_y + row) * row_stride + (crop_x * 4)
            dst_offset = row * crop_stride
            cropped_data[dst_offset : dst_offset + crop_stride] = raw_bytes[
                src_offset : src_offset + crop_stride
            ]

        return ImageResult(
            data=bytes(cropped_data),
            width=crop_w,
            height=crop_h,
            channels=4,
            color_format=image.color_format,
            timestamp=image.timestamp,
            stride=crop_stride,
        )

    def _release_dxgi_resources(self) -> None:
        """释放资源。"""
        self._d3d_device = None
        self._d3d_context = None
        self._dxgi_duplication = None
        self._initialized = False
        self.clear_frame_cache()

    @override
    async def close(self) -> None:
        """异步关闭设备。"""
        self._release_dxgi_resources()
