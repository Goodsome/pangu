from abc import ABC
import asyncio
from dataclasses import dataclass, field
import logging
import math

from pathlib import Path

from client_core import (
    AutoCalibratingScreen,
    Point,
    Region,
    RelativeRegion,
    RelativePoint,
)
from mhxy_client.config import MainHudLayoutConfig
from sys_input import MouseButton

logger = logging.getLogger(__name__)

_DEFAULT_CURSOR_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3] / "templates" / "cursor.png"
)
_DEFAULT_POINTER_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3] / "templates" / "pointer.png"
)

# 校准容差与 CV 沉淀时间：游戏光标滞后系统光标，测量前需沉淀让其追上
_TOLERANCE_PX: float = 10.0
_SETTLE_SEC: float = 0.2
# 钟形减速段 CV 检查点 (占步数比例)：此处速度低、游戏光标滞后误差小，offset 估计更准
_CV_CHECKPOINT_FRACTIONS: tuple[float, ...] = (0.8,)


def _corrected_aim(abs_target: Point, sys_pos: Point, game: Point) -> Point:
    """按 offset (game - sys) 反算系统光标目标: aim = target - offset。"""
    return Point(
        x=abs_target.x - (game.x - sys_pos.x),
        y=abs_target.y - (game.y - sys_pos.y),
    )


def _hop_scale(hop_dist: float) -> tuple[int, float]:
    """按跳距缩放钟形步数与时长: 短跳用更少步数与更短时长。"""
    steps = max(5, min(30, int(hop_dist / 20)))
    duration = max(0.4, min(1.2, hop_dist / 200))
    return steps, duration


