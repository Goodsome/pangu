"""BaseScreen.mouse_move 偏移校准与钟形轨迹单元测试。"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from client_core import Point, Window
from mhxy_client.screens import base as base_mod
from mhxy_client.screens.base import BaseScreen


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


def _make_window() -> MagicMock:
    """构造 mock window，目标点固定解析为 (100, 100)、系统光标在窗内。"""
    mock_window = MagicMock(spec=Window)
    mock_window.width = 800
    mock_window.height = 600
    mock_window.resolve_point = MagicMock(return_value=Point(x=100, y=100))
    mock_window.get_sys_cursor_client_pos = MagicMock(return_value=Point(x=100, y=100))
    mock_window.ensure_cursor_in_window = AsyncMock(return_value=Point(x=100, y=100))
    mock_window.bell_move_steps = AsyncMock()
    return mock_window


@pytest.mark.anyio
async def test_mouse_move_pointer_template_returns_immediately() -> None:
    """命中指针模板时立即返回 True，不触发钟形移动。"""
    mock_window = _make_window()
    screen = _ConcreteScreen(
        window=mock_window, game_sequence=[(Point(x=100, y=100), True)]
    )

    assert await screen.mouse_move(Point(x=100, y=100)) is True
    assert not mock_window.bell_move_steps.called


@pytest.mark.anyio
async def test_mouse_move_within_tolerance_returns_true() -> None:
    """游戏鼠标已落入容差时返回 True，不触发钟形移动。"""
    mock_window = _make_window()
    # 游戏鼠标距目标 5px (< 10 容差)
    screen = _ConcreteScreen(
        window=mock_window, game_sequence=[(Point(x=105, y=100), False)]
    )

    assert await screen.mouse_move(Point(x=100, y=100)) is True
    assert not mock_window.bell_move_steps.called


@pytest.mark.anyio
async def test_mouse_move_calibrates_offset_and_converges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """偏移校正: 首次按 offset 反算 aim 并钟形移动，二次复测落入容差收敛。"""
    monkeypatch.setattr(base_mod, "_SETTLE_SEC", 0.0)

    mock_window = _make_window()
    # 迭代1: sys=(100,100), game=(150,100) -> offset(+50,0), aim=(50,100)
    # 迭代2: sys=(50,100),  game=(100,100) -> 落入容差收敛
    mock_window.get_sys_cursor_client_pos = MagicMock(
        side_effect=[Point(x=100, y=100), Point(x=50, y=100)]
    )
    screen = _ConcreteScreen(
        window=mock_window,
        game_sequence=[(Point(x=150, y=100), False), (Point(x=100, y=100), False)],
    )

    assert await screen.mouse_move(Point(x=100, y=100)) is True
    mock_window.bell_move_steps.assert_called_once()
    call = mock_window.bell_move_steps.call_args
    assert call.args[0] == Point(x=100, y=100)  # start = sys_pos
    assert call.args[1] == Point(x=50, y=100)  # aim = target - offset


@pytest.mark.anyio
async def test_mouse_move_raises_when_no_cursor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """未匹配到游戏鼠标模板时抛出 RuntimeError。"""
    monkeypatch.setattr(base_mod, "_SETTLE_SEC", 0.0)

    mock_window = _make_window()
    screen = _ConcreteScreen(window=mock_window, game_sequence=[(None, False)])

    with pytest.raises(RuntimeError):
        await screen.mouse_move(Point(x=100, y=100))


@pytest.mark.anyio
async def test_mouse_move_exhausts_retries_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """持续偏离目标时耗尽迭代返回 False，每次迭代均触发钟形移动。"""
    monkeypatch.setattr(base_mod, "_SETTLE_SEC", 0.0)

    mock_window = _make_window()
    # 始终偏离: sys=(100,100), game=(200,100) -> aim=(0,100)，复测仍偏离
    mock_window.get_sys_cursor_client_pos = MagicMock(return_value=Point(x=100, y=100))
    screen = _ConcreteScreen(
        window=mock_window,
        game_sequence=[
            (Point(x=200, y=100), False),
            (Point(x=200, y=100), False),
            (Point(x=200, y=100), False),
        ],
    )

    assert await screen.mouse_move(Point(x=100, y=100), max_retries=3) is False
    assert mock_window.bell_move_steps.call_count == 3
