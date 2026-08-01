from pathlib import Path
from typing import ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pangu_cli.infrastructure.config import Settings as SharedSettings


class AppConfig(BaseSettings):
    """Top-level application configuration. 包含了 Project 级别的全局配置，并聚合了所有上下文的配置。"""
    
    shared: SharedSettings = Field(default_factory=SharedSettings)
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=str(Path.home() / ".pangu" / ".env"),
        env_file_encoding="utf-8",
        frozen=True,
        extra="ignore",
    )


def load_all_configurations() -> AppConfig:
    """实例化全局配置（会自动触发各级环境变量的读取）"""
    return AppConfig()
