import contextlib
import typing
from typing import cast
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest
from dependency_injector.providers import Factory
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from d4_leaderboard.container import Container
from d4_leaderboard.infrastructure.persistence.models.entry_model import EntryModel
from d4_leaderboard.infrastructure.persistence.repositories.sql_alchemy_entry_query_service import (
    SqlAlchemyEntryQueryService,
)
from d4_leaderboard.interfaces.http import router


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "D4_LEADERBOARD_DB_URL", "postgresql+psycopg://user:pass@localhost:5432/db"
    )


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def container(mock_session: AsyncMock) -> typing.Generator[Container, None, None]:
    mock_session_factory = MagicMock(return_value=mock_session)

    @contextlib.asynccontextmanager
    async def mock_query_session_maker():
        yield mock_session

    c = Container(session_factory=mock_session_factory)
    c.entry_query_service.override(
        Factory(
            SqlAlchemyEntryQueryService,
            session_factory=cast(typing.Any, mock_query_session_maker),
        )
    )
    c.wire(modules=["d4_leaderboard.interfaces.http"])
    yield c
    c.unwire()


@pytest.fixture
def app(container: Container) -> FastAPI:
    fastapi_app = FastAPI()
    fastapi_app.include_router(router)
    return fastapi_app


@pytest.mark.anyio
async def test_create_entry_endpoint(app: FastAPI) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/entries/",
            json={"name": "Test Entry"},
        )

    assert response.status_code == 201


@pytest.mark.anyio
async def test_get_entry_endpoint_success(
    app: FastAPI, mock_session: AsyncMock
) -> None:
    test_id = uuid.uuid4()
    mock_model = EntryModel(id=test_id, name="Found Entry")
    mock_session.get.return_value = mock_model

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/entries/{test_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_id)
    assert data["name"] == "Found Entry"


@pytest.mark.anyio
async def test_get_entry_endpoint_not_found(
    app: FastAPI, mock_session: AsyncMock
) -> None:
    mock_session.get.return_value = None
    test_id = uuid.uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/entries/{test_id}")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_entries_endpoint(app: FastAPI, container: Container) -> None:
    mock_query_service = AsyncMock()
    mock_query_service.find_by_query.return_value = {
        "items": [{"id": str(uuid.uuid4()), "name": "Item 1"}],
        "total": 1,
        "current": 1,
        "size": 10,
    }
    container.entry_query_service.override(mock_query_service)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/entries/?current=1&size=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


@pytest.mark.anyio
async def test_update_entry_endpoint(app: FastAPI, mock_session: AsyncMock) -> None:
    test_id = uuid.uuid4()
    mock_model = EntryModel(id=test_id, name="Updated Entry")
    mock_session.get.return_value = mock_model

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            f"/entries/{test_id}",
            json={"name": "Updated Entry"},
        )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_update_entry_endpoint_not_found(
    app: FastAPI, mock_session: AsyncMock
) -> None:
    mock_session.get.return_value = None
    test_id = uuid.uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            f"/entries/{test_id}",
            json={"name": "Nonexistent Entry"},
        )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_entry_endpoint(app: FastAPI, mock_session: AsyncMock) -> None:
    test_id = uuid.uuid4()
    mock_model = EntryModel(id=test_id, name="To Delete")
    mock_session.get.return_value = mock_model

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(f"/entries/{test_id}")

    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_entry_endpoint_not_found(
    app: FastAPI, mock_session: AsyncMock
) -> None:
    mock_session.get.return_value = None
    test_id = uuid.uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(f"/entries/{test_id}")

    assert response.status_code == 404
