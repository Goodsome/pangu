"""POM (Page Object Model) 模型层基础屏幕与面板抽象。

提供 AutoCalibratingScreen 自动校准基类，封装 UI 元素自动寻址与位置缓存能力。
"""

import asyncio
from dataclasses import dataclass, field
import logging
from pathlib import Path

from d4_client.models import Point, Region
from d4_client.window import D4Window

logger = logging.getLogger(__name__)


@dataclass
class AutoCalibratingScreen:
    """所有游戏 UI 屏幕与面板的自动校准基类。"""

    window: D4Window
    screen_name: str = "BaseScreen"

    # UI 元素绝对坐标缓存
    _element_cache: dict[str, Region | Point] = field(
        default_factory=dict, init=False, repr=False
    )

    async def is_visible(self) -> bool:
        """判断当前页面/屏幕是否处于可见/激活状态。

        子类应重写此方法，通过特征模板或关键文本识别页面状态。
        """
        return True

    async def wait_until_visible(
        self, timeout_sec: float = 5.0, poll_interval_sec: float = 0.2
    ) -> bool:
        """异步轮询等待直到该页面处于可见就绪状态。

        使用 asyncio 事件循环高精度单调时钟进行超时控制。

        Args:
            timeout_sec: 超时时间 (秒)
            poll_interval_sec: 轮询时间间隔 (秒)

        Returns:
            bool: 页面就绪返回 True，超时返回 False
        """
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_sec

        while loop.time() < deadline:
            if await self.is_visible():
                return True
            await asyncio.sleep(poll_interval_sec)

        logger.warning("[%s] 等待页面可见超时 (%ss)", self.screen_name, timeout_sec)
        return False

    async def find_element_by_text(
        self,
        element_key: str,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | None = None,
        use_cache: bool = True,
    ) -> Region | None:
        """通过文本定位 UI 元素位置（支持缓存）。"""
        if use_cache and element_key in self._element_cache:
            cached = self._element_cache[element_key]
            if isinstance(cached, Region):
                return cached

        res = await self.window.find_text(
            target_text=target_text,
            confidence_threshold=confidence_threshold,
            exact_match=exact_match,
            roi=roi,
        )

        if res is not None:
            if use_cache:
                self._element_cache[element_key] = res.rect
            return res.rect

        return None

    async def find_element_by_template(
        self,
        element_key: str,
        template: Path | str,
        threshold: float = 0.8,
        roi: Region | None = None,
        use_cache: bool = True,
    ) -> Region | None:
        """通过图像模板定位 UI 元素位置（支持缓存）。"""
        if use_cache and element_key in self._element_cache:
            cached = self._element_cache[element_key]
            if isinstance(cached, Region):
                return cached

        res = await self.window.match_template(
            template=template,
            threshold=threshold,
            roi=roi,
        )

        if res is not None:
            if use_cache:
                self._element_cache[element_key] = res.rect
            return res.rect

        return None

    async def click_element(
        self,
        element_key: str,
        target_text_or_template: str | Path,
        roi: Region | None = None,
        use_cache: bool = True,
    ) -> bool:
        """定位特定 UI 元素并进行鼠标点击。"""
        rect: Region | None = None

        if isinstance(target_text_or_template, Path):
            rect = await self.find_element_by_template(
                element_key=element_key,
                template=target_text_or_template,
                roi=roi,
                use_cache=use_cache,
            )
        else:
            rect = await self.find_element_by_text(
                element_key=element_key,
                target_text=target_text_or_template,
                roi=roi,
                use_cache=use_cache,
            )

        if rect is None:
            logger.warning("[%s] 尝试点击元素 [%s] 失败: 未定位到目标", self.screen_name, element_key)
            return False

        await self.window.mouse_click(point=rect.center)
        return True

    def clear_cache(self) -> None:
        """清理已缓存在内存中的 UI 元素坐标。"""
        self._element_cache.clear()
