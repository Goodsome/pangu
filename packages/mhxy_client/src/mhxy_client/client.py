"""梦幻西游 SDK 聚合根与门面入口 MhxyClient。

向下屏蔽底层 sys_input, vision_stream, cv_engine 组装细节；
向上向 Automation / Robot 业务层提供强类型的 POM 页面与窗口操控入口。
"""

from dataclasses import dataclass
from functools import cached_property
from types import TracebackType
from typing import Self

from client_core import Window
from mhxy_client.models import MHXY_TITLE_PATTERN
from mhxy_client.screens.main_hud import MainHUD
from sys_input import HWND


@dataclass
class MhxyClient:
    """梦幻西游 SDK 聚合根与门面 Client。

    示例:
        ```python
        from mhxy_client import RelativeRegion, create_mhxy_client_by_index

        client = create_mhxy_client_by_index(0, init_cv_engines=True)
        print(f"服务器: {client.server_name}, 角色名: {client.role_name}, ID: {client.role_id}")
        async with client:
            hud = client.main_hud
            inventory = await hud.open_inventory()
        ```
    """

    hwnd: HWND
    window: Window

    @cached_property
    def main_hud(self) -> MainHUD:
        """获取游戏常驻主界面 (MainHUD) 页面对象。"""
        return MainHUD(window=self.window)

    @property
    def title(self) -> str:
        """获取底层关联游戏窗口的真实标题。"""
        return self.window.title

    @property
    def server_name(self) -> str:
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("server").strip() if m else ""

    @property
    def role_name(self) -> str:
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_name").strip() if m else ""

    @property
    def role_id(self) -> str:
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_id").strip() if m else ""

    def activate(self) -> None:
        """置顶并将当前游戏窗口激活到前台。"""
        self.window.activate()

    async def begin_frame(self) -> None:
        """显式触发底层视觉后端捕获并缓存单帧画面。"""
        await self.window.begin_frame()

    async def close(self) -> None:
        """释放底层图形设备与资源。"""
        await self.window.close()

    # ---------------------------------------------------------------------------
    # 异步上下文管理器 (async with MhxyClient(...) as client)
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
