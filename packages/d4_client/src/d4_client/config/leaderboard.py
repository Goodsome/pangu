"""d4_client 天梯榜页面坐标配置加载器。

从 leaderboard.yaml 加载坐标数据，供 LeaderboardScreen 与 PlayerConfigScreen 使用。
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from typing import Any

import yaml

from d4_client.models import Point, Region, RelativeRegion

# 配置文件路径（与本模块同目录）
_CONFIG_PATH = Path(__file__).parent / "leaderboard.yaml"

@dataclass(frozen=True)
class LeaderboardLayoutConfig:
    """新版天梯榜页面布局配置 (基于 RelativeRegion 相对物理坐标解算)。"""

    title_roi: RelativeRegion = RelativeRegion(
        x=0.0277, y=0.0160, width=0.0371, height=0.0291
    )
    class_selector_roi: RelativeRegion = RelativeRegion(
        x=0.1362, y=0.0762, width=0.2751, height=0.0592
    )
    records_roi: RelativeRegion = RelativeRegion(x=0.3377, y=0.3882, width=0.4248, height=0.3992)
    view_config_roi: RelativeRegion = RelativeRegion(x=0.3904, y=0.3811, width=0.2077, height=0.0421)
    next_page_roi: RelativeRegion = RelativeRegion(x=0.4870, y=0.8716, width=0.0167, height=0.0381)
    last_page_roi: RelativeRegion = RelativeRegion(x=0.4588, y=0.8716, width=0.0209, height=0.0411)
    title_text: str = "天梯榜"


# ---------------------------------------------------------------------------
# 玩家配置页槽位配置 (暂存)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SlotConfig:
    """单个悬停槽位配置。"""

    name: str
    hover: Point


@dataclass(frozen=True)
class TooltipConfig:
    """Tooltip 截图区域策略配置。"""

    strategy: str  # "fixed_left" | "near_cursor"
    fixed_region: Region
    cursor_offset: tuple[int, int]
    cursor_size: tuple[int, int]


@dataclass(frozen=True)
class PlayerConfigLayoutConfig:
    """玩家配置页面布局配置。"""

    close_btn: Point
    tooltip: TooltipConfig
    equipment_slots: list[SlotConfig]
    skill_slots: list[SlotConfig]
    paragon_slots: list[SlotConfig]
    amulet_slots: list[SlotConfig]
    title_roi: RelativeRegion
    title_text: str


@dataclass(frozen=True)
class ViewConfigButtonConfig:
    """'查看配置'按钮定位策略配置。"""

    strategy: str  # "template" | "offset"
    template: Path
    offset: tuple[int, int]


@dataclass(frozen=True)
class LeaderboardLayoutConfigLegacy:
    """旧版天梯榜页面布局配置 (过渡用)。"""

    records_region: Region
    row_click_points: list[Point]
    view_config_button: ViewConfigButtonConfig
    next_page_btn: Point
    class_buttons: dict[str, Point]
    title_roi: RelativeRegion
    title_text: str
    page_number_roi: Region
    row_count: int


# ---------------------------------------------------------------------------
# 顶层聚合配置
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LeaderboardConfig:
    """leaderboard.yaml 完整解析结果。"""

    leaderboard: LeaderboardLayoutConfigLegacy
    player_config: PlayerConfigLayoutConfig


# ---------------------------------------------------------------------------
# 解析函数
# ---------------------------------------------------------------------------


def _parse_point(raw: list[int]) -> Point:
    return Point(x=raw[0], y=raw[1])


def _parse_region(raw: list[int]) -> Region:
    return Region(x=raw[0], y=raw[1], width=raw[2], height=raw[3])


def _parse_relative_region(raw: list[float]) -> RelativeRegion:
    return RelativeRegion(x=raw[0], y=raw[1], width=raw[2], height=raw[3])


def _parse_slot_list(raw: Any) -> list[SlotConfig]:
    return [
        SlotConfig(name=str(s["name"]), hover=_parse_point(s["hover"])) for s in raw
    ]


def _parse_leaderboard_layout(raw: Any) -> LeaderboardLayoutConfigLegacy:
    vcb = raw["view_config_button"]
    return LeaderboardLayoutConfigLegacy(
        records_region=_parse_region(raw["records_region"]),
        row_click_points=[_parse_point(p) for p in raw["row_click_points"]],
        view_config_button=ViewConfigButtonConfig(
            strategy=vcb["strategy"],
            template=_CONFIG_PATH.parent / vcb["template"],
            offset=tuple(vcb["offset"]),
        ),
        next_page_btn=_parse_point(raw["next_page_btn"]),
        class_buttons={k: _parse_point(v) for k, v in raw["class_buttons"].items()},
        title_roi=_parse_relative_region(raw["title_roi"]),
        title_text=str(raw["title_text"]),
        page_number_roi=_parse_region(raw["page_number_roi"]),
        row_count=int(raw["row_count"]),
    )


def _parse_player_config_layout(raw: Any) -> PlayerConfigLayoutConfig:
    tt = raw["tooltip"]
    return PlayerConfigLayoutConfig(
        close_btn=_parse_point(raw["close_btn"]),
        tooltip=TooltipConfig(
            strategy=str(tt["strategy"]),
            fixed_region=_parse_region(tt["fixed_region"]),
            cursor_offset=tuple(tt["cursor_offset"]),
            cursor_size=tuple(tt["cursor_size"]),
        ),
        equipment_slots=_parse_slot_list(raw["equipment_slots"]),
        skill_slots=_parse_slot_list(raw["skill_slots"]),
        paragon_slots=_parse_slot_list(raw["paragon_slots"]),
        amulet_slots=_parse_slot_list(raw["amulet_slots"]),
        title_roi=_parse_relative_region(raw["title_roi"]),
        title_text=str(raw["title_text"]),
    )


@lru_cache(maxsize=1)
def load_leaderboard_config(config_path: Path = _CONFIG_PATH) -> LeaderboardConfig:
    """加载并缓存天梯榜 YAML 配置（进程内单例）。"""
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return LeaderboardConfig(
        leaderboard=_parse_leaderboard_layout(data["leaderboard"]),
        player_config=_parse_player_config_layout(data["player_config"]),
    )
