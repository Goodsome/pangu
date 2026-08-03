"""mhxy_client MainHUD 与 POM 页面对象单元测试套件。"""

from unittest.mock import AsyncMock

import pytest

from client_core import OcrResult, Point, Region, RelativeRegion
from mhxy_client import (
    InventoryPanel,
    MainHUD,
    MainHudLayoutConfig,
    MhxyClient,
    SocialPanel,
    Window,
)
from sys_input.constants import VirtualKeyCode


@pytest.fixture
def mock_window() -> AsyncMock:
    """构造 Mock Window 实例。"""
    window = AsyncMock(spec=Window)
    window.ocr.return_value = [
        OcrResult(
            text="建邺城 (105, 42)",
            confidence=0.95,
            rect=Region(0, 0, 100, 20),
            box_points=(Point(0, 0), Point(100, 0), Point(100, 20), Point(0, 20)),
        )
    ]
    return window


@pytest.fixture
def main_hud(mock_window: AsyncMock) -> MainHUD:
    """构造 MainHUD 测试对象。"""
    return MainHUD(window=mock_window)


def test_main_hud_layout_config_default() -> None:
    """测试 MainHudLayoutConfig 配置。"""
    config = MainHudLayoutConfig()
    assert isinstance(config.map_name_roi, RelativeRegion)
    assert isinstance(config.task_list_roi, RelativeRegion)


@pytest.mark.anyio
async def test_main_hud_is_visible(main_hud: MainHUD, mock_window: AsyncMock) -> None:
    """测试 MainHUD 基础判定与等待处理 (包含兜底 fallback ROI 处理)。"""
    visible = await main_hud.is_visible()
    assert visible is True

    wait_res = await main_hud.wait_until_visible(timeout_sec=0.5, poll_interval_sec=0.1)
    assert wait_res is True


@pytest.mark.anyio
async def test_main_hud_is_visible_false(
    main_hud: MainHUD, mock_window: AsyncMock
) -> None:
    """测试当无地图 OCR 识别结果时 is_visible 返回 False。"""
    mock_window.ocr.return_value = []
    visible = await main_hud.is_visible()
    assert visible is False


@pytest.mark.anyio
async def test_main_hud_get_current_map(
    main_hud: MainHUD, mock_window: AsyncMock
) -> None:
    """测试 MainHUD.get_current_map 提取地图名称并剥离坐标。"""
    mock_window.ocr.return_value = [
        OcrResult(
            text="长安城 [230, 150]",
            confidence=0.95,
            rect=Region(0, 0, 100, 20),
            box_points=(Point(0, 0), Point(100, 0), Point(100, 20), Point(0, 20)),
        )
    ]
    map_name = await main_hud.get_current_map()
    assert map_name == "长安城"

    # 空识别逻辑
    mock_window.ocr.return_value = []
    map_name_empty = await main_hud.get_current_map()
    assert map_name_empty == ""


@pytest.mark.anyio
async def test_main_hud_check_sect_task(
    main_hud: MainHUD, mock_window: AsyncMock
) -> None:
    """测试 MainHUD.check_sect_task 获取师门任务解析并返回 SectTaskInfo。"""
    from mhxy_client.models import SectTaskStatus

    mock_window.ocr.return_value = [
        OcrResult(
            text="任务追踪",
            confidence=1.0,
            rect=Region(655, 156, 63, 15),
            box_points=(
                Point(655, 156),
                Point(718, 156),
                Point(718, 171),
                Point(655, 171),
            ),
        ),
        OcrResult(
            text="师门任务",
            confidence=0.99,
            rect=Region(616, 193, 63, 16),
            box_points=(
                Point(616, 193),
                Point(679, 193),
                Point(679, 209),
                Point(616, 209),
            ),
        ),
        OcrResult(
            text="新的一天，回师门看看师",
            confidence=0.99,
            rect=Region(615, 210, 176, 17),
            box_points=(
                Point(615, 210),
                Point(791, 210),
                Point(791, 227),
                Point(615, 227),
            ),
        ),
        OcrResult(
            text="父有什么吩咐吧。",
            confidence=0.98,
            rect=Region(615, 226, 119, 18),
            box_points=(
                Point(615, 226),
                Point(734, 226),
                Point(734, 244),
                Point(615, 244),
            ),
        ),
        OcrResult(
            text="仙石天机",
            confidence=1.0,
            rect=Region(615, 263, 64, 17),
            box_points=(
                Point(615, 263),
                Point(679, 263),
                Point(679, 280),
                Point(615, 280),
            ),
        ),
    ]
    info = await main_hud.check_sect_task()
    assert info.is_tracking_panel_open is True
    assert info.is_sect_task_active is True
    assert info.status == SectTaskStatus.CLAIMABLE
    assert info.task_title == "师门任务"
    assert len(info.description_lines) == 2
    assert info.action_text == "父"
    # 父字在 "父有什么吩咐吧。" (8字) 的第0个字符，offset 0.5/8 = 0.0625, X = 615 + int(119 * 0.0625) = 622
    assert info.action_point == Point(x=622, y=235)


