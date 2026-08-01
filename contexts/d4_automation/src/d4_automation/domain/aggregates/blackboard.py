from dataclasses import dataclass, field
from pathlib import Path

from d4_client import D4Client, D4Panel


@dataclass
class LeaderboardCaptureContext:
    """天梯榜采集会话上下文，存储当前进度状态。"""

    player_class: str = "野蛮人"
    current_page: int = 1
    target_end_page: int = 100
    current_row: int = 0  # 当前处理的行索引 (0-9)
    current_rank: int = 1  # 当前行对应的全局排名（页数×10 + 行索引）
    output_base_dir: Path = field(default_factory=lambda: Path("output/screenshots"))

    @property
    def has_more_rows(self) -> bool:
        """当前页是否还有未处理的行。"""
        return self.current_row < 10

    @property
    def has_more_pages(self) -> bool:
        """是否还需要采集更多页。"""
        return self.current_page <= self.target_end_page

    def advance_row(self) -> None:
        """移至下一行，并更新全局排名。"""
        self.current_row += 1
        self.current_rank += 1

    def advance_page(self) -> None:
        """翻页：重置行索引，页码递增。"""
        self.current_page += 1
        self.current_row = 0

    def page_output_dir(self) -> Path:
        """当前页的输出目录。"""
        return (
            self.output_base_dir / self.player_class / f"page_{self.current_page:03d}"
        )

    def rank_output_dir(self) -> Path:
        """当前行（排名）的输出目录。"""
        return self.page_output_dir() / f"rank_{self.current_rank:03d}"


@dataclass
class Blackboard:
    client: D4Client
    current_panel: D4Panel
    leaderboard: LeaderboardCaptureContext = field(
        default_factory=LeaderboardCaptureContext
    )

    def update_panel(self, panel: D4Panel) -> None:
        self.current_panel = panel
