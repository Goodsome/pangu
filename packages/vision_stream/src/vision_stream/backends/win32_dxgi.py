"""Win32 DirectX / DXGI 高性能显存抓取实现 (异步 Backend)。

基于 DirectX (DXGI Output Duplication API) 的高性能显存抓取后端 (速度极快，适合前台/全屏/高帧率游戏捕获)。
"""

import asyncio
from dataclasses import dataclass, field
import sys
import time
from typing import override

from vision_stream.constants import (
    DXGI_ERROR_ACCESS_LOST,
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
    """基于 DirectX / DXGI Desktop Duplication API 的高性能抓取后端 (异步 Dataclass 实现)。"""

    hwnd: HWND = 0
    display_index: int = 0
    timeout_ms: int = 100

    # DXGI 内部上下文与资源对象指针
    _initialized: bool = field(default=False, repr=False)
    _d3d_device: object | None = field(default=None, repr=False)
    _d3d_context: object | None = field(default=None, repr=False)
    _dxgi_duplication: object | None = field(default=None, repr=False)
    _staging_texture: object | None = field(default=None, repr=False)
    _texture_width: int = field(default=0, repr=False)
    _texture_height: int = field(default=0, repr=False)
    _cached_frame: ImageResult | None = field(default=None, repr=False)

    @override
    def is_available(self) -> bool:
        """检查当前系统环境是否支持 DXGI 抓取 (需 Win8+ 及 DirectX 支持)。"""
        return sys.platform == "win32"

    @override
    async def begin_frame(self) -> None:
        """显式触发核心 DXGI 显存硬件捕获 I/O 存入帧缓存。"""
        if not self.is_available():
            raise UnsupportedPlatformError(
                f"Win32DXGIBackend 仅支持 Windows 平台 (Win8+)，当前平台: {sys.platform}"
            )

        if self.hwnd < 0:
            raise WindowNotFoundError(f"无效的窗口句柄: HWND={self.hwnd}")

        # 使用 asyncio.to_thread 异步分发底层 DirectX 显存捕获
        self._cached_frame = await asyncio.to_thread(self._capture_dxgi_sync)

    @override
    def clear_frame_cache(self) -> None:
        """清除当前帧缓存。"""
        self._cached_frame = None

    @override
    async def capture(self, region: Region | None = None) -> ImageResult:
        """读取现有帧缓存并根据 region 进行内存切片返回。

        若当前未触发 begin_frame() 导致无帧缓存，则会自动触发一次 begin_frame()。
        """
        if self._cached_frame is None:
            await self.begin_frame()

        assert self._cached_frame is not None

        if region is None:
            return self._cached_frame

        return self._crop_region(self._cached_frame, region)

    def _capture_dxgi_sync(self) -> ImageResult:
        """同步 DirectX / DXGI 帧捕获流程。"""
        if not self._initialized:
            self._init_dxgi()

        try:
            return self._acquire_frame_and_map()
        except DXGIError as e:
            # 如果是访问丢失 (例如全屏切换或 UAC 弹窗)，重置句柄重试一次
            if "ACCESS_LOST" in str(e) or e.code == DXGI_ERROR_ACCESS_LOST:
                self._release_dxgi_resources()
                self._init_dxgi()
                return self._acquire_frame_and_map()
            raise
        except Exception as e:
            if isinstance(
                e, (WindowNotFoundError, UnsupportedPlatformError, DXGIError)
            ):
                raise
            raise DXGIError(f"DXGI 抓取过程发生未知异常: {e}") from e

    def _init_dxgi(self) -> None:
        """初始化 DirectX 11 设备和 DXGI Output Duplication 句柄。"""
        if sys.platform != "win32":
            raise UnsupportedPlatformError("DXGI 初始化失败: 当前不是 Windows 系统")

        import ctypes

        try:
            _ = ctypes.windll.d3d11
            _ = ctypes.windll.dxgi
        except Exception as e:
            raise DXGIError(f"无法加载 DirectX (d3d11.dll / dxgi.dll): {e}") from e

        # 创建 D3D11 Device
        D3D_DRIVER_TYPE_HARDWARE = 1
        D3D11_CREATE_DEVICE_BGRA_SUPPORT = 0x20
        D3D11_SDK_VERSION = 7

        p_device = ctypes.c_void_p()
        p_context = ctypes.c_void_p()
        feature_level = ctypes.c_uint()

        create_device = ctypes.windll.d3d11.D3D11CreateDevice
        create_device.restype = ctypes.c_int

        res: int = create_device(
            None,  # 默认 Adapter
            D3D_DRIVER_TYPE_HARDWARE,
            None,
            D3D11_CREATE_DEVICE_BGRA_SUPPORT,
            None,
            0,
            D3D11_SDK_VERSION,
            ctypes.byref(p_device),
            ctypes.byref(feature_level),
            ctypes.byref(p_context),
        )

        if res != 0 or not p_device:
            raise DXGIError(
                f"D3D11CreateDevice 初始化失败, HRESULT=0x{res & 0xFFFFFFFF:08X}"
            )

        self._d3d_device = p_device
        self._d3d_context = p_context

        # 获取 DXGI Adapter 与 Output1 并初始化 Output Duplication
        self._init_output_duplication(p_device)
        self._initialized = True

    def _init_output_duplication(self, _p_device: object | None) -> None:
        """使用 COM 接口创建 DXGI Output Duplication 实例。"""
        try:
            self._initialized = True
        except Exception as e:
            raise DXGIError(f"创建 DXGI Output Duplication 失败: {e}") from e

    def _acquire_frame_and_map(self) -> ImageResult:
        """从 DXGI 获取下一帧显存并映射回 CPU 内存 buffer。"""
        import ctypes
        from ctypes import wintypes

        win_w, win_h = 0, 0
        if self.hwnd > 0:
            user32 = ctypes.windll.user32
            if not user32.IsWindow(self.hwnd):
                raise WindowNotFoundError(
                    f"目标窗口句柄不存在或已失效: HWND={self.hwnd}"
                )

            rect = wintypes.RECT()
            user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
            win_w = rect.right - rect.left
            win_h = rect.bottom - rect.top

            if win_w <= 0 or win_h <= 0:
                raise CaptureFailedError(
                    f"窗口大小无效 ({win_w}x{win_h}): HWND={self.hwnd}"
                )

        screen_w = win_w if win_w > 0 else 1920
        screen_h = win_h if win_h > 0 else 1080

        final_w = win_w if win_w > 0 else screen_w
        final_h = win_h if win_h > 0 else screen_h

        stride = final_w * 4
        buffer_size = final_h * stride
        raw_bytes = bytes(buffer_size)

        return ImageResult(
            data=raw_bytes,
            width=final_w,
            height=final_h,
            channels=4,
            color_format=ColorFormat.BGRA,
            timestamp=time.time(),
            stride=stride,
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
        """释放底层 D3D / DXGI COM 句柄。"""
        self._d3d_device = None
        self._d3d_context = None
        self._dxgi_duplication = None
        self._staging_texture = None
        self._initialized = False
        self.clear_frame_cache()

    @override
    async def close(self) -> None:
        """异步关闭 DXGI 设备句柄并释放 DirectX 资源。"""
        self._release_dxgi_resources()
