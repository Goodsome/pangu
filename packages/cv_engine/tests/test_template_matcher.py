"""cv_engine 模板匹配器单元测试套件。"""

from dataclasses import is_dataclass

import numpy as np
import pytest

from cv_engine import (
    InvalidImageError,
    ITemplateMatcher,
    MatchResult,
    Point,
    Region,
    TemplateMatcher,
    TemplateNotFoundError,
)


@pytest.fixture
def matcher() -> TemplateMatcher:
    """初始化 TemplateMatcher 测试实例。"""
    return TemplateMatcher()


def create_synthetic_scene_and_template() -> tuple[np.ndarray, np.ndarray, Point]:
    """生成带有非零方差特征纹理的测试场景与模板。

    背景 200x200 像素，包含在 (50, 60) 位置放置的 20x20 特征图案模板（有背景与前景差异）。
    """
    scene = np.zeros((200, 200), dtype=np.uint8)

    # 构造带有中心星号/方块特征的 20x20 模板
    template = np.zeros((20, 20), dtype=np.uint8)
    template[5:15, 5:15] = 255  # 有明显对比度方差

    target_x, target_y = 50, 60
    target_w, target_h = 20, 20

    # 放置到场景中
    scene[target_y : target_y + target_h, target_x : target_x + target_w] = template

    expected_center = Point(x=target_x + target_w // 2, y=target_y + target_h // 2)

    return scene, template, expected_center


def test_models_dataclass() -> None:
    """测试数据结构 Dataclasses。"""
    assert is_dataclass(Point)
    assert is_dataclass(Region)
    assert is_dataclass(MatchResult)

    rect = Region(x=10, y=20, width=40, height=50)
    assert rect.center == Point(x=30, y=45)
    assert rect.right == 50
    assert rect.bottom == 70

    res = MatchResult(score=0.95, rect=rect, template_name="test_item")
    assert res.center == Point(x=30, y=45)
    assert res.score == 0.95
    assert res.template_name == "test_item"


def test_template_matcher_protocol(matcher: TemplateMatcher) -> None:
    """测试 TemplateMatcher 实现了 ITemplateMatcher Protocol。"""
    assert isinstance(matcher, ITemplateMatcher)


def test_match_best_success(matcher: TemplateMatcher) -> None:
    """测试同步 match_best 能精准定位单目标。"""
    scene, template, expected_center = create_synthetic_scene_and_template()

    result = matcher.match_best(scene=scene, template=template, threshold=0.9)

    assert result is not None
    assert result.score >= 0.99
    assert result.center == expected_center
    assert result.rect.x == 50
    assert result.rect.y == 60
    assert result.rect.width == 20
    assert result.rect.height == 20


def test_match_best_with_roi(matcher: TemplateMatcher) -> None:
    """测试带 ROI 区域限制的 match_best 匹配。"""
    scene, template, expected_center = create_synthetic_scene_and_template()
    roi = Region(x=40, y=50, width=50, height=50)

    result = matcher.match_best(scene=scene, template=template, threshold=0.9, roi=roi)

    assert result is not None
    assert result.center == expected_center

    # 超出 ROI 区域的场景匹配应该未找到
    invalid_roi = Region(x=100, y=100, width=50, height=50)
    no_result = matcher.match_best(
        scene=scene, template=template, threshold=0.9, roi=invalid_roi
    )
    assert no_result is None


def test_match_multi_with_nms(matcher: TemplateMatcher) -> None:
    """测试多目标匹配与 NMS 去重功能。"""
    scene = np.zeros((300, 300), dtype=np.uint8)

    template = np.zeros((20, 20), dtype=np.uint8)
    template[5:15, 5:15] = 255

    # 绘制两处独立特征块
    scene[30:50, 30:50] = template
    scene[150:170, 150:170] = template

    results = matcher.match_multi(
        scene=scene, template=template, threshold=0.9, nms_threshold=0.3
    )

    assert len(results) == 2
    centers = [res.center for res in results]
    assert Point(x=40, y=40) in centers
    assert Point(x=160, y=160) in centers


@pytest.mark.anyio
async def test_async_match_best(matcher: TemplateMatcher) -> None:
    """测试异步 async_match_best 方法。"""
    scene, template, expected_center = create_synthetic_scene_and_template()

    result = await matcher.async_match_best(
        scene=scene, template=template, threshold=0.9
    )

    assert result is not None
    assert result.center == expected_center


@pytest.mark.anyio
async def test_async_match_multi(matcher: TemplateMatcher) -> None:
    """测试异步 async_match_multi 方法。"""
    scene = np.zeros((200, 200), dtype=np.uint8)
    template = np.zeros((10, 10), dtype=np.uint8)
    template[2:8, 2:8] = 255

    scene[10:20, 10:20] = template

    results = await matcher.async_match_multi(
        scene=scene, template=template, threshold=0.9
    )

    assert len(results) == 1
    assert results[0].center == Point(x=15, y=15)


def test_exceptions_handling(matcher: TemplateMatcher) -> None:
    """测试模板与图像异常捕获。"""
    with pytest.raises(TemplateNotFoundError):
        matcher.load_template("non_existent_file_path.png")

    with pytest.raises(InvalidImageError):
        matcher.match_best(
            scene=np.array([]), template=np.full((10, 10), 255, dtype=np.uint8)
        )
