"""d4_client 天梯榜与玩家配置页面物理布局配置。"""

from __future__ import annotations

from dataclasses import dataclass

from client_core import RelativeRegion


@dataclass(frozen=True)
class LeaderboardLayoutConfig:
    """天梯榜与玩家配置页面强类型相对物理布局配置 (基于 RelativeRegion 相对物理坐标解算)。"""

    title_roi: RelativeRegion = RelativeRegion(
        x=0.0277, y=0.0160, width=0.0371, height=0.0291
    )
    class_selector_roi: RelativeRegion = RelativeRegion(
        x=0.1362, y=0.0762, width=0.2751, height=0.0592
    )
    records_roi: RelativeRegion = RelativeRegion(
        x=0.3377, y=0.3882, width=0.4248, height=0.3992
    )
    row_manu_roi: RelativeRegion = RelativeRegion(
        x=0.3794, y=0.2832, width=0.2370, height=0.4325
    )
    view_config_roi: RelativeRegion = RelativeRegion(
        x=0.3904, y=0.3811, width=0.2077, height=0.0421
    )
    next_page_roi: RelativeRegion = RelativeRegion(
        x=0.4870, y=0.8716, width=0.0167, height=0.0381
    )
    previous_page_roi: RelativeRegion = RelativeRegion(
        x=0.4588, y=0.8716, width=0.0209, height=0.0411
    )
    page_number_roi: RelativeRegion = RelativeRegion(
        x=0.5104, y=0.8766, width=0.0381, height=0.0301
    )
    config_viewer_title_roi: RelativeRegion = RelativeRegion(
        x=0.7923, y=0.0772, width=0.0736, height=0.0331
    )
    close_config_viewer_roi: RelativeRegion = RelativeRegion(x=0.9807, y=0.0532, width=0.0146, height=0.0311)
    equipment_roi: RelativeRegion = RelativeRegion(
        x=0.6827, y=0.1861, width=0.2923, height=0.1769
    )
    equipment_01_roi: RelativeRegion = RelativeRegion(
        x=0.49, y=0.05, width=0.1874, height=0.7011
    )

    skill_roi: RelativeRegion = RelativeRegion(
        x=0.7265, y=0.4356, width=0.2035, height=0.0654
    )
    skill_01_roi: RelativeRegion = RelativeRegion(
        x=0.6451, y=0.5562, width=0.1994, height=0.2270
    )
    talismans_roi: RelativeRegion = RelativeRegion(
        x=0.7380, y=0.7597, width=0.1816, height=0.0521
    )
    talismans_01_roi: RelativeRegion = RelativeRegion(
        x=0.5543, y=0.0685, width=0.17, height=0.7720
    )

    title_text: str = "天梯榜"
