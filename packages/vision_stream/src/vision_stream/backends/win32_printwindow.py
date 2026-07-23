"""Win32 PrintWindow 后台窗口抓取实现 (异步 Backend)。

依赖 HWND 的后台窗口 PrintWindow / GDI 抓取实现 (兼容性好，支持遮挡/后台抓取，速度一般)。
"""

import asyncio
from dataclasses import dataclass
import sys
import time
from typing import override

from vision_stream.constants import PW_CLIENTONLY, PW_RENDERFULLCONTENT, ColorFormat
from vision_stream.exceptions import (
    CaptureFailedError,
    UnsupportedPlatformError,
    WindowNotFoundError,
)
from vision_stream.interfaces import IWindowVisionBackend
from vision_stream.models import HWND, ImageResult, Region


@dataclass
class Win32PrintWindowBackend(IWindowVisionBackend):
    """基于 Win32 PrintWindow API 的后台窗口抓取后端 (异步 Dataclass 实现)。"""

    hwnd: HWND = 0
    render_full_content: bool = True
    client_only: bool = False

    @override
    def is_available(self) -> bool:
        """检查当前系统环境是否支持 Win32 API。"""
        return sys.platform == "win32"

    @override
    async def capture(self, region: Region | None = None) -> ImageResult:
        """异步捕获已被绑定窗口句柄 (self.hwnd) 的图像。

        Args:
            region: 可选的图像截取子区域 (ROI)

        Returns:
            ImageResult: 包含 BGRA 数据的图像对象
        """
        if not self.is_available():
            raise UnsupportedPlatformError(
                f"Win32PrintWindowBackend 仅支持 Windows 平台，当前平台: {sys.platform}"
            )

        if self.hwnd <= 0:
            raise WindowNotFoundError(f"无效的窗口句柄: HWND={self.hwnd}")

        # 使用 asyncio.to_thread 包装 CPU/Win32 GDI 阻塞调用，避免卡顿事件循环
        return await asyncio.to_thread(self._capture_win32_sync, self.hwnd, region)

    def _capture_win32_sync(
        self, hwnd: HWND, region: Region | None = None
    ) -> ImageResult:
        """Win32 GDI / PrintWindow Ctypes 捕获同步逻辑。"""
        try:
            return self._do_capture_win32(hwnd, region)
        except Exception as e:
            if isinstance(
                e, (WindowNotFoundError, UnsupportedPlatformError, CaptureFailedError)
            ):
                raise
            raise CaptureFailedError(f"PrintWindow 抓取异常: {e}") from e

    def _do_capture_win32(
        self, hwnd: HWND, region: Region | None = None
    ) -> ImageResult:
        """底层 Win32 Ctypes 结构与 GDI 捕获。"""
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        if not user32.IsWindow(hwnd):
            raise WindowNotFoundError(f"窗口不存在或已销毁: HWND={hwnd}")

        rect = wintypes.RECT()
        if self.client_only:
            user32.GetClientRect(hwnd, ctypes.byref(rect))
        else:
            user32.GetWindowRect(hwnd, ctypes.byref(rect))

        width = rect.right - rect.left
        height = rect.bottom - rect.top

        if width <= 0 or height <= 0:
            raise CaptureFailedError(f"窗口尺寸无效 ({width}x{height}): HWND={hwnd}")

        # 获取 DC 并创建兼容 DC/Bitmap
        hdc_window = user32.GetWindowDC(hwnd)
        if not hdc_window:
            raise CaptureFailedError(f"获取窗口 DC 失败: HWND={hwnd}")

        hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
        hbm = gdi32.CreateCompatibleBitmap(hdc_window, width, height)
        gdi32.SelectObject(hdc_mem, hbm)

        flags = 0
        if self.client_only:
            flags |= PW_CLIENTONLY
        if self.render_full_content:
            flags |= PW_RENDERFULLCONTENT

        success = bool(user32.PrintWindow(hwnd, hdc_mem, flags))

        if not success:
            # 清理句柄
            gdi32.DeleteObject(hbm)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(hwnd, hdc_window)
            raise CaptureFailedError(f"PrintWindow API 调用失败: HWND={hwnd}")

        # 获取位图 RGB/BGRA 字节数据
        bmp_header_size = 40
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
        bmi.biSize = bmp_header_size
        bmi.biWidth = width
        bmi.biHeight = -height  # 负数表示自顶向下的 DIB
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0  # BI_RGB

        gdi32.GetDIBits(
            hdc_mem,
            hbm,
            0,
            height,
            ctypes.byref(buffer),
            ctypes.byref(bmi),
            0,  # DIB_RGB_COLORS
        )

        # 释放 GDI 句柄资源
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(hwnd, hdc_window)

        raw_bytes = bytes(buffer)

        # 如果指定了 region 剪裁
        if region:
            return self._crop_region(raw_bytes, width, height, region)

        return ImageResult(
            data=raw_bytes,
            width=width,
            height=height,
            channels=4,
            color_format=ColorFormat.BGRA,
            timestamp=time.time(),
            stride=width * 4,
        )

    def _crop_region(
        self, raw_bytes: bytes, src_w: int, src_h: int, region: Region
    ) -> ImageResult:
        """切割 ROI 区域字节数据。"""
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
            color_format=ColorFormat.BGRA,
            timestamp=time.time(),
            stride=crop_stride,
        )

    @override
    async def close(self) -> None:
        """异步关闭并清理 Backend 资源。"""
        pass
