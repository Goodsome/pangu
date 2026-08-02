# pyright: reportAny=false, reportIncompatibleVariableOverride=false, reportUnannotatedClassAttribute=false
"""Win32 DXGI / 桌面显存极速抓取后端实现 (Win32DXGIBackend)。

针对 Windows 高性能图形渲染窗口与游戏客户端，
基于 Win32 GDI / D3D 显存直接映射与 Memory BitBlt 抓取像素，提供毫秒级图像流。
"""

import asyncio
from dataclasses import dataclass
import sys
import time
from typing import override

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
        """从显存缓冲区捕获当前窗口的真实彩色画面 (包含 DPI 物理分辨率精准校正)。"""
        import ctypes
        from ctypes import wintypes

        if self.hwnd <= 0:
            raise WindowNotFoundError(f"未绑定有效的窗口句柄: HWND={self.hwnd}")

        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        if not user32.IsWindow(self.hwnd):
            raise WindowNotFoundError(f"目标窗口句柄不存在或已失效: HWND={self.hwnd}")

        dpi_scale = 1.0
        try:
            dpi_val = user32.GetDpiForWindow(self.hwnd)
            if dpi_val > 0:
                dpi_scale = dpi_val / 96.0
        except Exception:
            pass

        use_window_dc = False
        width: int = 0
        height: int = 0
        src_x: int = 0
        src_y: int = 0
        hdc_screen: object = None

        if self.client_only:
            # 优先尝试从窗口自身的 HDC 进行纯客户区捕获 (天然去除系统标题栏与桌面偏移)
            hdc_win = user32.GetDC(self.hwnd)
            client_rect = wintypes.RECT()
            if user32.GetClientRect(self.hwnd, ctypes.byref(client_rect)):
                width = client_rect.right - client_rect.left
                height = client_rect.bottom - client_rect.top
                if width > 0 and height > 0 and hdc_win:
                    use_window_dc = True
                    hdc_screen = hdc_win

            if not use_window_dc:
                dwmapi = ctypes.windll.dwmapi
                dwm_rect = wintypes.RECT()
                has_dwm = (
                    dwmapi.DwmGetWindowAttribute(
                        self.hwnd, 9, ctypes.byref(dwm_rect), ctypes.sizeof(dwm_rect)
                    )
                    == 0
                )

                window_rect = dwm_rect if has_dwm else wintypes.RECT()
                if not has_dwm:
                    user32.GetWindowRect(self.hwnd, ctypes.byref(window_rect))

                client_rect = wintypes.RECT()
                if not user32.GetClientRect(self.hwnd, ctypes.byref(client_rect)):
                    raise CaptureFailedError(
                        f"获取窗口 ClientRect 失败: HWND={self.hwnd}"
                    )

                width = client_rect.right - client_rect.left
                height = client_rect.bottom - client_rect.top

                pt = wintypes.POINT(0, 0)
                user32.ClientToScreen(self.hwnd, ctypes.byref(pt))
                src_x = pt.x
                src_y = pt.y

                if abs(src_y - window_rect.top) < 5:
                    caption_h = user32.GetSystemMetrics(4)
                    frame_y = user32.GetSystemMetrics(33)
                    border_h = user32.GetSystemMetrics(92)
                    offset_y = caption_h + frame_y + border_h
                    src_y += offset_y
                    height = max(1, height - offset_y)
        else:
            rect = wintypes.RECT()
            if not user32.GetWindowRect(self.hwnd, ctypes.byref(rect)):
                raise CaptureFailedError(f"获取窗口 RECT 失败: HWND={self.hwnd}")
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            src_x = rect.left
            src_y = rect.top

        if not use_window_dc:
            hdc_screen = user32.GetDC(0)
            if not hdc_screen:
                raise CaptureFailedError("获取桌面显存 DC 失败")

        phys_width = int(width * dpi_scale) if not use_window_dc else width
        phys_height = int(height * dpi_scale) if not use_window_dc else height
        phys_src_x = int(src_x * dpi_scale)
        phys_src_y = int(src_y * dpi_scale)

        if phys_width <= 0 or phys_height <= 0:
            if use_window_dc and hdc_screen:
                user32.ReleaseDC(self.hwnd, hdc_screen)
            raise CaptureFailedError(
                f"捕获窗口物理尺寸无效 ({phys_width}x{phys_height}): HWND={self.hwnd}"
            )

        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        hbm = gdi32.CreateCompatibleBitmap(hdc_screen, phys_width, phys_height)
        old_hbm = gdi32.SelectObject(hdc_mem, hbm)

        SRCCOPY = 0x00CC0020
        success = bool(
            gdi32.BitBlt(
                hdc_mem,
                0,
                0,
                phys_width,
                phys_height,
                hdc_screen,
                phys_src_x,
                phys_src_y,
                SRCCOPY,
            )
        )

        if not success:
            gdi32.SelectObject(hdc_mem, old_hbm)
            gdi32.DeleteObject(hbm)
            gdi32.DeleteDC(hdc_mem)
            if use_window_dc:
                user32.ReleaseDC(self.hwnd, hdc_screen)
            else:
                user32.ReleaseDC(0, hdc_screen)
            raise CaptureFailedError(f"从显存拷贝像素失败: HWND={self.hwnd}")

        buffer_size = phys_width * phys_height * 4
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
        bmi.biWidth = phys_width
        bmi.biHeight = -phys_height
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0

        gdi32.GetDIBits(
            hdc_mem,
            hbm,
            0,
            phys_height,
            ctypes.byref(buffer),
            ctypes.byref(bmi),
            0,
        )

        gdi32.SelectObject(hdc_mem, old_hbm)
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem)
        if use_window_dc:
            user32.ReleaseDC(self.hwnd, hdc_screen)
        else:
            user32.ReleaseDC(0, hdc_screen)

        raw_bytes = bytes(buffer)

        return ImageResult(
            data=raw_bytes,
            width=phys_width,
            height=phys_height,
            channels=4,
            color_format=ColorFormat.BGRA,
            timestamp=time.time(),
            stride=phys_width * 4,
        )

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
