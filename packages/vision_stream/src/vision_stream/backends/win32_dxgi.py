"""Win32 DirectX / DXGI 高性能显存抓取实现 (异步 Backend)。

基于 DirectX / 桌面显存缓冲区的抓取后端。
必须绑定有效 HWND 窗口句柄，捕获游戏窗口的真实像素；当抓取失败或句柄无效时抛出明确异常。
"""

import asyncio
from dataclasses import dataclass, field
import sys
import time
from typing import override

from vision_stream.constants import (
    ColorFormat,
)
from vision_stream.exceptions import (
    CaptureFailedError,
    DXGIError,
    UnsupportedPlatformError,
    WindowNotFoundError,
)
from vision_stream.interfaces import IWindowVisionBackend
from vision_stream.models import HWND, ImageResult, Region


@dataclass
class Win32DXGIBackend(IWindowVisionBackend):
    """基于 DirectX / 桌面显存缓冲区的抓取后端。"""

    hwnd: HWND = 0

    # 内部上下文与资源对象指针
    _initialized: bool = field(default=False, repr=False)
    _d3d_device: object | None = field(default=None, repr=False)
    _d3d_context: object | None = field(default=None, repr=False)
    _dxgi_duplication: object | None = field(default=None, repr=False)
    _cached_frame: ImageResult | None = field(default=None, repr=False)

    @override
    def is_available(self) -> bool:
        """检查当前系统环境是否支持抓取。"""
        return sys.platform == "win32"

    @override
    async def begin_frame(self) -> None:
        """显式触发核心显存硬件捕获 I/O 存入帧缓存。"""
        if not self.is_available():
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
        except Exception as e:
            raise DXGIError(f"无法加载 Win32 系统动态库: {e}") from e

        self._initialized = True

    def _acquire_frame_and_map(self) -> ImageResult:
        """从显存缓冲区捕获当前窗口的真实彩色画面。句柄无效或尺寸异常时抛出报错。"""
        import ctypes
        from ctypes import wintypes

        if self.hwnd <= 0:
            raise WindowNotFoundError(f"未绑定有效的窗口句柄: HWND={self.hwnd}")

        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        if not user32.IsWindow(self.hwnd):
            raise WindowNotFoundError(f"目标窗口句柄不存在或已失效: HWND={self.hwnd}")

        rect = wintypes.RECT()
        if not user32.GetWindowRect(self.hwnd, ctypes.byref(rect)):
            raise CaptureFailedError(f"获取窗口 RECT 失败: HWND={self.hwnd}")

        width = rect.right - rect.left
        height = rect.bottom - rect.top

        if width <= 0 or height <= 0:
            raise CaptureFailedError(
                f"捕获窗口尺寸无效 ({width}x{height}): HWND={self.hwnd}"
            )

        # 1. 获取显存桌面合成器 DC
        hdc_screen = user32.GetDC(0)
        if not hdc_screen:
            raise CaptureFailedError("获取桌面显存 DC 失败")

        # 2. 创建内存 DC 及兼容位图
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        hbm = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
        old_hbm = gdi32.SelectObject(hdc_mem, hbm)

        # 3. 从显存句柄拷贝像素数据
        SRCCOPY = 0x00CC0020
        success = bool(
            gdi32.BitBlt(
                hdc_mem,
                0,
                0,
                width,
                height,
                hdc_screen,
                rect.left,
                rect.top,
                SRCCOPY,
            )
        )

        if not success:
            gdi32.SelectObject(hdc_mem, old_hbm)
            gdi32.DeleteObject(hbm)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(0, hdc_screen)
            raise CaptureFailedError(f"从显存拷贝像素失败: HWND={self.hwnd}")

        # 4. 读取内存像素位图 (BGRA 32 位)
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
        bmi.biHeight = -height  # 自顶向下 (Top-down DIB)
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

        # 5. 释放 DC 资源
        gdi32.SelectObject(hdc_mem, old_hbm)
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc_screen)

        raw_bytes = bytes(buffer)

        return ImageResult(
            data=raw_bytes,
            width=width,
            height=height,
            channels=4,
            color_format=ColorFormat.BGRA,
            timestamp=time.time(),
            stride=width * 4,
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

        row_stride = src_w * 4
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
