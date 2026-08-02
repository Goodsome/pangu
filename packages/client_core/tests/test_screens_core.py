"""client_core AutoCalibratingScreen 单元测试套件。"""

from unittest.mock import AsyncMock
import pytest

from client_core import AutoCalibratingScreen, OcrResult, Point, Region, Window


@pytest.fixture
def mock_window() -> AsyncMock:
    """构造 Mock Window 实例。"""
    window = AsyncMock(spec=Window)
    window.ocr.return_value = [
        OcrResult(
            text="开始游戏",
            confidence=0.95,
            rect=Region(0, 0, 10, 10),
            box_points=(Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)),
        )
    ]
    return window


@pytest.mark.anyio
async def test_auto_calibrating_screen_wait_until_visible(mock_window: AsyncMock) -> None:
    """测试 AutoCalibratingScreen 页面等待检测。"""
    screen = AutoCalibratingScreen(window=mock_window, screen_name="TestScreen")
    visible = await screen.wait_until_visible(timeout_sec=0.2, poll_interval_sec=0.05)
    assert visible is True


@pytest.mark.anyio
async def test_auto_calibrating_screen_clear_cache(mock_window: AsyncMock) -> None:
    """测试 AutoCalibratingScreen 清除元素缓存。"""
    screen = AutoCalibratingScreen(window=mock_window, screen_name="TestScreen")
    screen._element_cache["btn"] = None  # type: ignore
    assert "btn" in screen._element_cache
    screen.clear_cache()
    assert "btn" not in screen._element_cache