def test_calculate_substring_point_interpolation() -> None:
    """测试 calculate_substring_point 字符横向比例插值计算。"""
    from mhxy_client.screens.main_hud import calculate_substring_point

    rect = Region(x=100, y=200, width=100, height=20)
    # 文本全长 10 字符，"师父" 位于索引 4..6，相对中心 5/10 = 0.5 -> center_x = 100 + 50 = 150
    pt = calculate_substring_point("一二三四师父七八九十", "师父", rect)
    assert pt == Point(x=150, y=210)


@pytest.mark.anyio
async def test_main_hud_claim_sect_task(
    main_hud: MainHUD, mock_window: AsyncMock
) -> None:
    """测试 MainHUD.claim_sect_task 触发点击操作。"""
    mock_window.ocr.return_value = [
        OcrResult(
            text="任务追踪",
            confidence=1.0,
            rect=Region(655, 156, 63, 15),
            box_points=(
                Point(655, 156),
                Point(718, 156),
                Point(718, 171),
                Point(655, 171),
            ),
        ),
        OcrResult(
            text="师门任务",
            confidence=0.99,
            rect=Region(616, 193, 63, 16),
            box_points=(
                Point(616, 193),
                Point(679, 193),
                Point(679, 209),
                Point(616, 209),
            ),
        ),
        OcrResult(
            text="父有什么吩咐吧。",
            confidence=0.98,
            rect=Region(615, 226, 119, 18),
            box_points=(
                Point(615, 226),
                Point(734, 226),
                Point(734, 244),
                Point(615, 244),
            ),
        ),
    ]
    res = await main_hud.claim_sect_task(smooth_move=False, delay_before_click_sec=0.0)
    assert res is True
    mock_window.mouse_move.assert_called_with(point=Point(x=622, y=235))
    mock_window.mouse_click.assert_called_with(point=None)

    # 测试 move_only 模式
    mock_window.mouse_click.reset_mock()
    res_move = await main_hud.claim_sect_task(move_only=True, smooth_move=False)
    assert res_move is True
    mock_window.mouse_move.assert_called_with(point=Point(x=622, y=235))
    mock_window.mouse_click.assert_not_called()


@pytest.mark.anyio
async def test_main_hud_open_screens(main_hud: MainHUD, mock_window: AsyncMock) -> None:
    """测试 MainHUD 呼出并返回页面 POM 对象。"""
    inv_screen = await main_hud.open_inventory()
    mock_window.key_press.assert_called_with(VirtualKeyCode.VK_E)
    assert isinstance(inv_screen, InventoryPanel)
    assert inv_screen.window == mock_window

    social_screen = await main_hud.open_social()
    mock_window.key_press.assert_called_with(VirtualKeyCode.VK_F)
    assert isinstance(social_screen, SocialPanel)
    assert social_screen.window == mock_window


@pytest.mark.anyio
async def test_social_panel_close(mock_window: AsyncMock) -> None:
    """测试 SocialPanel.close 按 ESC 返回 MainHUD。"""
    social = SocialPanel(window=mock_window)
    hud = await social.close()
    mock_window.key_press.assert_called_with(VirtualKeyCode.VK_ESCAPE)
    assert isinstance(hud, MainHUD)
    assert hud.window == mock_window


@pytest.mark.anyio
async def test_mhxy_client_main_hud_property(mock_window: AsyncMock) -> None:
    """测试 MhxyClient.main_hud 属性。"""
    client = MhxyClient(hwnd=12345, window=mock_window)
    hud = client.main_hud
    assert isinstance(hud, MainHUD)
    assert hud.window == mock_window


def test_calibrate_script_is_valid_relative_roi() -> None:
    """测试 calibrate_main_hud_roi.py 中的 is_valid_relative_roi。"""
    import importlib.util
    from pathlib import Path

    script_path = Path(__file__).parents[2] / "scripts" / "calibrate_main_hud_roi.py"
    spec = importlib.util.spec_from_file_location("calibrate_main_hud_roi", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.is_valid_relative_roi(RelativeRegion(0.1, 0.1, 0.2, 0.2)) is True
    assert module.is_valid_relative_roi(RelativeRegion(0.1, 0.1, 0.0, 0.2)) is False
    assert module.is_valid_relative_roi(None) is False
