from pathlib import Path
from pydantic import PostgresDsn
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Shared kernel application settings."""

    database_url: PostgresDsn | None = Field(
        default=None, description="PostgreSQL Database Connection String"
    )
    redis_url: str
        
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
