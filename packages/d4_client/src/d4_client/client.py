"""D4 自动化 SDK 聚合根与门面入口 D4Client。

向下屏蔽底层 sys_input, vision_stream, cv_engine 引擎组装细节；
向上向 Robot 业务层提供干净、强类型的 POM 页面与窗口操控入口。
"""

from dataclasses import dataclass
from types import TracebackType
from typing import Self

from cv_engine import OcrEngine, TemplateMatcher
from d4_client.models import ImageFrame, Region
from d4_client.screens.main_hud import MainHUD
from d4_client.window import D4Window
from sys_input import HWND, Win32MessageBackend
from vision_stream import Win32PrintWindowBackend


@dataclass
class D4Client:
    """暗黑破坏神 4 SDK 聚合根与门面 Client。

    示例:
        ```python
        async with D4Client.create(hwnd=12345) as client:
            # 访问主界面 HUD POM
            hud = client.main_hud
            social_screen = await hud.open_social()

            # 或直接通过控制台操控窗口
            frame = await client.window.capture()
        ```
    """

    hwnd: HWND
    window: D4Window

    @classmethod
    def create(
        cls,
        hwnd: HWND,
        render_full_content: bool = True,
        client_only: bool = False,
        ocr_lang: str = "ch",
        use_gpu: bool = False,
    ) -> Self:
        """快速工厂方法：传入句柄与基础配置，自动组装全套底层引擎与 D4Window 组合体。

        Args:
            hwnd: 目标游戏窗口句柄 HWND
            render_full_content: 画面抓取是否渲染完整内容
            client_only: 画面抓取是否仅限于客户区
            ocr_lang: OCR 识别语言模型
            use_gpu: OCR 是否使用 GPU 硬件加速

        Returns:
            D4Client: 组装就绪的 D4Client 聚合根对象
        """
        input_backend = Win32MessageBackend(hwnd=hwnd)

        vision_backend = Win32PrintWindowBackend(
            hwnd=hwnd,
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
        )

        return cls(hwnd=hwnd, window=window)

    @property
    def main_hud(self) -> MainHUD:
        """获取游戏常驻主界面 (MainHUD) 页面对象。"""
        return MainHUD(window=self.window)

    async def capture(self, region: Region | None = None) -> ImageFrame:
        """快捷代理：捕获窗口画面。"""
        return await self.window.capture(region=region)

    async def close(self) -> None:
        """释放底层图形设备、句柄与视觉匹配引擎缓存。"""
        await self.window.close()

    # ---------------------------------------------------------------------------
    # 异步上下文管理器 (async with D4Client(...) as client)
    # ---------------------------------------------------------------------------
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
