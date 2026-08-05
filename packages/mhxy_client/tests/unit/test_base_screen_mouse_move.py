"""BaseScreen.mouse_move 偏移校准与钟形轨迹 (含 on_step 中途校正) 单元测试。"""

from unittest.mock import MagicMock

import pytest

from client_core import Point, Window
from mhxy_client.screens import base as base_mod
from mhxy_client.screens.base import BaseScreen


class _BellSpy:
    """替代 bell_move_steps: 记录调用次数，并逐步触发 on_step 回调 (回调内部按检查点节流)。"""

    def __init__(self) -> None:
        self.call_count = 0

    async def __call__(
        self,
        start: Point,
        target: Point,
        steps: int,
        duration_sec: float,
        on_step=None,
    ) -> None:
        self.call_count += 1
        if on_step is not None:
            for s in range(1, steps + 1):
                await on_step(s, steps, target)


class _ConcreteScreen(BaseScreen):
    """可实例化的 BaseScreen 测试替身，_get_game_mouse 由注入序列驱动。"""

    def __init__(
        self,
        window: Window,
        game_sequence: list[tuple[Point | None, bool]],
    ) -> None:
        super().__init__(window=window)
        self._game_sequence = game_sequence
        self._game_index = 0

    async def _get_game_mouse(self) -> tuple[Point | None, bool]:
        if self._game_index >= len(self._game_sequence):
            raise AssertionError("_get_game_mouse 被调用次数超出预期")
        result = self._game_sequence[self._game_index]
        self._game_index += 1
        return result


def _make_window(sys_positions: list[Point]) -> MagicMock:
    """构造 mock window: 目标点固定解析为 (100,100)，系统光标按序列返回。"""
    mock_window = MagicMock(spec=Window)
    mock_window.width = 800
    mock_window.height = 600
    mock_window.resolve_point = MagicMock(return_value=Point(x=100, y=100))
    mock_window.get_sys_cursor_client_pos = MagicMock(side_effect=sys_positions)
    mock_window.bell_move_steps = _BellSpy()
    return mock_window


@pytest.mark.anyio
async def test_mouse_move_pointer_template_returns_immediately() -> None:
    """命中指针模板时立即返回 True，不触发钟形移动。"""
    mock_window = _make_window([Point(x=100, y=100)])
    screen = _ConcreteScreen(
        window=mock_window, game_sequence=[(Point(x=100, y=100), True)]
    )

    assert await screen.mouse_move(Point(x=100, y=100)) is True
    assert mock_window.bell_move_steps.call_count == 0


@pytest.mark.anyio
async def test_mouse_move_within_tolerance_returns_true() -> None:
    """游戏鼠标已落入容差时返回 True，不触发钟形移动。"""
    mock_window = _make_window([Point(x=100, y=100)])
    # 游戏鼠标距目标 5px (< 10 容差)
    screen = _ConcreteScreen(
        window=mock_window, game_sequence=[(Point(x=105, y=100), False)]
    )

    assert await screen.mouse_move(Point(x=100, y=100)) is True
    assert mock_window.bell_move_steps.call_count == 0


@pytest.mark.anyio
async def test_mouse_move_in_flight_cv_converges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """减速段检查点 CV 用新鲜 offset 重算 aim，单条钟形即收敛 (无需二次修正)。"""
    monkeypatch.setattr(base_mod, "_SETTLE_SEC", 0.0)

    # 初始 CV: sys=(100,100), game=(150,100) -> aim=(50,100)
    # 检查点 CV (step 6): sys=(50,100), game=(100,100) -> 落入容差收敛
    mock_window = _make_window([Point(x=100, y=100), Point(x=50, y=100)])
    screen = _ConcreteScreen(
        window=mock_window,
        game_sequence=[(Point(x=150, y=100), False), (Point(x=100, y=100), False)],
    )

    assert await screen.mouse_move(Point(x=100, y=100)) is True
    # 仅一条钟形 (on_step 内完成校正)，未进入残差循环
    assert mock_window.bell_move_steps.call_count == 1


@pytest.mark.anyio
async def test_mouse_move_raises_when_no_cursor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """未匹配到游戏鼠标模板时抛出 RuntimeError。"""
    monkeypatch.setattr(base_mod, "_SETTLE_SEC", 0.0)

    mock_window = _make_window([Point(x=100, y=100)])
    screen = _ConcreteScreen(window=mock_window, game_sequence=[(None, False)])

    with pytest.raises(RuntimeError):
        await screen.mouse_move(Point(x=100, y=100))


@pytest.mark.anyio
async def test_mouse_move_exhausts_retries_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """持续偏离目标: on_step 钟形未收敛，残差循环兜底耗尽返回 False。"""
    monkeypatch.setattr(base_mod, "_SETTLE_SEC", 0.0)

    # 初始 + 检查点 + 3 次残差 = 5 次 CV，均偏离
    sys_positions = [Point(x=100, y=100) for _ in range(5)]
    mock_window = _make_window(sys_positions)
    game_seq = [(Point(x=200, y=100), False) for _ in range(5)]
    screen = _ConcreteScreen(window=mock_window, game_sequence=game_seq)

    assert await screen.mouse_move(Point(x=100, y=100), max_retries=3) is False
    # 1 条 on_step 钟形 + 3 条残差钟形
    assert mock_window.bell_move_steps.call_count == 4
