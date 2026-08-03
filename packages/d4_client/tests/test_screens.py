"""MainHUD 与 AutoCalibratingScreen POM 单元测试套件。"""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from d4_client import InventoryPanel, MainHUD, SocialPanel, Window
from sys_input.constants import VirtualKeyCode


@pytest.fixture
def mock_window() -> AsyncMock:
    """构造 Mock Window 实例。"""
    from client_core import OcrResult, Point, Region

    window = AsyncMock(spec=Window)
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
    await board.select_class(PlayerClass.BARBARIAN)
    assert mock_window.mouse_click.called

    # 2. 成功使用 PlayerClass 枚举计算第 2 个职业 (NECROMANCER 死灵法师)
    await board.select_class(PlayerClass.NECROMANCER)
    assert mock_window.mouse_click.called

    # 3. 未知职业抛出 KeyError
    with pytest.raises(KeyError):
        await board.select_class("INVALID_CLASS")


@pytest.mark.anyio
async def test_leaderboard_capture_records_region(
    mock_window: AsyncMock, tmp_path: Path
) -> None:
    """测试 LeaderboardScreen.capture_records_region 截取记录区域并保存磁盘图片。"""
    from client_core import ImageFrame
    from d4_client.screens.leaderboard import LeaderboardScreen

    mock_window.width = 1920
    mock_window.height = 1080
    mock_window.capture.return_value = ImageFrame(
        data=b"\x00" * 400,
        width=10,
        height=10,
        channels=4,
    )

    board = LeaderboardScreen(window=mock_window)
    out_file = tmp_path / "records_test.png"
    saved_path = await board.capture_records_region(out_file)

    assert saved_path == out_file
    assert out_file.exists()
    mock_window.capture.assert_called_once_with(region=board.layout.records_roi)


@pytest.mark.anyio
async def test_leaderboard_click_row(mock_window: AsyncMock) -> None:
    """测试 LeaderboardScreen.click_row 依据 records_roi 垂直 10 等分定位计算。"""
    from d4_client.screens.leaderboard import LeaderboardScreen

    mock_window.width = 1920
    mock_window.height = 1080

    board = LeaderboardScreen(window=mock_window)

    # 1. 成功计算第 1 行 (row_index=0)
    pt0 = await board.click_row(0)
    assert pt0.x > 0 and pt0.y > 0
    assert mock_window.mouse_click.called

    # 2. 成功计算第 10 行 (row_index=9)
    pt9 = await board.click_row(9)
    assert pt9.x == pt0.x  # 同一列，X 相对坐标对齐
    assert pt9.y > pt0.y  # 第 10 行的 Y 坐标显著大于第 1 行

    # 3. 越界 row_index 抛出 IndexError
    with pytest.raises(IndexError):
        await board.click_row(-1)

    with pytest.raises(IndexError):
        await board.click_row(10)


@pytest.mark.anyio
async def test_leaderboard_open_player_config(mock_window: AsyncMock) -> None:
    """测试 LeaderboardScreen.open_player_config 使用 view_config_roi 点击并返回 PlayerConfigScreen。"""
    from d4_client.screens.leaderboard import LeaderboardScreen
    from d4_client.screens.player_config import PlayerConfigScreen

    mock_window.width = 1920
    mock_window.height = 1080

    board = LeaderboardScreen(window=mock_window)
    player_config_screen = await board.open_player_config()

    assert isinstance(player_config_screen, PlayerConfigScreen)
    assert mock_window.mouse_click.called


@pytest.mark.anyio
async def test_leaderboard_current_page_number(mock_window: AsyncMock) -> None:
    """测试 LeaderboardScreen.current_page_number OCR 识别与正则提取。"""
    from client_core import OcrResult, Point, Region
    from d4_client.screens.leaderboard import LeaderboardScreen

    mock_window.width = 1920
    mock_window.height = 1080
    mock_window.ocr.return_value = [
        OcrResult(
            text="23 / 100",
            confidence=0.95,
            rect=Region(x=0, y=0, width=50, height=20),
            box_points=(Point(0, 0), Point(50, 0), Point(50, 20), Point(0, 20)),
        )
    ]

    board = LeaderboardScreen(window=mock_window)
    page_num = await board.current_page_number()

    assert page_num == 23
    mock_window.ocr.assert_called_once_with(roi=board.layout.page_number_roi)


