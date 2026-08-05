"""client_core POM (Page Object Model) 模型层基础屏幕与面板抽象。

提供 AutoCalibratingScreen 自动校准基类，封装 UI 元素自动寻址与位置缓存能力。
"""

import asyncio
from dataclasses import dataclass
import logging
from typing import ClassVar

from client_core.models import Element, Point, Region, RelativePoint, RelativeRegion
from client_core.window import Window

logger = logging.getLogger(__name__)


@dataclass
class AutoCalibratingScreen:
    """所有应用/游戏 UI 屏幕与面板的自动校准基类。"""

    window: Window
    screen_name: str = "BaseScreen"
    is_visible: bool = False

    _element_cache: ClassVar[dict[str, Element]] = {}

    def __init_subclass__(cls) -> None:
        cls._element_cache = {}

    async def check_visible(self) -> bool:
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
            await self.window.begin_frame()
            self.is_visible = await self.check_visible()
            if self.is_visible:
                return True
            await asyncio.sleep(poll_interval_sec)

        logger.warning("[%s] 等待页面可见超时 (%ss)", self.screen_name, timeout_sec)
        return False

    async def locate_element(
        self,
        element_key: str,
        target_text: str,
        roi: Region | RelativeRegion | None = None,
        is_element_fixed: bool = True,
    ) -> Element | None:
        """定位特定 UI 元素。

        优先基于内存缓存的特征图片执行极速模板匹配；
        未命中缓存时回退至基于 OCR 文本的精确定位，并自动截取该元素特征存入缓存。
        """
        
        cached = self._element_cache.get(element_key)
        
        if is_element_fixed and cached:
            return cached
            
        if cached:
            if roi is None:
                roi = cached.region
            res = await self.window.match_template(
                template=cached.image.mat,
                roi=roi,
            )
        else:
            res = await self.window.find_text(
                target_text=target_text,
                roi=roi,
            )

        if res is None:
            return None

        image = await self.window.capture(res.rect)
        cached = Element(
            name=element_key,
            region=res.rect,
            image=image,
        )
        self._element_cache[element_key] = cached
        return cached

    async def click_element(
        self,
        element_key: str,
        target_text: str,
        roi: Region | RelativeRegion | None = None,
        is_element_fixed: bool = False,
    ) -> bool:
        """定位特定 UI 元素并进行鼠标点击。"""

        element = await self.locate_element(
            element_key=element_key,
            target_text=target_text,
            roi=roi,
            is_element_fixed=is_element_fixed
        )

        if element is None:
            logger.warning(
                "[%s] 尝试点击元素 [%s] 失败: 未定位到目标",
                self.screen_name,
                element_key,
            )
            return False

        await self.window.mouse_click(point=element.region.center)
        return True

    def clear_cache(self) -> None:
        """清理已缓存在内存中的 UI 元素坐标。"""
        self._element_cache.clear()