@dataclass
class BaseScreen(AutoCalibratingScreen, ABC):
    config: MainHudLayoutConfig = field(default_factory=MainHudLayoutConfig)

    async def _get_cursor_region(self) -> Region:
        sys_client_pos = self.window.get_sys_cursor_client_pos()
        win_w = self.window.width
        win_h = self.window.height
        if not (0 <= sys_client_pos.x <= win_w and 0 <= sys_client_pos.y <= win_h):
            # 系统光标不在窗口客户区内时才挪进来 (不再无条件重置到中心)
            sys_client_pos = await self.window.ensure_cursor_in_window()
        radius = 100
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
            frame = await self.window.capture(roi)
            await frame.save(Path("screenshots/match_cursor_failed.png"))
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
        if not (0 <= sys_pos.x <= win_w and 0 <= sys_pos.y <= win_h):
            return sys_pos, sys_pos, False
        await asyncio.sleep(_SETTLE_SEC)
        game_cursor, is_pointer = await self._get_game_mouse()
        return sys_pos, game_cursor, is_pointer

    async def _measure_and_plan(
        self,
        abs_target: Point,
        target_roi: Region | None = None,
    ) -> tuple[Point, Point, int, float] | None:
        """沉淀测量并规划下一步钟形: 返回 (sys_pos, aim, steps, duration)。

        已命中指针模板、游戏光标落入目标 ROI 或与目标点距离小于容差时返回 None
        (视为到位)。
        """
        sys_pos, game_cursor, is_pointer = await self._measure_game_cursor()
        if game_cursor is None:
            raise RuntimeError("未匹配到游戏鼠标模板 cursor.png")
        if is_pointer:
            return None
        if target_roi is not None and target_roi.contains_point(game_cursor):
            return None
        if (
            math.hypot(game_cursor.x - abs_target.x, game_cursor.y - abs_target.y)
            <= _TOLERANCE_PX
        ):
            return None
        aim = _corrected_aim(abs_target, sys_pos, game_cursor)
        hop_dist = math.hypot(aim.x - sys_pos.x, aim.y - sys_pos.y)
        steps, duration_sec = _hop_scale(hop_dist)
        return sys_pos, aim, steps, duration_sec

    async def mouse_move(
        self,
        target_point: Point | RelativePoint | None = None,
        max_retries: int = 5,
        target_roi: Region | RelativeRegion | None = None,
    ) -> bool:
        """校准移动鼠标光标至目标点，补偿游戏鼠标与系统光标的位置偏移。

        一条钟形 + 减速段中途 CV: 初始测偏移定粗略 aim，钟形行进至减速段检查点时
        复测 (此处速度低、游戏光标滞后误差小)，用新鲜 offset 重算 aim 并重新基准
        剩余步数 (边走边修)，避免"先冲到错误目标再二次修正"的机械感。
        未收敛则进入残差修正循环兜底。

        若提供 ``target_roi``，到位判定优先使用 ROI 包含检测——只要游戏光标落在
        ROI 内即视为到达，不再以目标点距离容差为准。此时 ``target_point`` 可省略，
        默认以 ROI 中心作为移动方向参考点。

        Args:
            target_point: 目标点 (绝对 Point 或相对 RelativePoint)。若提供了
                ``target_roi`` 可省略，默认取 ROI 中心。
            max_retries: 残差修正最大迭代次数。
            target_roi: 目标感兴趣区域。游戏光标进入该矩形区域即视为到位，
                优先级高于点距离容差判定。

        Returns:
            bool: 到位返回 True，达到最大次数仍未收敛返回 False。
        """
        abs_target_roi = self.window.resolve_region(target_roi)
        if target_point is not None:
            abs_target = self.window.resolve_point(target_point)
            assert abs_target is not None
        else:
            if abs_target_roi is None:
                raise ValueError("target_point 和 target_roi 不能同时为 None")
            abs_target = abs_target_roi.center

        planned = await self._measure_and_plan(abs_target, abs_target_roi)
        if planned is None:
            return True
        sys_pos, aim, steps, duration_sec = planned
        checkpoints = {int(steps * f) for f in _CV_CHECKPOINT_FRACTIONS}
        checkpoints.discard(0)
        converged = False

        async def on_step(step: int, _total: int, _cur: Point) -> Point | None:
            nonlocal converged
            if step not in checkpoints:
                return None
            # 减速段检查点: 速度低、滞后误差小，offset 估计更准
            sys_cur, game, is_pointer = await self._measure_game_cursor()
            if game is None:
                return None
            if is_pointer:
                converged = True
            elif abs_target_roi is not None and abs_target_roi.contains_point(game):
                converged = True
            elif (
                math.hypot(game.x - abs_target.x, game.y - abs_target.y)
                <= _TOLERANCE_PX
            ):
                converged = True
            aim = _corrected_aim(abs_target, sys_cur, game)
            return aim

        await self.window.bell_move_steps(
            sys_pos, aim, steps, duration_sec, on_step=on_step
        )
        if converged:
            return True

        for _ in range(max_retries):
            planned = await self._measure_and_plan(abs_target, abs_target_roi)
            if planned is None:
                return True
            sys_pos, aim, steps, duration_sec = planned
            await self.window.bell_move_steps(sys_pos, aim, steps, duration_sec)

        logger.warning("达到最大校准重试次数")
        return False

    async def mouse_click(
        self,
        point: Point | RelativePoint | None = None,
        button: MouseButton = MouseButton.LEFT,
        target_roi: Region | RelativeRegion | None = None,
    ) -> None:
        """点击目标点/目标区域。

        若提供 ``target_roi``，只要游戏光标进入该区域即视为到位并执行点击，
        不再以点距离容差为准。详见 :meth:`mouse_move`。
        """
        if point is not None or target_roi is not None:
            _ = await self.mouse_move(point, target_roi=target_roi)
            await asyncio.sleep(0.1)
        await self.window.mouse_click(button=button)

    async def click(
        self,
        point: Point | RelativePoint | None = None,
        target_roi: Region | RelativeRegion | None = None,
        button: MouseButton = MouseButton.LEFT,
    ) -> None:
        await self.mouse_click(point, target_roi=target_roi, button=button)