@pytest.mark.anyio
async def test_player_config_get_equipment_slot_roi(mock_window: AsyncMock) -> None:
    """测试 PlayerConfigScreen 针对 1/2 排及不同职业计算装备格子 ROI 与居中对齐。"""
    from d4_client.screens.player_config import PlayerConfigScreen
    from d4_types.enums.player_class import PlayerClass

    screen_barbarian = PlayerConfigScreen(
        window=mock_window,
        player_class=PlayerClass.BARBARIAN,
        page=1,
        row=1,
    )

    # 1. 第一排装备槽 (slot_index=0 ~ 7)
    roi_0 = screen_barbarian.get_equipment_slot_roi(0)
    roi_7 = screen_barbarian.get_equipment_slot_roi(7)
    assert roi_0.y == roi_7.y
    assert roi_7.x > roi_0.x
    assert (
        pytest.approx(roi_0.width) == screen_barbarian.config.equipment_roi.width / 8.0
    )

    # 2. 第二排装备槽 (野蛮人 4 件: slot_index=8 ~ 11)
    roi_8 = screen_barbarian.get_equipment_slot_roi(8)
    roi_11 = screen_barbarian.get_equipment_slot_roi(11)
    assert roi_8.y > roi_0.y
    assert roi_11.x > roi_8.x

    # 验证居中逻辑: 第二排 4 件的总宽度与起点相对居中
    eq_roi = screen_barbarian.config.equipment_roi
    slot_w = eq_roi.width / 8.0
    expected_start_x = eq_roi.x + (eq_roi.width - 4 * slot_w) / 2.0
    assert pytest.approx(roi_8.x) == expected_start_x

    # 3. 越界 slot_index 校验 (灵巫共 8+1=9 个槽位 0~8)
    screen_spirit = PlayerConfigScreen(
        window=mock_window,
        player_class=PlayerClass.SPIRITBORN,
        page=1,
        row=1,
    )
    with pytest.raises(IndexError):
        screen_spirit.get_equipment_slot_roi(9)


@pytest.mark.anyio
async def test_player_config_capture_equipment_slot(
    mock_window: AsyncMock, tmp_path: Path
) -> None:
    """测试 PlayerConfigScreen.capture_equipment_slot 使用持有的状态保存截图。"""
    from client_core import ImageFrame
    from d4_client.screens.player_config import PlayerConfigScreen
    from d4_types.enums.player_class import PlayerClass

    mock_window.width = 1920
    mock_window.height = 1080
    mock_window.capture.return_value = ImageFrame(
        data=b"\x00" * 1600,
        width=20,
        height=20,
        channels=4,
    )

    screen = PlayerConfigScreen(
        window=mock_window,
        player_class=PlayerClass.BARBARIAN,
        page=1,
        row=2,
    )
    output_dir = tmp_path / "equipment_captures"

    saved_path = await screen.capture_equipment_slot(
        output_dir=output_dir,
        slot_index=0,
    )

    expected_path = output_dir / "BARBARIAN_1_2_0.png"
    assert saved_path == expected_path
    assert expected_path.exists()
    assert mock_window.mouse_click.called or mock_window.smooth_mouse_move.called
    assert mock_window.capture.called


@pytest.mark.anyio
async def test_player_config_get_skill_slot_roi(mock_window: AsyncMock) -> None:
    """测试 PlayerConfigScreen 1 排 6 个技能格子 ROI 计算与 tooltip ROI 计算。"""
    from d4_client.screens.player_config import PlayerConfigScreen
    from d4_types.enums.player_class import PlayerClass

    screen = PlayerConfigScreen(
        window=mock_window,
        player_class=PlayerClass.BARBARIAN,
        page=1,
        row=1,
    )

    assert screen.get_skill_slot_count() == 6

    # 1. 验证第 1 个与第 6 个技能格子 ROI (0 ~ 5)
    s_roi_0 = screen.get_skill_slot_roi(0)
    s_roi_5 = screen.get_skill_slot_roi(5)
    assert s_roi_0.y == s_roi_5.y
    assert s_roi_5.x > s_roi_0.x
    assert pytest.approx(s_roi_0.width) == screen.config.skill_roi.width / 6.0

    # 2. 验证 tooltip ROI 相对偏移
    tt_roi_0 = screen.get_skill_tooltip_roi(s_roi_0)
    assert tt_roi_0.width == screen.config.skill_01_roi.width
    assert tt_roi_0.height == screen.config.skill_01_roi.height

    # 3. 越界 slot_index 校验
    with pytest.raises(IndexError):
        screen.get_skill_slot_roi(6)


@pytest.mark.anyio
async def test_player_config_capture_skill_slot(
    mock_window: AsyncMock, tmp_path: Path
) -> None:
    """测试 PlayerConfigScreen.capture_skill_slot 使用持有的状态截取并保存技能图片。"""
    from client_core import ImageFrame
    from d4_client.screens.player_config import PlayerConfigScreen
    from d4_types.enums.player_class import PlayerClass

    mock_window.width = 1920
    mock_window.height = 1080
    mock_window.capture.return_value = ImageFrame(
        data=b"\x00" * 1600,
        width=20,
        height=20,
        channels=4,
    )

    screen = PlayerConfigScreen(
        window=mock_window,
        player_class=PlayerClass.BARBARIAN,
        page=1,
        row=2,
    )
    output_dir = tmp_path / "skill_captures"

    saved_path = await screen.capture_skill_slot(
        output_dir=output_dir,
        slot_index=0,
    )

    expected_path = output_dir / "skill_BARBARIAN_1_2_0.png"
    assert saved_path == expected_path
    assert expected_path.exists()
    assert mock_window.mouse_click.called
    assert mock_window.capture.called


