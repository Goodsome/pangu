from typing import ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="D4_LEADERBOARD_",
        extra="ignore",
    )

    db_url: str = Field(
        ...,
        validation_alias="D4_LEADERBOARD_DB_URL",
        description="PostgreSQL 数据库连接字符串",
    )
