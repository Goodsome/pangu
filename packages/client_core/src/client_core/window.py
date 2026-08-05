"""client_core 通用窗口高级封装 Window。

作为防腐隔离层 (Anti-Corruption Layer)，整合 sys_input 输入模拟、vision_stream 画面捕获、cv_engine 图像与 OCR 识别能力。
"""

import logging
import asyncio
import random
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

logger = logging.getLogger(__name__)


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


def get_cursor_pos() -> Point:
    """Win32 API 获取当前系统鼠标指针在屏幕上的绝对物理像素坐标。"""
    if sys.platform != "win32":
        return Point(0, 0)
    import ctypes
    from ctypes import wintypes

    pt = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return Point(x=int(pt.x), y=int(pt.y))


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

    def resolve_point(self, point: Point | RelativePoint | None) -> Point | None:
        """解析并统一 Point。

        若传入的点坐标为 RelativePoint (0.0 ~ 1.0 的相对比例)，
        则结合当前窗口物理尺寸 (width, height) 自动转换为绝对像素坐标 Point。
        """
        if point is None:
            return None
        if isinstance(point, RelativePoint):
            return point.to_absolute(window_width=self.width, window_height=self.height)
        return point

    # ---------------------------------------------------------------------------
    # 画面捕获与帧缓存控制
    # ---------------------------------------------------------------------------
    async def begin_frame(self) -> None:
        """显式触发底层视觉后端捕获并缓存单帧画面。"""
        await self.vision_backend.begin_frame()

    async def capture(
        self,
        region: Region | RelativeRegion | None = None,
        refresh: bool = False,
    ) -> ImageFrame:
        """捕获窗口当前画面。"""
        abs_region = self._resolve_region(region)
        vision_roi = abs_region.to_vision_stream() if abs_region else None
        if refresh:
            await self.vision_backend.begin_frame()
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

    async def match_template_masked(
        self,
        template: Path,
        threshold: float = 0.8,
        roi: Region | RelativeRegion | None = None,
    ) -> MatchResult | None:
        """异步从当前画面中进行单目标模板匹配 (极速局部捕获)。"""
        abs_roi = self._resolve_region(roi)
        frame = await self.capture(region=abs_roi)
        offset_x = abs_roi.x if abs_roi else 0
        offset_y = abs_roi.y if abs_roi else 0

        res = self.template_matcher.match_masked_template(
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
    def get_sys_cursor_client_pos(self) -> Point | None:
        """获取当前系统物理鼠标指针在窗口客户区中的相对坐标 Point。"""
        if not self.hwnd:
            return None
        try:
            valid_hwnd = int(self.hwnd)
            if valid_hwnd == 0:
                return None
        except ValueError, TypeError:
            return None

        sys_screen_pos = get_cursor_pos()
        client_origin_screen = client_to_screen(valid_hwnd, Point(x=0, y=0))
        return Point(
            x=sys_screen_pos.x - client_origin_screen.x,
            y=sys_screen_pos.y - client_origin_screen.y,
        )

    async def ensure_cursor_in_window(self) -> Point:
        """检查系统物理鼠标是否在窗口客户区内。若不在，先将其平滑/直接移动至窗口中心。"""
        win_w = getattr(self, "width", 800)
        win_h = getattr(self, "height", 600)
        win_w = win_w if isinstance(win_w, int) and win_w > 0 else 800
        win_h = win_h if isinstance(win_h, int) and win_h > 0 else 600

        sys_client_pos = self.get_sys_cursor_client_pos()
        if (
            sys_client_pos is not None
            and 0 <= sys_client_pos.x <= win_w
            and 0 <= sys_client_pos.y <= win_h
        ):
            return sys_client_pos

        center_point = Point(x=win_w // 2, y=win_h // 2)
        logger.info(
            "[Window] ⚠️ 系统鼠标不在窗口客户区内 (%s)，先移动至窗口中心 %s",
            sys_client_pos,
            center_point,
        )
        await self.mouse_move(point=center_point)
        await asyncio.sleep(0.1)
        new_pos = self.get_sys_cursor_client_pos()
        return new_pos if new_pos is not None else center_point

    async def mouse_move(self, point: Point | RelativePoint) -> None:
        """异步移动光标到相对窗口的指定像素或相对比例位置。"""
        abs_point = self.resolve_point(point)
        if abs_point is None:
            return
        target_pt = abs_point
        if isinstance(self.input_backend, Win32HardwareBackend):
            target_pt = client_to_screen(self.hwnd, abs_point)
        await self.input_backend.mouse_move(target_pt.to_sys_input())

    async def mouse_move_relative(self, dx: int, dy: int) -> None:
        """异步委托底层 input_backend 相对移动鼠标光标指定偏移量 (dx, dy)。

        Args:
            dx: X 轴相对偏移像素量（正数向右，负数向左）。
            dy: Y 轴相对偏移像素量（正数向下，负数向上）。
        """
        await self.input_backend.mouse_move_relative(dx, dy)

    async def bell_move_steps(
        self,
        start: Point,
        target: Point,
        steps: int,
        duration_sec: float,
    ) -> None:
        """从 start 到 target (客户区坐标) 按 ease-in-out 钟形分步移动。

        在客户区坐标空间从真实起点 start 插值至 target，每步调用原生 mouse_move
        (由 mouse_move 统一处理 hardware 后端的 client->screen 转换)，后端无关。
        采用 smoothstep 钟形速度曲线 (起停慢、中段快) 并叠加轻微时间抖动。

        Args:
            start: 起点客户区坐标。
            target: 终点客户区坐标。
            steps: 插值步数。
            duration_sec: 移动总耗时 (秒)。
        """
        if steps <= 1:
            await self.mouse_move(target)
            return

        interval = duration_sec / steps
        for i in range(1, steps + 1):
            r = i / steps
            # ease-in-out (smoothstep): 起停慢、中段快，近似最小急动度轨迹
            eased = 3 * r * r - 2 * r * r * r
            cur = Point(
                x=int(start.x + (target.x - start.x) * eased),
                y=int(start.y + (target.y - start.y) * eased),
            )
            await self.mouse_move(cur)
            # 轻微时间抖动 (±15%) 消除等间隔机械感
            jitter = interval * random.uniform(-0.15, 0.15)
            await asyncio.sleep(max(0.0, interval + jitter))

    async def smooth_mouse_move(
        self,
        point: Point | RelativePoint,
        steps: int = 30,
        duration_sec: float = 0.8,
    ) -> None:
        """缓慢/平滑移动鼠标光标至指定目标位置 (避免瞬间跳变引致物理光标震荡或下漂)。

        采用 ease-in-out (smoothstep) 钟形速度曲线 (起停慢、中段快)，近似最小急动度轨迹；
        并在步间叠加轻微时间抖动以消除等间隔机械感，整体更贴近人类鼠标运动。

        Args:
            point: 目标点 (绝对 Point 或相对 RelativePoint)
            steps: 平滑插值步数 (默认 30 步)
            duration_sec: 移动总耗时 (秒，默认 0.8 秒)
        """
        abs_point = self.resolve_point(point)
        if abs_point is None:
            return

        start = self.get_sys_cursor_client_pos() or Point(x=0, y=0)
        await self.bell_move_steps(start, abs_point, steps, duration_sec)

        # 闭环反馈微调校正 (Closed-Loop Correction): 消除长距离移动下的线性缩放与四舍五入积累误差。
        # 在客户区坐标空间闭环，统一走 mouse_move (后端无关)。
        for _ in range(3):
            cur = self.get_sys_cursor_client_pos()
            if cur is None:
                break
            err_x = abs_point.x - cur.x
            err_y = abs_point.y - cur.y
            if abs(err_x) <= 1 and abs(err_y) <= 1:
                break
            await self.mouse_move(Point(x=cur.x + err_x, y=cur.y + err_y))
            await asyncio.sleep(0.03)

    async def mouse_click(
        self,
        point: Point | RelativePoint | None = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval_ms: int = 0,
    ) -> None:
        """异步在窗口指定位置点击鼠标。"""
        abs_point = self.resolve_point(point)
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
        abs_point = self.resolve_point(point)
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
        abs_point = self.resolve_point(point)
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
        abs_point = self.resolve_point(point)
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