@pytest.mark.anyio
async def test_player_config_get_talisman_slot_roi(mock_window: AsyncMock) -> None:
    """测试 PlayerConfigScreen 1 排 7 个护身符格子 ROI 计算与 tooltip ROI 计算。"""
    from d4_client.screens.player_config import PlayerConfigScreen
    from d4_types.enums.player_class import PlayerClass

    screen = PlayerConfigScreen(
        window=mock_window,
        player_class=PlayerClass.BARBARIAN,
        page=1,
        row=1,
    )

    assert screen.get_talisman_slot_count() == 7

    # 1. 验证第 1 个与第 7 个护身符格子 ROI (0 ~ 6)
    t_roi_0 = screen.get_talisman_slot_roi(0)
    t_roi_6 = screen.get_talisman_slot_roi(6)
    assert t_roi_0.y == t_roi_6.y
    assert t_roi_6.x > t_roi_0.x
    assert pytest.approx(t_roi_0.width) == screen.config.talismans_roi.width / 7.0

    # 2. 验证 tooltip ROI 相对偏移
    tt_roi_0 = screen.get_talisman_tooltip_roi(t_roi_0)
    assert tt_roi_0.width == screen.config.talismans_01_roi.width
    assert tt_roi_0.height == screen.config.talismans_01_roi.height

    # 3. 越界 slot_index 校验
    with pytest.raises(IndexError):
        screen.get_talisman_slot_roi(7)


@pytest.mark.anyio
async def test_player_config_capture_talisman_slot(
    mock_window: AsyncMock, tmp_path: Path
) -> None:
    """测试 PlayerConfigScreen.capture_talisman_slot 使用持有的状态截取并保存护身符图片。"""
    from client_core import ImageFrame
    from d4_client.screens.player_config import PlayerConfigScreen
    from d4_types.enums.player_class import PlayerClass

    mock_window.width = 1920
    mock_window.height = 1080
    mock_window.capture.return_value = ImageFrame(
        data=b"\x00" * 1600,
        width=20,
        height=20,
        channels=4,
    )

    screen = PlayerConfigScreen(
        window=mock_window,
        player_class=PlayerClass.BARBARIAN,
        page=1,
        row=2,
    )
    output_dir = tmp_path / "talisman_captures"

    saved_path = await screen.capture_talisman_slot(
        output_dir=output_dir,
        slot_index=0,
    )

    expected_path = output_dir / "talisman_BARBARIAN_1_2_0.png"
    assert saved_path == expected_path
    assert expected_path.exists()
    assert mock_window.mouse_click.called
    assert mock_window.capture.called


@pytest.mark.anyio
async def test_leaderboard_state_tracking_and_pass_to_player_config(
    mock_window: AsyncMock, tmp_path: Path
) -> None:
    """测试 LeaderboardScreen 记录职业、页码、行号状态并透传至 PlayerConfigScreen，默认完成命名保存。"""
    from client_core import ImageFrame
    from d4_client.screens.leaderboard import LeaderboardScreen
    from d4_types.enums.player_class import PlayerClass

    mock_window.width = 1920
    mock_window.height = 1080
    mock_window.capture.return_value = ImageFrame(
        data=b"\x00" * 1600,
        width=20,
        height=20,
        channels=4,
    )

    board = LeaderboardScreen(window=mock_window)

    # 1. 模拟交互并记录状态
    await board.select_class(PlayerClass.NECROMANCER)
    await board.next_page()  # current_page -> 2
    await board.click_row(3)  # current_row -> 3

    assert board.current_class == PlayerClass.NECROMANCER
    assert board.current_page == 2
    assert board.current_row == 3

    # 2. 打开 PlayerConfigScreen 并验证状态继承
    player_config_screen = await board.open_player_config()
    assert player_config_screen.player_class == PlayerClass.NECROMANCER
    assert player_config_screen.page == 2
    assert player_config_screen.row == 3

    # 3. 验证 capture_equipment_slot 默认使用透传的状态进行保存
    output_dir = tmp_path / "auto_state_captures"
    saved_path = await player_config_screen.capture_equipment_slot(
        output_dir=output_dir,
        slot_index=0,
    )

    expected_path = output_dir / "NECROMANCER_2_3_0.png"
    assert saved_path == expected_path
    assert expected_path.exists()
