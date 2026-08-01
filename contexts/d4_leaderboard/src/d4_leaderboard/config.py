from pathlib import Path
from typing import ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=str(Path.home() / ".pangu" / ".env"),
        env_file_encoding="utf-8",
        env_prefix="D4_LEADERBOARD_",
        extra="ignore",
    )

    db_url: str = Field(
        ...,
        description="PostgreSQL 数据库连接字符串",
    )
