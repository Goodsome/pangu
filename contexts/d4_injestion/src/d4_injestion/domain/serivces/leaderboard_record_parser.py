"""榜单整页 OCR 结果解析领域服务。

将一张榜单整页截图的 OCR 文本块列表，按行 (y 坐标聚类) 还原为多条
``LeaderboardRecord``。每行包含: 玩家名 / tier / 用时 / 时间戳 四列。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord
from d4_injestion.domain.value_objects.leaderboard_screenshot import (
    LeaderboardScreenshot,
)
from d4_injestion.domain.value_objects.ocr_text_block import OcrTextBlock
from d4_injestion.domain.serivces.occurred_at_parser import OccurredAtParser


@dataclass
class LeaderboardRecordParser:
    """榜单整页 OCR 文本块 -> ``LeaderboardRecord`` 列表解析器。"""

    occurred_at_parser: OccurredAtParser = field(default_factory=OccurredAtParser)

    def parse(
        self,
        blocks: list[OcrTextBlock],
        screenshot: LeaderboardScreenshot,
    ) -> list[LeaderboardRecord]:
        """解析单页榜单的 OCR 文本块为记录列表。

        Args:
            blocks: 一张榜单整页截图的全部 OCR 文本块。
            screenshot: 该截图的定位信息 (提供 player_class)。
        """
        ...

    def _parse_duration_ms(self, raw: str) -> int:
        """将 ``m:ss.mmm`` 格式用时文本解析为毫秒整数。"""
        ...
