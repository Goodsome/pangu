"""cv_engine OcrEngine 单元测试套件。"""

from dataclasses import is_dataclass
from unittest.mock import MagicMock

import numpy as np
import pytest

from cv_engine import (
    IOCREngine,
    OcrEngine,
    OcrResult,
    Point,
    Region,
)


@pytest.fixture
def mock_paddle_app() -> MagicMock:
    """构造 Mock 的 PaddleOCR APP 实例。"""
    mock_app = MagicMock()
    # 模拟 PaddleOCR 返回结构: [[[ [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], ("文本", 置信度) ]]]
    mock_app.ocr.return_value = [
        [
            [[[10.0, 20.0], [100.0, 20.0], [100.0, 50.0], [10.0, 50.0]], ("属性面板", 0.98)],
            [[[150.0, 200.0], [250.0, 200.0], [250.0, 230.0], [150.0, 230.0]], ("等级 100", 0.91)],
        ]
    ]
    return mock_app


@pytest.fixture
def ocr_engine(mock_paddle_app: MagicMock) -> OcrEngine:
    """构造以 Mock 依赖注入的 OcrEngine 实例。"""
    return OcrEngine(ocr_instance=mock_paddle_app)


def test_ocr_result_dataclass() -> None:
    """测试 OcrResult 模型中心计算与属性。"""
    assert is_dataclass(OcrResult)

    pts = (Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10))
    res = OcrResult(
        text="测试文本",
        confidence=0.99,
        rect=Region(x=10, y=20, width=100, height=40),
        box_points=pts,
    )
    assert res.text == "测试文本"
    assert res.confidence == 0.99
    assert res.center == Point(x=60, y=40)
    assert res.box_points == pts


def test_ocr_engine_protocol(ocr_engine: OcrEngine) -> None:
    """测试 OcrEngine 实现了 IOCREngine Protocol。"""
    assert isinstance(ocr_engine, IOCREngine)


def test_ocr_recognize_full_scene(ocr_engine: OcrEngine) -> None:
    """测试同步全图识别。"""
    scene = np.zeros((300, 300, 3), dtype=np.uint8)
    results = ocr_engine.ocr(scene, confidence_threshold=0.5)

    assert len(results) == 2
    assert results[0].text == "属性面板"
    assert results[0].rect == Region(x=10, y=20, width=90, height=30)
    assert results[0].center == Point(x=55, y=35)

    assert results[1].text == "等级 100"
    assert results[1].rect == Region(x=150, y=200, width=100, height=30)
    assert results[1].center == Point(x=200, y=215)


def test_ocr_with_roi_offset(ocr_engine: OcrEngine) -> None:
    """测试指定 ROI 区域识别时的坐标偏移量计算。"""
    scene = np.zeros((500, 500, 3), dtype=np.uint8)
    roi = Region(x=100, y=100, width=300, height=300)

    results = ocr_engine.ocr(scene, roi=roi)

    assert len(results) == 2
    # 原识别框 1: (10, 20) -> 叠加 ROI (100, 100) 偏移后: (110, 120)
    assert results[0].rect.x == 110
    assert results[0].rect.y == 120
    assert results[0].center == Point(x=155, y=135)


def test_find_text(ocr_engine: OcrEngine) -> None:
    """测试在图中检索特定文本。"""
    scene = np.zeros((300, 300, 3), dtype=np.uint8)

    # 模糊包含搜索
    item = ocr_engine.find_text(scene, target_text="等级")
    assert item is not None
    assert item.text == "等级 100"

    # 精确匹配搜索
    exact_item = ocr_engine.find_text(scene, target_text="属性面板", exact_match=True)
    assert exact_item is not None
    assert exact_item.text == "属性面板"

    # 查找不存在的文本
    none_item = ocr_engine.find_text(scene, target_text="不存在词汇")
    assert none_item is None


@pytest.mark.anyio
async def test_async_ocr_methods(ocr_engine: OcrEngine) -> None:
    """测试 async_ocr 与 async_find_text 异步方法。"""
    scene = np.zeros((300, 300, 3), dtype=np.uint8)

    results = await ocr_engine.async_ocr(scene)
    assert len(results) == 2

    item = await ocr_engine.async_find_text(scene, target_text="属性面板")
    assert item is not None
    assert item.center == Point(x=55, y=35)
