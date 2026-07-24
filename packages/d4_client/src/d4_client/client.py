"""D4 自动化 SDK 聚合根与门面入口 D4Client。

向下屏蔽底层 sys_input, vision_stream, cv_engine 引擎组装细节；
向上向 Robot 业务层提供干净、强类型的 POM 页面与窗口操控入口。
"""

from dataclasses import dataclass
from types import TracebackType
from typing import Self

from d4_client.models import ImageFrame, Region
from d4_client.screens.main_hud import MainHUD
from d4_client.window import D4Window
from sys_input import HWND


@dataclass
class D4Client:
    """暗黑破坏神 4 SDK 聚合根与门面 Client。

    示例:
        ```python
        from d4_client import create_d4_clients

        clients = create_d4_clients()
        async with clients[0] as client:
            hud = client.main_hud
            social_screen = await hud.open_social()

            # 抓取画面
            frame = await client.window.capture()
        ```
    """

    hwnd: HWND
    window: D4Window

    @property
    def main_hud(self) -> MainHUD:
        """获取游戏常驻主界面 (MainHUD) 页面对象。"""
        return MainHUD(window=self.window)

    async def begin_frame(self) -> None:
        """显式触发底层视觉后端捕获并缓存单帧画面。"""
        await self.window.begin_frame()

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
