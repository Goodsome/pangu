"""Use Case: 将 output/screenshots 下榜单截图 OCR 识别并注入 d4_leaderboard。

编排流程::

    discover(base_dir) -> [LeaderboardScreenshot]
    for screenshot in screenshots:
        image  = image_loader.load(screenshot.path)        # path -> ndarray
        blocks = ocr_scanner.scan(image)                    # ndarray -> OCR 文本块
        records = parser.parse(blocks, screenshot)          # 文本块 -> LeaderboardRecord
        for record in records:
            await entry_client.create_entry(record)         # HTTP POST /entries/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from d4_injestion.application.dtos.injestion_result import InjestionResult
from d4_injestion.application.ports.image_loader import ImageLoader
from d4_injestion.application.ports.leaderboard_entry_client import (
    LeaderboardEntryClient,
)
from d4_injestion.application.ports.ocr_scanner import OcrScanner
from d4_injestion.application.ports.screenshot_discoverer import ScreenshotDiscoverer
from d4_injestion.domain.serivces.leaderboard_record_parser import (
    LeaderboardRecordParser,
)

logger = logging.getLogger(__name__)


@dataclass
class InjestLeaderboardEntries:
    """榜单截图 OCR 识别与注入 Use Case。"""

    image_loader: ImageLoader
    ocr_scanner: OcrScanner
    discoverer: ScreenshotDiscoverer
    parser: LeaderboardRecordParser
    entry_client: LeaderboardEntryClient
    ocr_confidence_threshold: float = 0.5

    async def execute(self, base_dir: Path) -> InjestionResult:
        """执行完整的榜单截图识别与注入流程。

        Args:
            base_dir: 截图根目录 (如 ``output/screenshots``)。
        """
        ...

    async def _process_screenshot(self, screenshot: Path) -> None:
        """处理单张榜单截图: 加载 -> OCR -> 解析 -> 注入。"""
        ...

    async def _inject_record(self, record: object) -> None:
        """注入单条记录, 失败时记录错误而非中断整体流程。"""
        ...

    async def aclose(self) -> None:
        """释放注入客户端等资源。"""
        await self.entry_client.aclose()
