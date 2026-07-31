import uuid
from typing import cast
from unittest.mock import AsyncMock, MagicMock
import pytest
from pydantic import ValidationError

from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.config import Settings
from d4_leaderboard.container import Container
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.infrastructure.persistence.models.entry_model import EntryModel
from d4_leaderboard.interfaces.api import D4LeaderboardApi
from foundation.message_bus.message_bus import AsyncBaseMessageBus
from foundation.persistence.sessions.sqlalchemy_session import AsyncSqlAlchemySession
from redis.asyncio import Redis


def test_container_initialization_with_override() -> None:
    mock_session_factory = MagicMock(
        return_value=MagicMock(spec=AsyncSqlAlchemySession)
    )
    mock_redis = MagicMock(spec=Redis)

    container = Container(
        session_factory=mock_session_factory,
        redis_client=mock_redis,
    )

    api = container.api()
    assert isinstance(api, D4LeaderboardApi)

    message_bus = container.message_bus()
    assert isinstance(message_bus, AsyncBaseMessageBus)


def test_container_settings_explicit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    custom_url = "postgresql+psycopg://d4_user:d4_pass@localhost:5432/d4_isolated_db"
    monkeypatch.setenv("D4_LEADERBOARD_DB_URL", custom_url)

    container = Container()
    assert container.settings().db_url == custom_url


def test_container_settings_missing_env_raises_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("D4_LEADERBOARD_DB_URL", raising=False)
    with pytest.raises(ValidationError):
        _ = Settings()  # pyright: ignore[reportCallIssue]


@pytest.mark.anyio
async def test_async_api_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "D4_LEADERBOARD_DB_URL", "postgresql+psycopg://user:pass@localhost:5432/db"
    )
    mock_session = AsyncMock(spec=AsyncSqlAlchemySession)
    mock_session_factory = MagicMock(return_value=mock_session)

    container = Container(session_factory=mock_session_factory)
    api = container.api()

    entry_dto = EntryDto(id=uuid.uuid4(), name="test")
    await api.create_entry(entry_dto)

    entry_id = EntryId.create()
    mock_model = EntryModel(id=uuid.uuid4(), name="test")
    get_mock = cast(AsyncMock, mock_session.get)
    get_mock.return_value = mock_model

    await api.update_entry(entry_id, entry_dto)
    await api.delete_entry(entry_id)
