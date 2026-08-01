from pathlib import Path
from typing import ClassVar
from pydantic import PostgresDsn
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Shared kernel application settings."""

    database_url: PostgresDsn | None = Field(
        default=None, description="PostgreSQL Database Connection String"
    )
    redis_url: str | None = Field(default=None, description="Redis Connection String")
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=str(Path.home() / ".pangu" / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
