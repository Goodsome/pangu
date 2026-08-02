"""client_core 通用窗口高级封装 Window。

作为防腐隔离层 (Anti-Corruption Layer)，整合 sys_input 输入模拟、vision_stream 画面捕获、cv_engine 图像与 OCR 识别能力。
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
import sys

import cv2
from cv_engine import (
    IOCREngine,
    ITemplateMatcher,
    MatLike,
)
from sys_input import (
    HWND,
    InputBackend,
    MouseButton,
    VirtualKeyCode,
    Win32HardwareBackend,
)
from vision_stream import (
    IWindowVisionBackend,
)

from client_core.models import (
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
    RelativePoint,
    RelativeRegion,
)


def activate_window(hwnd: HWND) -> None:
    """Win32 API 置顶并激活指定 HWND 窗口。"""
    if sys.platform != "win32" or not hwnd:
        return
    import ctypes

    user32 = ctypes.windll.user32
    # SW_RESTORE = 9, SW_SHOW = 5
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)


def client_to_screen(hwnd: HWND, point: Point) -> Point:
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
class Window:
    """通用应用/游戏窗口与视听/输入控制大管家 (全异步门面封装)。"""

    input_backend: InputBackend
    vision_backend: IWindowVisionBackend
    template_matcher: ITemplateMatcher
    ocr_engine: IOCREngine
    width: int
    height: int
    hwnd: HWND = 0
    title: str = ""

    def activate(self) -> None:
        """激活并将当前窗口置顶前台。"""
        if self.hwnd:
            activate_window(self.hwnd)

    def _resolve_region(self, region: Region | RelativeRegion | None) -> Region | None:
        """解析并统一 Region。

        若传入的区域为 RelativeRegion (0.0 ~ 1.0 的相对比例)，
        则结合当前窗口物理尺寸 (width, height) 自动转换为绝对像素坐标 Region。
        """
        if region is None:
            return None
        if isinstance(region, RelativeRegion):
            return region.to_absolute(
                window_width=self.width, window_height=self.height
            )
        return region

    def _resolve_point(self, point: Point | RelativePoint | None) -> Point | None:
        """解析并统一 Point。

        若传入的点坐标为 RelativePoint (0.0 ~ 1.0 的相对比例)，
        则结合当前窗口物理尺寸 (width, height) 自动转换为绝对像素坐标 Point。
        """
        if point is None:
            return None
        if isinstance(point, RelativePoint):
            return point.to_absolute(
                window_width=self.width, window_height=self.height
            )
        return point

    # ---------------------------------------------------------------------------
    # 画面捕获与帧缓存控制
    # ---------------------------------------------------------------------------
    async def begin_frame(self) -> None:
        """显式触发底层视觉后端捕获并缓存单帧画面。"""
        await self.vision_backend.begin_frame()

    async def capture(
        self, region: Region | RelativeRegion | None = None
    ) -> ImageFrame:
        """捕获窗口当前画面。"""
        abs_region = self._resolve_region(region)
        vision_roi = abs_region.to_vision_stream() if abs_region else None
        res = await self.vision_backend.capture(region=vision_roi)
        return ImageFrame.from_vision_stream(res)

    # ---------------------------------------------------------------------------
    # 图像模板匹配
    # ---------------------------------------------------------------------------
    async def match_template(
        self,
        template: Path | str | MatLike,
        threshold: float = 0.8,
        roi: Region | RelativeRegion | None = None,
    ) -> MatchResult | None:
        """异步从当前画面中进行单目标模板匹配 (极速局部捕获)。"""
        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
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
        template: Path | str | MatLike,
        threshold: float = 0.8,
        roi: Region | RelativeRegion | None = None,
        nms_threshold: float = 0.3,
    ) -> list[MatchResult]:
        """异步从当前画面中匹配全部目标 (极速局部捕获，含 NMS 去重)。"""
        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
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
    # OCR 文本识别与定位
    # ---------------------------------------------------------------------------
    async def ocr(
        self,
        confidence_threshold: float = 0.5,
        roi: Region | RelativeRegion | None = None,
    ) -> list[OcrResult]:
        """异步对当前画面进行文字识别与坐标定位 (极速局部捕获)。"""
        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
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
        """异步在当前画面中检索特定的目标文字 (极速局部捕获)。"""
        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
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
    # 组合交互操作 (Match & Click / Find Text & Click)
    # ---------------------------------------------------------------------------
    async def match_and_click(
        self,
        template: Path | str | MatLike,
        threshold: float = 0.8,
        roi: Region | RelativeRegion | None = None,
        button: MouseButton = MouseButton.LEFT,
    ) -> bool:
        """匹配模板成功后异步点击对应中心坐标。"""
        match = await self.match_template(
            template=template, threshold=threshold, roi=roi
        )
        if match is None:
            return False

        await self.mouse_click(point=match.center, button=button)
        return True

    async def find_text_and_click(
        self,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | RelativeRegion | None = None,
        button: MouseButton = MouseButton.LEFT,
    ) -> bool:
        """检索识别特定文本成功后异步点击其中心位置。"""
        res = await self.find_text(
            target_text=target_text,
            confidence_threshold=confidence_threshold,
            exact_match=exact_match,
            roi=roi,
        )
        if res is None:
            return False

        await self.mouse_click(point=res.center, button=button)
        return True

    # ---------------------------------------------------------------------------
    # 输入模拟异步代理
    # ---------------------------------------------------------------------------
    async def mouse_move(self, point: Point | RelativePoint) -> None:
        """异步移动光标到相对窗口的指定像素或相对比例位置。"""
        abs_point = self._resolve_point(point)
        if abs_point is None:
            return
        target_pt = abs_point
        if isinstance(self.input_backend, Win32HardwareBackend):
            target_pt = client_to_screen(self.hwnd, abs_point)
        await self.input_backend.mouse_move(target_pt.to_sys_input())

    async def mouse_click(
        self,
        point: Point | RelativePoint | None = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval_ms: int = 0,
    ) -> None:
        """异步在窗口指定位置点击鼠标。"""
        abs_point = self._resolve_point(point)
        ipt = None
        if abs_point is not None:
            target_pt = abs_point
            if isinstance(self.input_backend, Win32HardwareBackend):
                target_pt = client_to_screen(self.hwnd, abs_point)
            ipt = target_pt.to_sys_input()

        await self.input_backend.mouse_click(
            point=ipt,
            button=button,
            clicks=clicks,
            interval_ms=interval_ms,
        )

    async def mouse_down(
        self,
        point: Point | RelativePoint | None = None,
        button: MouseButton = MouseButton.LEFT,
    ) -> None:
        """异步在窗口指定位置按下鼠标按键。"""
        abs_point = self._resolve_point(point)
        ipt = None
        if abs_point is not None:
            target_pt = abs_point
            if isinstance(self.input_backend, Win32HardwareBackend):
                target_pt = client_to_screen(self.hwnd, abs_point)
            ipt = target_pt.to_sys_input()

        await self.input_backend.mouse_down(point=ipt, button=button)

    async def mouse_up(
        self,
        point: Point | RelativePoint | None = None,
        button: MouseButton = MouseButton.LEFT,
    ) -> None:
        """异步在窗口指定位置抬起鼠标按键。"""
        abs_point = self._resolve_point(point)
        ipt = None
        if abs_point is not None:
            target_pt = abs_point
            if isinstance(self.input_backend, Win32HardwareBackend):
                target_pt = client_to_screen(self.hwnd, abs_point)
            ipt = target_pt.to_sys_input()

        await self.input_backend.mouse_up(point=ipt, button=button)

    async def key_press(
        self, vk_code: VirtualKeyCode | int, duration_sec: float = 0.05
    ) -> None:
        """异步模拟按键按下并在指定秒后抬起。"""
        await self.input_backend.key_down(vk_code)
        if duration_sec > 0:
            await asyncio.sleep(duration_sec)
        await self.input_backend.key_up(vk_code)

    async def scroll(
        self, amount: int, point: Point | RelativePoint | None = None
    ) -> None:
        """异步模拟滚轮滚动。"""
        abs_point = self._resolve_point(point)
        ipt = None
        if abs_point is not None:
            target_pt = abs_point
            if isinstance(self.input_backend, Win32HardwareBackend):
                target_pt = client_to_screen(self.hwnd, abs_point)
            ipt = target_pt.to_sys_input()

        await self.input_backend.scroll(amount=amount, point=ipt)

    # ---------------------------------------------------------------------------
    # 手动 ROI 选区与拖拽交互 (OpenCV 选区器)
    # ---------------------------------------------------------------------------
    async def select_roi(
        self,
        window_name: str = "Select ROI (Press ENTER/SPACE to confirm, ESC/c to cancel)",
        image: ImageFrame | None = None,
    ) -> Region | None:
        """捕获/使用指定画面并弹出 OpenCV GUI 交互窗口，允许用户手动拖拽框选 ROI 区域。

        Args:
            window_name: 弹出交互窗口的标题栏名称。
            image: 可选。显式传入要框选的图像帧，若未传入则自动捕获当前窗口画面。

        Returns:
            Region | None: 用户确定的绝对像素坐标 Region。若取消框选或无效选区则返回 None。
        """
        frame = image if image is not None else await self.capture()
        img = frame.mat

        def _do_select() -> tuple[int, int, int, int]:
            rect = cv2.selectROI(window_name, img, showCrosshair=True, fromCenter=False)
            cv2.destroyWindow(window_name)
            return (int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))

        rect = await asyncio.to_thread(_do_select)
        x, y, w, h = rect
        if w <= 0 or h <= 0:
            return None

        return Region(x=int(x), y=int(y), width=int(w), height=int(h))

    async def select_relative_roi(
        self,
        window_name: str = "Select Relative ROI (Press ENTER/SPACE to confirm, ESC/c to cancel)",
        image: ImageFrame | None = None,
    ) -> RelativeRegion | None:
        """捕获/使用指定画面，弹窗供用户手动拖拽框选，并自动转换为 0.0~1.0 比例的相对 ROI。

        Args:
            window_name: 弹出交互窗口的标题栏名称。
            image: 可选。显式传入要框选的图像帧，若未传入则自动捕获当前窗口画面。

        Returns:
            RelativeRegion | None: 计算获取的 RelativeRegion。若取消框选则返回 None。
        """
        abs_region = await self.select_roi(window_name=window_name, image=image)
        if abs_region is None:
            return None

        return RelativeRegion.from_absolute(
            region=abs_region,
            window_width=self.width,
            window_height=self.height,
        )

    async def close(self) -> None:
        """异步关闭并清理画面捕获与底层句柄资源。"""
        if hasattr(self.vision_backend, "close"):
            await self.vision_backend.close()


BaseWindow = Window
