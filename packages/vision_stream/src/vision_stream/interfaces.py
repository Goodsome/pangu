"""视觉流契约层。

定义统一的异步窗口图像抓取后端 Protocol 接口契约。
"""

from typing import Protocol, runtime_checkable

from vision_stream.models import ImageResult, Region


@runtime_checkable
class IWindowVisionBackend(Protocol):
    """统一窗口视觉抓取后端接口契约 (异步接口)。

    解耦底层抓取技术实现（例如 Win32 PrintWindow 后台抓取或 DXGI 显存硬件加速抓取）。
    """

    async def capture(self, region: Region | None = None) -> ImageResult:
        """异步捕获当前绑定窗口句柄的单帧图像。

        Args:
            region: 可选的相对抓取区域 ROI (如不提供则抓取整个窗口)

        Returns:
            ImageResult 抓取的图像数据结果

        Raises:
            WindowNotFoundError: 当绑定的窗口句柄无效或不存在时抛出
            CaptureFailedError: 图像捕获过程失败时抛出
            UnsupportedPlatformError: 当运行平台不支持该 Backend 时抛出
        """
        ...

    async def begin_frame(self) -> None:
        """显式触发捕获当前窗口图像并写入帧缓存。

        在后续调用 capture() 时将优先使用此缓存帧（若指定 region 则对缓存帧进行剪裁），
        直至再次调用 begin_frame() 刷新缓存或显式清除缓存。
        """
        ...

    def clear_frame_cache(self) -> None:
        """清除当前帧缓存。"""
        ...

    def is_available(self) -> bool:
        """判断当前环境与操作系统是否支持并就绪该后端驱动。"""
        ...

    async def close(self) -> None:
        """异步释放底层图形设备、DC 句柄或 DXGI 显存资源。"""
        ...
