from abc import ABC
import asyncio
from dataclasses import dataclass, field
import logging

from pathlib import Path

from client_core import AutoCalibratingScreen, Point, Region
from mhxy_client.config import MainHudLayoutConfig

logger = logging.getLogger(__name__)

_DEFAULT_CURSOR_TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "templates" / "cursor.png"
_DEFAULT_POINTER_TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "templates" / "pointer.png"


@dataclass
class BaseScreen(AutoCalibratingScreen, ABC):

    config: MainHudLayoutConfig = field(default_factory=MainHudLayoutConfig)

    async def _get_cursor_region(self) -> Region:
        sys_client_pos = await self.window.ensure_cursor_in_window()
        radius = 50
        win_w = self.window.width
        win_h = self.window.height

        roi_x = max(0, sys_client_pos.x - radius)
        roi_y = max(0, sys_client_pos.y - radius)
        roi_w = min(win_w - roi_x, radius * 2)
        roi_h = min(win_h - roi_y, radius * 2)
        return Region(x=roi_x, y=roi_y, width=roi_w, height=roi_h)

    async def _get_game_mouse(self) -> tuple[Point | None, bool]:
        """获取游戏鼠标指针位置。"""

        roi = await self._get_cursor_region()
        await self.window.begin_frame()
        pointer_result = await self.window.match_template_masked(
            template=_DEFAULT_POINTER_TEMPLATE_PATH,
            threshold=0.7,
            roi=roi,
        )
        cursor_result = await self.window.match_template_masked(
            template=_DEFAULT_CURSOR_TEMPLATE_PATH,
            threshold=0.7,
            roi=roi,
        )
        if pointer_result is not None and cursor_result is not None:
            if pointer_result.score > cursor_result.score:
                return pointer_result.top_left, True
            return cursor_result.top_left, False
        elif pointer_result is None and cursor_result is not None:
            return cursor_result.top_left, False
        elif pointer_result is not None and cursor_result is None:
            return pointer_result.top_left, True
        else:
            return None, False

    async def _calibrate_and_realign_mouse(
        self,
        target_point: Point,
        tolerance_px: float = 10.0,
    ) -> bool:
        """单次测量游戏鼠标与目标的误差，按偏移量反算绝对像素坐标并移动矫正。

        Returns:
            tuple[Point, float]: (当前游戏鼠标实际位置, 距离目标的像素残差距离)
        """
        sys_client_pos = await self.window.ensure_cursor_in_window()
        game_cursor, is_pointer = await self._get_game_mouse()
        if game_cursor is None:
            raise RuntimeError("未匹配到游戏鼠标模板 cursor.png")
        if is_pointer:
            return True
        offset_x = game_cursor.x - sys_client_pos.x
        offset_y = game_cursor.y - sys_client_pos.y

        dx = float(game_cursor.x - target_point.x)
        dy = float(game_cursor.y - target_point.y)
        dist: float = (dx * dx + dy * dy) ** 0.5

        if dist <= tolerance_px:
            return True

        corrected_target = Point(
            x=target_point.x - offset_x,
            y=target_point.y - offset_y,
        )
        await self.window.smooth_mouse_move(point=corrected_target)
        await asyncio.sleep(0.1)
        return False

    async def mouse_move(
        self,
        target_point: Point,
        max_retries: int = 5,
    ) -> bool:
        _ = await self.window.ensure_cursor_in_window()

        for _ in range(1, max_retries + 1):
            result = await self._calibrate_and_realign_mouse(
                target_point=target_point,
            )
            if result:
                return True

        logger.warning( "达到最大校准重试次数")
        return False

    async def mouse_click(
        self,
        point: Point | None = None,
    ) -> None:
        if point:
            await self.window.smooth_mouse_move(point=point)
            await asyncio.sleep(0.1)
        await self.window.mouse_click()