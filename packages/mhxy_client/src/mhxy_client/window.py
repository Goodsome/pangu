"""梦幻西游 游戏窗口高级封装类 MhxyWindow。

作为防腐隔离层 (Anti-Corruption Layer)，整合 sys_input 输入模拟、vision_stream 画面捕获、cv_engine 图像与 OCR 引擎能力。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any

from mhxy_client.models import (
    MHXY_TITLE_PATTERN,
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
    RelativeRegion,
)
from sys_input import (
    HWND,
    InputBackend,
    MouseButton,
    VirtualKeyCode,
    Win32HardwareBackend,
)
from vision_stream import IWindowVisionBackend

if TYPE_CHECKING:
    from cv_engine.interfaces import IOCREngine, ITemplateMatcher


def _activate_window(hwnd: HWND) -> None:
    """Win32 API 置顶并激活指定 HWND 窗口。"""
    if sys.platform != "win32" or not hwnd:
        return
    import ctypes

    user32 = ctypes.windll.user32
    # SW_RESTORE = 9, SW_SHOW = 5
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)


def _client_to_screen(hwnd: HWND, point: Point) -> Point:
    """Win32 API 将窗口客户区相对坐标转换为屏幕绝对坐标。"""
    if sys.platform != "win32" or not hwnd:
        return point
    import ctypes
    from ctypes import wintypes

    pt = wintypes.POINT(point.x, point.y)
    user32 = ctypes.windll.user32
    user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return Point(x=pt.x, y=pt.y)


@dataclass
class MhxyWindow:
    """梦幻西游 游戏窗口控制管理类 (MhxyWindow)。"""

    hwnd: HWND = 0
    input_backend: InputBackend | None = None
    vision_backend: IWindowVisionBackend | None = None
    template_matcher: ITemplateMatcher | None = None
    ocr_engine: IOCREngine | None = None
    width: int = 0
    height: int = 0
    title: str = ""

    @property
    def server_name(self) -> str:
        """从窗口标题提取的大区/服务器名字 (如 '畅玩服[天下无双]')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("server").strip() if m else ""

    @property
    def role_name(self) -> str:
        """从窗口标题提取的游戏角色名字 (如 '游易幽寒')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_name").strip() if m else ""

    @property
    def role_id(self) -> str:
        """从窗口标题提取的游戏角色 ID (如 '39200278')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_id").strip() if m else ""

    def activate(self) -> None:
        """激活并将当前游戏窗口置顶前台。"""
        if self.hwnd:
            _activate_window(self.hwnd)

    def _resolve_region(self, region: Region | RelativeRegion | None) -> Region | None:
        """解析并统一 Region。"""
        if region is None:
            return None
        if isinstance(region, RelativeRegion):
            return region.to_absolute(
                window_width=self.width, window_height=self.height
            )
        return region

    async def begin_frame(self) -> None:
        """显式触发底层视觉后端捕获并缓存单帧画面。"""
        if self.vision_backend:
            await self.vision_backend.begin_frame()

    async def capture(
        self, region: Region | RelativeRegion | None = None
    ) -> ImageFrame:
        """捕获游戏窗口画面 (支持绝对 Region 或相对 RelativeRegion 精准切片)。"""
        if self.vision_backend:
            abs_region = self._resolve_region(region)
            # 抓取完整帧后使用 NumPy 精准裁剪，彻底解决显存映射跨 stride 切片导致的错位偏移
            res = await self.vision_backend.capture(region=None)
            full_frame = ImageFrame.from_vision_stream(res)
            return full_frame.crop(abs_region) if abs_region else full_frame
        return ImageFrame()

    # ---------------------------------------------------------------------------
    # OCR 文本识别与定位
    # ---------------------------------------------------------------------------
    async def ocr(
        self,
        confidence_threshold: float = 0.5,
        roi: Region | RelativeRegion | None = None,
    ) -> list[OcrResult]:
        """异步对当前游戏窗口/指定 ROI 区域进行文字识别与坐标定位。"""
        if self.ocr_engine is None:
            return []

        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
        if frame.mat is None:
            return []

        offset_x = abs_roi.x if abs_roi else 0
        offset_y = abs_roi.y if abs_roi else 0

        results = await self.ocr_engine.async_ocr(
            scene=frame.mat,
            confidence_threshold=confidence_threshold,
            roi=None,
        )
        return [
            OcrResult.from_cv_engine(r, offset_x=offset_x, offset_y=offset_y)
            for r in results
        ]

    async def find_text(
        self,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | RelativeRegion | None = None,
    ) -> OcrResult | None:
        """异步在当前游戏窗口中检索特定的目标文字。"""
        if self.ocr_engine is None:
            return None

        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
        if frame.mat is None:
            return None

        offset_x = abs_roi.x if abs_roi else 0
        offset_y = abs_roi.y if abs_roi else 0

        res = await self.ocr_engine.async_find_text(
            scene=frame.mat,
            target_text=target_text,
            confidence_threshold=confidence_threshold,
            exact_match=exact_match,
            roi=None,
        )
        return (
            OcrResult.from_cv_engine(res, offset_x=offset_x, offset_y=offset_y)
            if res
            else None
        )

    # ---------------------------------------------------------------------------
    # 模板匹配能力
    # ---------------------------------------------------------------------------
    async def match_template(
        self,
        template: Path | str | Any,
        threshold: float = 0.8,
        roi: Region | RelativeRegion | None = None,
    ) -> MatchResult | None:
        """异步从当前游戏窗口中匹配单目标模板。"""
        if self.template_matcher is None:
            return None

        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
        if frame.mat is None:
            return None

        offset_x = abs_roi.x if abs_roi else 0
        offset_y = abs_roi.y if abs_roi else 0

        res = await self.template_matcher.async_match_best(
            scene=frame.mat,
            template=template,
            threshold=threshold,
            roi=None,
        )
        return (
            MatchResult.from_cv_engine(res, offset_x=offset_x, offset_y=offset_y)
            if res
            else None
        )

    async def match_template_multi(
        self,
        template: Path | str | Any,
        threshold: float = 0.8,
        roi: Region | RelativeRegion | None = None,
        nms_threshold: float = 0.3,
    ) -> list[MatchResult]:
        """异步从当前游戏窗口中匹配全部多目标模板。"""
        if self.template_matcher is None:
            return []

        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
        if frame.mat is None:
            return []

        offset_x = abs_roi.x if abs_roi else 0
        offset_y = abs_roi.y if abs_roi else 0

        results = await self.template_matcher.async_match_multi(
            scene=frame.mat,
            template=template,
            threshold=threshold,
            roi=None,
            nms_threshold=nms_threshold,
        )
        return [
            MatchResult.from_cv_engine(r, offset_x=offset_x, offset_y=offset_y)
            for r in results
        ]

    # ---------------------------------------------------------------------------
    # 输入模拟与窗口操控方法 (代理底层 InputBackend)
    # ---------------------------------------------------------------------------
    async def mouse_move(self, point: Point) -> None:
        """异步移动鼠标光标到相对窗口的指定像素位置。"""
        if self.input_backend:
            target_pt = point
            if isinstance(self.input_backend, Win32HardwareBackend):
                self.activate()
                target_pt = _client_to_screen(self.hwnd, point)
            await self.input_backend.mouse_move(target_pt.to_sys_input())

    async def mouse_click(
        self,
        point: Point | None = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval_ms: int = 0,
    ) -> None:
        """异步在窗口指定位置点击鼠标。"""
        if self.input_backend:
            ipt = None
            if point is not None:
                target_pt = point
                if isinstance(self.input_backend, Win32HardwareBackend):
                    self.activate()
                    target_pt = _client_to_screen(self.hwnd, point)
                ipt = target_pt.to_sys_input()
            elif isinstance(self.input_backend, Win32HardwareBackend):
                self.activate()

            await self.input_backend.mouse_click(
                point=ipt,
                button=button,
                clicks=clicks,
                interval_ms=interval_ms,
            )

    async def key_press(
        self, vk_code: VirtualKeyCode | int, duration_sec: float = 0.05
    ) -> None:
        """异步模拟按键按下并在指定秒数后抬起。"""
        if self.input_backend:
            if isinstance(self.input_backend, Win32HardwareBackend):
                self.activate()
            await self.input_backend.key_down(vk_code)
            if duration_sec > 0:
                await asyncio.sleep(duration_sec)
            await self.input_backend.key_up(vk_code)

    async def scroll(self, amount: int, point: Point | None = None) -> None:
        """异步模拟滚轮滚动。"""
        if self.input_backend:
            ipt = None
            if point is not None:
                target_pt = point
                if isinstance(self.input_backend, Win32HardwareBackend):
                    self.activate()
                    target_pt = _client_to_screen(self.hwnd, point)
                ipt = target_pt.to_sys_input()
            await self.input_backend.scroll(amount=amount, point=ipt)

    async def close(self) -> None:
        """释放资源。"""
        if self.vision_backend and hasattr(self.vision_backend, "close"):
            await self.vision_backend.close()
