"""client_core 数据模型单元测试套件。"""

import pytest

from cv_engine import (
    MatchResult as CVMatchResult,
    Point as CVPoint,
    Region as CVRegion,
)
from client_core.models import (
    BaseRegion,
    ImageFrame,
    MatchResult,
    Point,
    Region,
    RelativePoint,
    RelativeRegion,
    SplitMode,
)


def test_models_conversion() -> None:
    """测试坐标与区域模型转换。"""
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
    match_res = MatchResult.from_cv_engine(cv_res)
    assert match_res.score == 0.9
    assert isinstance(match_res.rect, Region)

    frame_zero_stride = ImageFrame(
        data=b"\x00" * 400,
        width=10,
        height=10,
        channels=4,
        stride=0,
    )
    assert frame_zero_stride.mat.shape == (10, 10, 4)


def test_relative_region() -> None:
    """测试 RelativeRegion 的相对比例坐标转换。"""
    rel_rect = RelativeRegion(x=0.1, y=0.2, width=0.5, height=0.4)
    resolved = rel_rect.to_absolute(1920, 1080)
    assert resolved == Region(x=192, y=216, width=960, height=432)

    full_rel = RelativeRegion(x=0.0, y=0.0, width=1.0, height=1.0)
    assert full_rel.to_absolute(1920, 1080) == Region(x=0, y=0, width=1920, height=1080)


def test_region_split() -> None:
    """测试 Region.split (继承自 BaseRegion) 按 SplitMode 枚举方向切分能力。"""
    region = Region(x=10, y=20, width=100, height=30)
    assert isinstance(region, BaseRegion)

    rows = region.split(n=3, mode=SplitMode.VERTICAL)
    assert len(rows) == 3
    assert rows[0] == Region(x=10, y=20, width=100, height=10)
    assert rows[1] == Region(x=10, y=30, width=100, height=10)
    assert rows[2] == Region(x=10, y=40, width=100, height=10)

    cols = region.split(n=4, mode=SplitMode.HORIZONTAL)
    assert len(cols) == 4
    assert cols[0] == Region(x=10, y=20, width=25, height=30)

    with pytest.raises(ValueError, match="n 必须大于等于 1"):
        region.split(n=0)


def test_relative_point() -> None:
    """测试 RelativePoint 的相对比例坐标转换。"""
    rel_pt = RelativePoint(x=0.5, y=0.5)
    abs_pt = rel_pt.to_absolute(1920, 1080)
    assert abs_pt == Point(x=960, y=540)

    conv_rel = RelativePoint.from_absolute(Point(960, 540), 1920, 1080)
    assert conv_rel.x == 0.5 and conv_rel.y == 0.5
