"""文件系统截图发现适配器。"""

from __future__ import annotations

from pathlib import Path
from typing import override

from d4_injestion.application.ports.screenshot_discoverer import ScreenshotDiscoverer
from d4_injestion.domain.value_objects.leaderboard_screenshot import (
    LeaderboardScreenshot,
)


class FilesystemScreenshotDiscoverer(ScreenshotDiscoverer):
    """扫描 ``{base_dir}/{CLASS}/leaderboard_{page:03d}.png`` 的适配器。"""

    @override
    def discover(self, base_dir: Path) -> list[LeaderboardScreenshot]:
        """枚举基准目录下全部职业子目录中的榜单整页截图。

        目录结构约定::

            {base_dir}/BARBARIAN/leaderboard_001.png
            {base_dir}/BARBARIAN/leaderboard_002.png
            ...

        Returns:
            按 (职业, 页码) 排序的截图列表。
        """
        ...
