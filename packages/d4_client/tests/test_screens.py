"""MainHUD 与 AutoCalibratingScreen POM 单元测试套件。"""

from unittest.mock import AsyncMock

import pytest

from d4_client import D4Window, InventoryPanel, MainHUD, SocialPanel
from sys_input.constants import VirtualKeyCode


@pytest.fixture
def mock_window() -> AsyncMock:
    """构造 Mock D4Window 实例。"""
    from d4_client.models import OcrResult, Point, Region

    window = AsyncMock(spec=D4Window)
    window.ocr.return_value = [
        OcrResult(
            text="基奥瓦沙",
            confidence=0.95,
            rect=Region(0, 0, 10, 10),
            box_points=(Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)),
        )
    ]
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


@pytest.mark.anyio
async def test_leaderboard_select_class(mock_window: AsyncMock) -> None:
    """测试 LeaderboardScreen.select_class 基于 PlayerClass 枚举和 8 等分相对 ROI 的定位功能。"""
    from d4_client.screens.leaderboard import LeaderboardScreen
    from d4_types.enums.player_class import PlayerClass

    mock_window.width = 1920
    mock_window.height = 1080

    board = LeaderboardScreen(window=mock_window)

    # 1. 成功使用 PlayerClass 枚举计算第 1 个职业 (BARBARIAN 野蛮人)
    pt1 = await board.select_class(PlayerClass.BARBARIAN)
    assert pt1.x > 0 and pt1.y > 0
    assert mock_window.mouse_click.called

    # 2. 成功使用 PlayerClass 枚举计算第 2 个职业 (NECROMANCER 死灵法师)
    pt2 = await board.select_class(PlayerClass.NECROMANCER)
    assert pt2.x > pt1.x  # 死灵法师在野蛮人右侧，X 坐标递增

    # 3. 未知职业抛出 KeyError
    with pytest.raises(KeyError):
        await board.select_class("INVALID_CLASS")
