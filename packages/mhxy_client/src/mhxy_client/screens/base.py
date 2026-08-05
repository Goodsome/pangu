from abc import ABC
import asyncio
from dataclasses import dataclass, field
import logging
import math

from pathlib import Path

from client_core import AutoCalibratingScreen, Point, Region, RelativePoint
from mhxy_client.config import MainHudLayoutConfig

logger = logging.getLogger(__name__)

_DEFAULT_CURSOR_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3] / "templates" / "cursor.png"
)
_DEFAULT_POINTER_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3] / "templates" / "pointer.png"
)

# 校准容差与 CV 沉淀时间：游戏光标滞后系统光标，测量前需沉淀让其追上
_TOLERANCE_PX: float = 10.0
_SETTLE_SEC: float = 0.1


@dataclass
class BaseScreen(AutoCalibratingScreen, ABC):
    config: MainHudLayoutConfig = field(default_factory=MainHudLayoutConfig)

    async def _get_cursor_region(self) -> Region:
        sys_client_pos = self.window.get_sys_cursor_client_pos()
        win_w = self.window.width
        win_h = self.window.height
        if sys_client_pos is None or not (
            0 <= sys_client_pos.x <= win_w and 0 <= sys_client_pos.y <= win_h
        ):
            # 系统光标不在窗口客户区内时才挪进来 (不再无条件重置到中心)
            sys_client_pos = await self.window.ensure_cursor_in_window()
        radius = 50
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

    async def _measure_game_cursor(self) -> tuple[Point, Point | None, bool]:
        """沉淀后测量系统光标位置与游戏鼠标位置。

        游戏鼠标滞后于系统光标，测量前需沉淀让其追上；返回系统光标客户区坐标、
        游戏鼠标位置 (None 表示未匹配到模板) 及是否命中指针模板。

        Returns:
            tuple[Point, Point | None, bool]: (系统光标客户区坐标, 游戏鼠标|None, is_pointer)。
        """
        sys_pos = self.window.get_sys_cursor_client_pos()
        win_w = self.window.width
        win_h = self.window.height
        if sys_pos is None or not (0 <= sys_pos.x <= win_w and 0 <= sys_pos.y <= win_h):
            sys_pos = await self.window.ensure_cursor_in_window()
        await asyncio.sleep(_SETTLE_SEC)
        game_cursor, is_pointer = await self._get_game_mouse()
        return sys_pos, game_cursor, is_pointer

    async def mouse_move(
        self,
        target_point: Point | RelativePoint,
        max_retries: int = 5,
    ) -> bool:
        """校准移动鼠标光标至目标点，补偿游戏鼠标与系统光标的位置偏移。

        拥有一整条钟形轨迹：每次迭代沉淀后用 CV 测量游戏鼠标实际位置，按偏移反算
        系统光标目标 aim，再用一条 ease-in-out 钟形 (按距离缩放步数/时长) 移动过去；
        首次迭代为主弹道，后续为残差小修正，直至落入容差或命中指针模板。

        Args:
            target_point: 目标点 (绝对 Point 或相对 RelativePoint)。
            max_retries: 最大校准迭代次数。

        Returns:
            bool: 到位返回 True，达到最大次数仍未收敛返回 False。
        """
        abs_target = self.window.resolve_point(target_point)
        assert abs_target is not None

        for _ in range(max_retries):
            sys_pos, game_cursor, is_pointer = await self._measure_game_cursor()
            if game_cursor is None:
                raise RuntimeError("未匹配到游戏鼠标模板 cursor.png")
            if is_pointer:
                return True
            if (
                math.hypot(game_cursor.x - abs_target.x, game_cursor.y - abs_target.y)
                <= _TOLERANCE_PX
            ):
                return True
            # 偏移校正：系统光标目标 = 目标点 - (游戏鼠标 - 系统光标)
            aim = Point(
                x=abs_target.x - (game_cursor.x - sys_pos.x),
                y=abs_target.y - (game_cursor.y - sys_pos.y),
            )
            # 单条钟形到 aim，按跳距缩放步数/时长：短跳用更少步数与更短时长
            hop_dist = math.hypot(aim.x - sys_pos.x, aim.y - sys_pos.y)
            steps = max(8, min(30, int(hop_dist / 20)))
            duration_sec = max(0.15, min(0.8, hop_dist / 1000))
            await self.window.bell_move_steps(sys_pos, aim, steps, duration_sec)
            # 下一轮迭代开头的 _measure_game_cursor 负责再次沉淀与复测

        logger.warning("达到最大校准重试次数")
        return False

    async def mouse_click(
        self,
        point: Point | RelativePoint | None = None,
    ) -> None:
        if point:
            await self.mouse_move(point)
            await asyncio.sleep(0.1)
        await self.window.mouse_click()
