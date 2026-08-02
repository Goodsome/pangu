"""梦幻西游 SDK 聚合根与门面入口 MhxyClient。

向下屏蔽底层 sys_input, vision_stream, cv_engine 组装细节；
向上向 Automation / Robot 业务层提供强类型的 POM 页面与窗口操控入口。
"""

from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Self

from client_core import (
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
    RelativeRegion,
    Window,
)
from mhxy_client.models import MHXY_TITLE_PATTERN
from sys_input import HWND, MouseButton, VirtualKeyCode


@dataclass
class MhxyClient:
    """梦幻西游 SDK 聚合根与门面 Client。

    示例:
        ```python
        from mhxy_client import RelativeRegion, create_mhxy_client_by_index

        client = create_mhxy_client_by_index(0, init_cv_engines=True)
        print(f"服务器: {client.server_name}, 角色名: {client.role_name}, ID: {client.role_id}")
        async with client:
            center_roi = RelativeRegion(x=0.25, y=0.25, width=0.5, height=0.5)
            ocr_results = await client.ocr(roi=center_roi)
        ```
    """

    hwnd: HWND
    window: Window

    @property
    def title(self) -> str:
        """获取底层关联游戏窗口的真实标题。"""
        return self.window.title

    @property
    def server_name(self) -> str:
        """获取关联游戏角色的大区/服务器名称 (如 '畅玩服[天下无双]')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("server").strip() if m else ""

    @property
    def role_name(self) -> str:
        """获取关联游戏角色的名字 (如 '游易幽寒')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_name").strip() if m else ""

    @property
    def role_id(self) -> str:
        """获取关联游戏角色的 ID (如 '39200278')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_id").strip() if m else ""

    def activate(self) -> None:
        """置顶并将当前游戏窗口激活到前台。"""
        self.window.activate()

    async def begin_frame(self) -> None:
        """显式触发底层视觉后端捕获并缓存单帧画面。"""
        await self.window.begin_frame()

    async def capture(
        self, region: Region | RelativeRegion | None = None
    ) -> ImageFrame:
        """快捷代理：捕获窗口画面。"""
        return await self.window.capture(region=region)

    # ---------------------------------------------------------------------------
    # OCR 与模板匹配能力代理
    # ---------------------------------------------------------------------------
    async def ocr(
        self,
        confidence_threshold: float = 0.5,
        roi: Region | RelativeRegion | None = None,
    ) -> list[OcrResult]:
        """快捷代理：异步进行 OCR 文字识别。"""
        return await self.window.ocr(confidence_threshold=confidence_threshold, roi=roi)

    async def find_text(
        self,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | RelativeRegion | None = None,
    ) -> OcrResult | None:
        """快捷代理：异步检索目标文本。"""
        return await self.window.find_text(
            target_text=target_text,
            confidence_threshold=confidence_threshold,
            exact_match=exact_match,
            roi=roi,
        )

    async def match_template(
        self,
        template: Path | str | Any,
        threshold: float = 0.8,
        roi: Region | RelativeRegion | None = None,
    ) -> MatchResult | None:
        """快捷代理：单目标模板匹配。"""
        return await self.window.match_template(
            template=template, threshold=threshold, roi=roi
        )

    async def match_template_multi(
        self,
        template: Path | str | Any,
        threshold: float = 0.8,
        roi: Region | RelativeRegion | None = None,
        nms_threshold: float = 0.3,
    ) -> list[MatchResult]:
        """快捷代理：多目标模板匹配。"""
        return await self.window.match_template_multi(
            template=template,
            threshold=threshold,
            roi=roi,
            nms_threshold=nms_threshold,
        )

    # ---------------------------------------------------------------------------
    # 输入模拟代理
    # ---------------------------------------------------------------------------
    async def mouse_move(self, point: Point) -> None:
        """快捷代理：异步移动鼠标光标。"""
        await self.window.mouse_move(point=point)

    async def mouse_click(
        self,
        point: Point | None = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval_ms: int = 0,
    ) -> None:
        """快捷代理：异步鼠标点击。"""
        await self.window.mouse_click(
            point=point,
            button=button,
            clicks=clicks,
            interval_ms=interval_ms,
        )

    async def key_press(
        self, vk_code: VirtualKeyCode | int, duration_sec: float = 0.05
    ) -> None:
        """快捷代理：异步模拟按键按下与抬起。"""
        await self.window.key_press(vk_code=vk_code, duration_sec=duration_sec)

    async def scroll(self, amount: int, point: Point | None = None) -> None:
        """快捷代理：异步滚轮滚动。"""
        await self.window.scroll(amount=amount, point=point)

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
