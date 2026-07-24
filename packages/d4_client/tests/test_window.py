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
from d4_client import D4Window, MatchResult, Point, Region
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


@pytest.mark.anyio
async def test_capture(d4_window: D4Window, mock_deps: tuple[MagicMock, ...]) -> None:
    """测试画面捕获与领域模型包装。"""
    img = await d4_window.capture()
    assert img.width == 10
    assert mock_deps[1].capture.called


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
