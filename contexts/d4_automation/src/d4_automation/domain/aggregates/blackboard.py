from dataclasses import dataclass, field
from pathlib import Path

from d4_client import D4Client, D4Panel


@dataclass
class LeaderboardCaptureContext:
    """天梯榜采集会话上下文，存储任务终止条件和输出路径。"""

    target_end_page: int = 100
    output_base_dir: Path = field(default_factory=lambda: Path("output/screenshots"))


@dataclass
class Blackboard:
    client: D4Client
    current_panel: D4Panel
    leaderboard: LeaderboardCaptureContext = field(
        default_factory=LeaderboardCaptureContext
    )

    def update_panel(self, panel: D4Panel) -> None:
        self.current_panel = panel
