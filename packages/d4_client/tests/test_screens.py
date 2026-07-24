"""MainHUD 与 AutoCalibratingScreen POM 单元测试套件。"""

from unittest.mock import AsyncMock

import pytest

from d4_client import D4Window, InventoryPanel, MainHUD, SocialPanel
from sys_input.constants import VirtualKeyCode


@pytest.fixture
def mock_window() -> AsyncMock:
    """构造 Mock D4Window 实例。"""
    window = AsyncMock(spec=D4Window)
    return window


@pytest.fixture
def main_hud(mock_window: AsyncMock) -> MainHUD:
    """构造 MainHUD 测试对象。"""
    return MainHUD(window=mock_window)


@pytest.mark.anyio
async def test_main_hud_is_visible(main_hud: MainHUD) -> None:
    """测试 MainHUD 基础判定。"""
    visible = await main_hud.is_visible()
    assert visible is True

    wait_res = await main_hud.wait_until_visible(timeout_sec=0.5, poll_interval_sec=0.1)
    assert wait_res is True


@pytest.mark.anyio
async def test_main_hud_open_screens(main_hud: MainHUD, mock_window: AsyncMock) -> None:
    """测试 MainHUD 呼出并返回页面 POM 对象。"""
    inv_screen = await main_hud.open_inventory()
    mock_window.key_press.assert_called_with(VirtualKeyCode.VK_I)
    assert isinstance(inv_screen, InventoryPanel)
    assert inv_screen.window == mock_window

    social_screen = await main_hud.open_social()
    mock_window.key_press.assert_called_with(VirtualKeyCode.VK_O)
    assert isinstance(social_screen, SocialPanel)
    assert social_screen.window == mock_window
