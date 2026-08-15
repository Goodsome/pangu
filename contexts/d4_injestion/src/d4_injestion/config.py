"""d4_injestion 配置。"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """d4_injestion 运行配置 (环境变量前缀 ``D4_INJESTION_``)。"""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=str(Path.home() / ".pangu" / ".env"),
        env_file_encoding="utf-8",
        env_prefix="D4_INJESTION_",
        extra="ignore",
    )

    screenshots_base_dir: Path = Field(
        default=Path("output/screenshots"),
        description="截图根目录",
    )
    leaderboard_base_url: str = Field(
        default="http://localhost:8000",
        description="d4_leaderboard HTTP 服务基址",
    )
    helltides_base_url: str = Field(
        default="https://helltides.com",
        description="helltides.com 抓取基址",
    )
    ocr_confidence_threshold: float = Field(
        default=0.5,
        description="OCR 识别置信度过滤阈值",
    )
