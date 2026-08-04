"""截图发现端口：枚举待注入的榜单整页截图。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from d4_injestion.domain.value_objects.leaderboard_screenshot import (
    LeaderboardScreenshot,
)


class ScreenshotDiscoverer(ABC):
    """榜单截图发现器端口。"""

    @abstractmethod
    def discover(self, base_dir: Path) -> list[LeaderboardScreenshot]:
        """扫描基准目录下的全部榜单整页截图。

        约定目录结构: ``{base_dir}/{CLASS}/leaderboard_{page:03d}.png``

        Args:
            base_dir: 截图根目录 (如 ``output/screenshots``)。
        """
        ...
