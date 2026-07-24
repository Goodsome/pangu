"""D4 游戏窗口高级封装类。

作为防腐层 (Anti-Corruption Layer)，整合 sys_input 输入模拟、vision_stream 画面捕获、cv_engine 模板匹配与 PaddleOCR 识别能力。
全线收发 d4_client 领域专有数据模型与异步交互。
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path

from cv_engine import (
    IOCREngine,
    ITemplateMatcher,
    MatLike,
)
from cv_engine.models import Region as CVRegion
from d4_client.models import (
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
)
from sys_input import (
    InputBackend,
    MouseButton,
    VirtualKeyCode,
)
from vision_stream import (
    IWindowVisionBackend,
)


@dataclass
class D4Window:
    """暗黑破坏神 4 游戏窗口与视听/输入控制大管家 (防腐隔离全异步封装)。"""

    input_backend: InputBackend
    vision_backend: IWindowVisionBackend
    template_matcher: ITemplateMatcher
    ocr_engine: IOCREngine

    # ---------------------------------------------------------------------------
    # 画面捕获与帧缓存控制
    # ---------------------------------------------------------------------------
    async def begin_frame(self) -> None:
        """显式触发底层视觉后端捕获并缓存单帧画面。"""
        await self.vision_backend.begin_frame()

    async def capture(self, region: Region | None = None) -> ImageFrame:
        """捕获游戏窗口当前画面。"""
        vision_roi = region.to_vision_stream() if region else None
        res = await self.vision_backend.capture(region=vision_roi)
        return ImageFrame.from_vision_stream(res)

    # ---------------------------------------------------------------------------
    # 图像模板匹配
    # ---------------------------------------------------------------------------
    async def match_template(
        self,
        template: Path | str | MatLike,
        threshold: float = 0.8,
        roi: Region | None = None,
    ) -> MatchResult | None:
        """异步从当前游戏画面中进行单目标模板匹配。"""
        frame = await self.capture(region=roi)
        cv_roi = roi.to_cv_engine() if roi else None

        res = await self.template_matcher.async_match_best(
            scene=frame.data,
            template=template,
            threshold=threshold,
            roi=cv_roi,
        )
        return MatchResult.from_cv_engine(res) if res else None

    async def match_template_multi(
        self,
        template: Path | str | MatLike,
        threshold: float = 0.8,
        roi: Region | None = None,
        nms_threshold: float = 0.3,
    ) -> list[MatchResult]:
        """异步从当前游戏画面中匹配全部目标 (含 NMS 去重)。"""
        frame = await self.capture(region=roi)
        cv_roi = roi.to_cv_engine() if roi else None

        results = await self.template_matcher.async_match_multi(
            scene=frame.data,
            template=template,
            threshold=threshold,
            roi=cv_roi,
            nms_threshold=nms_threshold,
        )
        return [MatchResult.from_cv_engine(r) for r in results]

    # ---------------------------------------------------------------------------
    # OCR 文本识别与定位
    # ---------------------------------------------------------------------------
    async def ocr(
        self,
        confidence_threshold: float = 0.5,
        roi: Region | None = None,
    ) -> list[OcrResult]:
        """异步对当前游戏画面进行文字识别与坐标定位。"""
        frame = await self.capture(region=roi)
        cv_roi: CVRegion | None = roi.to_cv_engine() if roi else None

        results = await self.ocr_engine.async_ocr(
            scene=frame.data,
            confidence_threshold=confidence_threshold,
            roi=cv_roi,
        )
        return [OcrResult.from_cv_engine(r) for r in results]

    async def find_text(
        self,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | None = None,
    ) -> OcrResult | None:
        """异步在当前游戏画面中检索特定的目标文字。"""
        frame = await self.capture(region=roi)
        cv_roi: CVRegion | None = roi.to_cv_engine() if roi else None

        res = await self.ocr_engine.async_find_text(
            scene=frame.data,
            target_text=target_text,
            confidence_threshold=confidence_threshold,
            exact_match=exact_match,
            roi=cv_roi,
        )
        return OcrResult.from_cv_engine(res) if res else None

    # ---------------------------------------------------------------------------
    # 组合交互操作 (Match & Click / Find Text & Click)
    # ---------------------------------------------------------------------------
    async def match_and_click(
        self,
        template: Path | str | MatLike,
        threshold: float = 0.8,
        roi: Region | None = None,
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
        roi: Region | None = None,
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
    async def mouse_move(self, point: Point) -> None:
        """异步移动光标到相对窗口的指定像素位置。"""
        await self.input_backend.mouse_move(point.to_sys_input())

    async def mouse_click(
        self,
        point: Point | None = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval_ms: int = 0,
    ) -> None:
        """异步在窗口指定位置点击鼠标。"""
        ipt = point.to_sys_input() if point else None
        await self.input_backend.mouse_click(
            point=ipt,
            button=button,
            clicks=clicks,
            interval_ms=interval_ms,
        )

    async def key_press(
        self, vk_code: VirtualKeyCode | int, duration_sec: float = 0.05
    ) -> None:
        """异步模拟按键按下并在指定秒后抬起。"""
        await self.input_backend.key_down(vk_code)
        if duration_sec > 0:
            await asyncio.sleep(duration_sec)
        await self.input_backend.key_up(vk_code)

    async def scroll(self, amount: int, point: Point | None = None) -> None:
        """异步模拟滚轮滚动。"""
        ipt = point.to_sys_input() if point else None
        await self.input_backend.scroll(amount=amount, point=ipt)

    async def close(self) -> None:
        """异步关闭并清理画面捕获与底层句柄资源。"""
        if hasattr(self.vision_backend, "close"):
            await self.vision_backend.close()
