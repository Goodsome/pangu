"""d4_injestion 依赖注入容器。

装配端口与 infrastructure 适配器, 并对外暴露 Use Case。
"""

from __future__ import annotations

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton

from d4_injestion.application.use_cases.injest_leaderboard_entries import (
    InjestLeaderboardEntries,
)
from d4_injestion.config import Settings
from d4_injestion.domain.serivces.leaderboard_record_parser import (
    LeaderboardRecordParser,
)
from d4_injestion.domain.serivces.occurred_at_parser import OccurredAtParser
from d4_injestion.infrastructure.adapters.cv2_image_loader import Cv2ImageLoader
from d4_injestion.infrastructure.adapters.cv_engine_ocr_scanner import (
    CvEngineOcrScanner,
)
from d4_injestion.infrastructure.adapters.filesystem_screenshot_discoverer import (
    FilesystemScreenshotDiscoverer,
)
from d4_injestion.infrastructure.adapters.http_leaderboard_entry_client import (
    HttpLeaderboardEntryClient,
)


class Container(DeclarativeContainer):
    """d4_injestion DI 容器。"""

    settings: Singleton[Settings] = Singleton(Settings)

    image_loader: Factory[Cv2ImageLoader] = Factory(Cv2ImageLoader)
    ocr_scanner: Factory[CvEngineOcrScanner] = Factory(CvEngineOcrScanner)
    discoverer: Factory[FilesystemScreenshotDiscoverer] = Factory(
        FilesystemScreenshotDiscoverer
    )
    occurred_at_parser: Factory[OccurredAtParser] = Factory(OccurredAtParser)
    parser: Factory[LeaderboardRecordParser] = Factory(
        LeaderboardRecordParser,
        occurred_at_parser=occurred_at_parser,
    )
    entry_client: Factory[HttpLeaderboardEntryClient] = Factory(
        HttpLeaderboardEntryClient,
        base_url=settings.provided.leaderboard_base_url,
    )

    injest_use_case: Factory[InjestLeaderboardEntries] = Factory(
        InjestLeaderboardEntries,
        image_loader=image_loader,
        ocr_scanner=ocr_scanner,
        discoverer=discoverer,
        parser=parser,
        entry_client=entry_client,
        ocr_confidence_threshold=settings.provided.ocr_confidence_threshold,
    )
