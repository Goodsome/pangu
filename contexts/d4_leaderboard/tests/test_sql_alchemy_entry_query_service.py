import contextlib
import typing
import uuid
from typing import cast
from unittest.mock import AsyncMock, MagicMock
import pytest

from d4_leaderboard.application.dtos.entry_filter import EntryFilter
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.infrastructure.persistence.models.entry_model import EntryModel
from d4_leaderboard.infrastructure.persistence.repositories.sql_alchemy_entry_query_service import (
    SqlAlchemyEntryQueryService,
)
from foundation.common_types.page import PageQuery
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_get_entry_success() -> None:
    test_uuid = uuid.uuid4()
    entry_id = EntryId.reconstitute(test_uuid)
    mock_model = EntryModel(id=test_uuid, name="test")

    mock_session = AsyncMock(spec=AsyncSession)
    get_mock = cast(AsyncMock, mock_session.get)
    get_mock.return_value = mock_model

    @contextlib.asynccontextmanager
    async def mock_session_factory():
        yield mock_session

    service = SqlAlchemyEntryQueryService(
        session_factory=cast(typing.Any, mock_session_factory)
    )

    dto = await service.get(entry_id)
    assert dto.id == test_uuid
    get_mock.assert_called_once_with(EntryModel, test_uuid)


@pytest.mark.anyio
async def test_get_entry_not_found() -> None:
    entry_id = EntryId.create()

    mock_session = AsyncMock(spec=AsyncSession)
    get_mock = cast(AsyncMock, mock_session.get)
    get_mock.return_value = None

    @contextlib.asynccontextmanager
    async def mock_session_factory():
        yield mock_session

    service = SqlAlchemyEntryQueryService(
        session_factory=cast(typing.Any, mock_session_factory)
    )

    with pytest.raises(ValueError, match="not found"):
        _ = await service.get(entry_id)


@pytest.mark.anyio
async def test_find_by_query() -> None:
    mock_session = AsyncMock(spec=AsyncSession)

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 2

    test_uuid_1 = uuid.uuid4()
    test_uuid_2 = uuid.uuid4()
    mock_model1 = EntryModel(id=test_uuid_1, name="test1")
    mock_model2 = EntryModel(id=test_uuid_2, name="test2")

    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value.all.return_value = [
        mock_model1,
        mock_model2,
    ]

    execute_mock = cast(AsyncMock, mock_session.execute)
    execute_mock.side_effect = [mock_count_result, mock_items_result]

    @contextlib.asynccontextmanager
    async def mock_session_factory():
        yield mock_session

    service = SqlAlchemyEntryQueryService(
        session_factory=cast(typing.Any, mock_session_factory)
    )

    page_query = PageQuery[EntryFilter](
        current=1,
        size=10,
        condition=EntryFilter(),
    )

    page = await service.find_by_query(page_query)
    assert page.total == 2
    assert page.current == 1
    assert page.size == 10
    assert len(page.items) == 2
    assert page.items[0].id == test_uuid_1
    assert page.items[1].id == test_uuid_2
