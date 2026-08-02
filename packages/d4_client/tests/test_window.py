"""D4Window 防腐层与数据映射单元测试套件。"""

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from cv_engine import (
    MatchResult as CVMatchResult,
    OcrResult as CVOcrResult,
    Point as CVPoint,
    Region as CVRegion,
)
from d4_client import D4Window, MatchResult, Point, Region, RelativeRegion
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
def d4_window(
    mock_deps: tuple[MagicMock, MagicMock, MagicMock, MagicMock],
) -> D4Window:
    """创建防腐隔离的 D4Window 实例。"""
    mock_input, mock_vision, mock_matcher, mock_ocr = mock_deps
    return D4Window(
        input_backend=mock_input,
        vision_backend=mock_vision,
        template_matcher=mock_matcher,
        ocr_engine=mock_ocr,
        width=1920,
        height=1080,
    )


def test_models_conversion() -> None:
    """测试防腐层数据模型转换。"""
    pt = Point(x=10, y=20)
    sys_pt = pt.to_sys_input()
    assert sys_pt.x == 10 and sys_pt.y == 20

    cv_pt = pt.to_cv_engine()
    assert cv_pt.x == 10 and cv_pt.y == 20

    rect = Region(x=5, y=5, width=10, height=20)
    assert rect.center == Point(x=10, y=15)
    vision_rect = rect.to_vision_stream()
    assert vision_rect.width == 10

    cv_res = CVMatchResult(score=0.9, rect=CVRegion(x=0, y=0, width=10, height=10))
    d4_res = MatchResult.from_cv_engine(cv_res)
    assert d4_res.score == 0.9
    assert isinstance(d4_res.rect, Region)

    # 测试 ImageFrame 提取 mat 且 stride==0 时正确容错
    from d4_client.models import ImageFrame

    frame_zero_stride = ImageFrame(
        data=b"\x00" * 400,
        width=10,
        height=10,
        channels=4,
        stride=0,
    )
    assert frame_zero_stride.mat.shape == (10, 10, 4)


def test_relative_region() -> None:
    """测试 RelativeRegion 的 0~1 相对比例坐标转换。"""
    rel_rect = RelativeRegion(x=0.1, y=0.2, width=0.5, height=0.4)
    resolved = rel_rect.to_absolute(1920, 1080)
    assert resolved == Region(x=192, y=216, width=960, height=432)

    full_rel = RelativeRegion(x=0.0, y=0.0, width=1.0, height=1.0)
    assert full_rel.to_absolute(1920, 1080) == Region(x=0, y=0, width=1920, height=1080)


def test_relative_point() -> None:
    """测试 RelativePoint 的 0~1 相对比例坐标转换。"""
    from d4_client.models import RelativePoint

    rel_pt = RelativePoint(x=0.5, y=0.5)
    abs_pt = rel_pt.to_absolute(1920, 1080)
    assert abs_pt == Point(x=960, y=540)

    conv_rel = RelativePoint.from_absolute(Point(960, 540), 1920, 1080)
    assert conv_rel.x == 0.5 and conv_rel.y == 0.5



@pytest.mark.anyio
async def test_capture(d4_window: D4Window, mock_deps: tuple[MagicMock, ...]) -> None:
    """测试画面捕获与领域模型包装 (含相对 ROI 解算)。"""
    # 无 roi
    img = await d4_window.capture()
    assert img.width == 10
    assert mock_deps[1].capture.called

    # 传入 0~1 相对 RelativeRegion ROI
    rel_roi = RelativeRegion(x=0.1, y=0.2, width=0.5, height=0.4)
    await d4_window.capture(region=rel_roi)
    # mock_deps[1].capture 被调用时接收转换后的 VisionRegion(x=192, y=216, width=960, height=432)
    last_call_args = mock_deps[1].capture.call_args
    passed_vision_region = last_call_args.kwargs["region"]
    assert passed_vision_region.x == 192
    assert passed_vision_region.y == 216
    assert passed_vision_region.width == 960
    assert passed_vision_region.height == 432


