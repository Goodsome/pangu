"""Window 封装层与操控方法单元测试套件。"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cv_engine import (
    MatchResult as CVMatchResult,
    OcrResult as CVOcrResult,
    Point as CVPoint,
    Region as CVRegion,
)
from client_core import (
    Point,
    RelativeRegion,
    Window,
)
from sys_input import MouseButton
from vision_stream import ImageResult as VisionImageResult


@pytest.fixture
def mock_deps() -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
    """创建 Mock 依赖项。"""
    mock_input = AsyncMock()
    mock_vision = AsyncMock()
    mock_matcher = AsyncMock()
    mock_ocr = AsyncMock()

    mock_vision.capture.return_value = VisionImageResult(
        data=b"\x00" * 400,
        width=10,
        height=10,
        channels=4,
        timestamp=100000.0,
    )

    return mock_input, mock_vision, mock_matcher, mock_ocr


@pytest.fixture
def base_window(
    mock_deps: tuple[MagicMock, MagicMock, MagicMock, MagicMock],
) -> Window:
    """创建 Window 实例。"""
    mock_input, mock_vision, mock_matcher, mock_ocr = mock_deps
    return Window(
        input_backend=mock_input,
        vision_backend=mock_vision,
        template_matcher=mock_matcher,
        ocr_engine=mock_ocr,
        width=1920,
        height=1080,
    )


@pytest.mark.anyio
async def test_capture(base_window: Window, mock_deps: tuple[MagicMock, ...]) -> None:
    """测试画面捕获与领域模型包装 (含相对 ROI 解算)。"""
    img = await base_window.capture()
    assert img.width == 10
    assert mock_deps[1].capture.called

    rel_roi = RelativeRegion(x=0.1, y=0.2, width=0.5, height=0.4)
    await base_window.capture(region=rel_roi)
    last_call_args = mock_deps[1].capture.call_args
    passed_vision_region = last_call_args.kwargs["region"]
    assert passed_vision_region.x == 192
    assert passed_vision_region.y == 216
    assert passed_vision_region.width == 960
    assert passed_vision_region.height == 432


@pytest.mark.anyio
async def test_match_and_click(
    base_window: Window, mock_deps: tuple[MagicMock, ...]
) -> None:
    """测试模板匹配并点击。"""
    mock_matcher = mock_deps[2]
    mock_input = mock_deps[0]

    mock_matcher.async_match_best.return_value = CVMatchResult(
        score=0.95, rect=CVRegion(x=10, y=20, width=30, height=40)
    )

    res = await base_window.match_and_click("tpl.png", threshold=0.8)
    assert res is True
    mock_input.mouse_click.assert_called_once()
    click_kwargs = mock_input.mouse_click.call_args.kwargs
    assert click_kwargs["point"].x == 25
    assert click_kwargs["point"].y == 40
    assert click_kwargs["button"] == MouseButton.LEFT

    mock_matcher.async_match_best.return_value = None
    mock_input.mouse_click.reset_mock()
    res_fail = await base_window.match_and_click("tpl.png")
    assert res_fail is False
    mock_input.mouse_click.assert_not_called()


@pytest.mark.anyio
async def test_find_text_and_click(
    base_window: Window, mock_deps: tuple[MagicMock, ...]
) -> None:
    """测试 OCR 找字并点击。"""
    mock_ocr = mock_deps[3]
    mock_input = mock_deps[0]

    mock_ocr.async_find_text.return_value = CVOcrResult(
        text="确定",
        confidence=0.99,
        rect=CVRegion(x=100, y=200, width=50, height=20),
        box_points=(
            CVPoint(100, 200),
            CVPoint(150, 200),
            CVPoint(150, 220),
            CVPoint(100, 220),
        ),
    )

    res = await base_window.find_text_and_click("确定")
    assert res is True
    mock_input.mouse_click.assert_called_once()
    click_kwargs = mock_input.mouse_click.call_args.kwargs
    assert click_kwargs["point"].x == 125
    assert click_kwargs["point"].y == 210


@pytest.mark.anyio
async def test_mouse_and_key_actions(
    base_window: Window, mock_deps: tuple[MagicMock, ...]
) -> None:
    """测试常规鼠标及按键方法调用链。"""
    mock_input = mock_deps[0]

    await base_window.mouse_move(Point(100, 200))
    mock_input.mouse_move.assert_called_once()

    mock_input.reset_mock()
    await base_window.mouse_move_relative(10, -20)
    mock_input.mouse_move_relative.assert_called_once_with(10, -20)

    await base_window.key_press(0x0D, duration_sec=0.01)
    assert mock_input.key_down.called
    assert mock_input.key_up.called


@pytest.mark.anyio
async def test_window_explicit_activate_and_key_press() -> None:
    """测试 Window 提供显式 activate() 方法，且 key_press 不进行隐式副作用。"""
    from sys_input import Win32HardwareBackend

    mock_input = MagicMock(spec=Win32HardwareBackend)
    mock_input.key_down = AsyncMock()
    mock_input.key_up = AsyncMock()

    win = Window(
        input_backend=mock_input,
        vision_backend=AsyncMock(),
        template_matcher=AsyncMock(),
        ocr_engine=AsyncMock(),
        width=800,
        height=600,
        hwnd=0x1234,
    )

    win.activate()
    await win.key_press(0x78)  # VK_F9
    assert mock_input.key_down.called


@pytest.mark.anyio
async def test_bell_move_steps_easing(
    base_window: Window, mock_deps: tuple[MagicMock, ...]
) -> None:
    """测试 bell_move_steps 产出 smoothstep 钟形插值轨迹。"""
    mock_input = mock_deps[0]
    mock_input.reset_mock()

    start = Point(x=0, y=0)
    target = Point(x=100, y=0)
    await base_window.bell_move_steps(start, target, steps=10, duration_sec=0.0)

    # 10 步 -> 10 次底层 mouse_move
    assert mock_input.mouse_move.call_count == 10
    xs = [call.args[0].x for call in mock_input.mouse_move.call_args_list]
    # 单调递增 (钟形位置不回退)
    assert all(xs[i] <= xs[i + 1] for i in range(len(xs) - 1))
    # smoothstep(0.5)=0.5 -> 第 5 步 (i=5, r=0.5) 落在半距 50
    assert xs[4] == 50
    # 末步到达目标
    assert xs[-1] == 100


@pytest.mark.anyio
async def test_smooth_mouse_move_interpolation(
    base_window: Window, mock_deps: tuple[MagicMock, ...]
) -> None:
    """测试 smooth_mouse_move 从当前系统光标位置钟形插值到目标。"""
    mock_input = mock_deps[0]
    mock_input.reset_mock()

    # base_window 无 hwnd -> get_sys_cursor_client_pos 返回 None -> start=Point(0,0)
    await base_window.smooth_mouse_move(Point(x=100, y=200), steps=10, duration_sec=0.0)

    # bell 步进 10 次；闭环因 hwnd=0 (get_sys_cursor_client_pos=None) 立即 break
    assert mock_input.mouse_move.call_count == 10
    last = mock_input.mouse_move.call_args_list[-1].args[0]
    assert last.x == 100
    assert last.y == 200