@pytest.mark.anyio
async def test_match_and_click(
    d4_window: D4Window, mock_deps: tuple[MagicMock, ...]
) -> None:
    """测试模板匹配并点击。"""
    mock_matcher = mock_deps[2]
    mock_input = mock_deps[0]

    mock_matcher.async_match_best.return_value = CVMatchResult(
        score=0.95,
        rect=CVRegion(x=10, y=20, width=40, height=30),
    )

    dummy_template = np.zeros((10, 10), dtype=np.uint8)
    success = await d4_window.match_and_click(
        template=dummy_template, button=MouseButton.LEFT
    )

    assert success is True
    assert mock_input.mouse_click.called


@pytest.mark.anyio
async def test_find_text_and_click(
    d4_window: D4Window, mock_deps: tuple[MagicMock, ...]
) -> None:
    """测试查找特定文本并点击。"""
    mock_ocr = mock_deps[3]
    mock_input = mock_deps[0]

    pts = (CVPoint(0, 0), CVPoint(10, 0), CVPoint(10, 10), CVPoint(0, 10))
    mock_ocr.async_find_text.return_value = CVOcrResult(
        text="进入游戏",
        confidence=0.98,
        rect=CVRegion(x=100, y=200, width=80, height=30),
        box_points=pts,
    )

    success = await d4_window.find_text_and_click(target_text="进入游戏")

    assert success is True
    assert mock_input.mouse_click.called


@pytest.mark.anyio
async def test_async_input_methods(
    d4_window: D4Window, mock_deps: tuple[MagicMock, ...]
) -> None:
    """测试异步输入代理方法。"""
    mock_input = mock_deps[0]

    await d4_window.mouse_move(Point(10, 20))
    assert mock_input.mouse_move.called

    await d4_window.mouse_click(Point(10, 20))
    assert mock_input.mouse_click.called

    await d4_window.key_press(65, duration_sec=0.01)
    assert mock_input.key_down.called
    assert mock_input.key_up.called

    await d4_window.scroll(120)
    assert mock_input.scroll.called

    await d4_window.mouse_down(Point(10, 20))
    assert mock_input.mouse_down.called

    await d4_window.mouse_up(Point(10, 20))
    assert mock_input.mouse_up.called


def test_window_dimensions(mock_deps: tuple[MagicMock, ...]) -> None:
    """测试 D4Window 实例化时显式传入 width 和 height 字段。"""
    mock_input, mock_vision, mock_matcher, mock_ocr = mock_deps

    custom_window = D4Window(
        input_backend=mock_input,
        vision_backend=mock_vision,
        template_matcher=mock_matcher,
        ocr_engine=mock_ocr,
        width=1280,
        height=720,
    )
    assert custom_window.width == 1280
    assert custom_window.height == 720


@pytest.mark.anyio
async def test_select_roi(
    d4_window: D4Window, monkeypatch: pytest.MonkeyPatch
) -> None:
    """测试基于 OpenCV 交互框选获取绝对 Region 和相对 RelativeRegion。"""
    mock_select_roi = MagicMock(return_value=(192, 216, 960, 432))
    mock_destroy_window = MagicMock()

    import cv2
    monkeypatch.setattr(cv2, "selectROI", mock_select_roi)
    monkeypatch.setattr(cv2, "destroyWindow", mock_destroy_window)

    # 1. 测试 select_roi 获取绝对像素 Region
    abs_region = await d4_window.select_roi(window_name="Test OpenCV ROI")
    assert abs_region == Region(x=192, y=216, width=960, height=432)
    assert mock_select_roi.called
    assert mock_destroy_window.called

    # 2. 测试 select_relative_roi 获取 RelativeRegion (1920x1080 屏幕)
    rel_region = await d4_window.select_relative_roi(window_name="Test OpenCV Relative ROI")
    assert rel_region == RelativeRegion(x=0.1, y=0.2, width=0.5, height=0.4)


@pytest.mark.anyio
async def test_image_frame_save(tmp_path: Path) -> None:
    """测试 ImageFrame.save 异步保存为磁盘图片文件。"""
    from d4_client.models import ImageFrame

    frame = ImageFrame(
        data=b"\x00" * 400,
        width=10,
        height=10,
        channels=4,
    )
    save_file = tmp_path / "sub_dir" / "test_frame.png"
    await frame.save(save_file)

    assert save_file.exists()
    assert save_file.stat().st_size > 0

