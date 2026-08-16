import contextlib
import typing
from datetime import datetime, timezone
from typing import cast
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest
from dependency_injector.providers import Factory
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from d4_leaderboard.container import Container
from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.application.dtos.affix_distribution_dto import (
    AffixDistributionDto,
    AffixDistributionItem,
)
from d4_leaderboard.application.dtos.skill_build_distribution_dto import (
    SkillBuildDistributionDto,
    SkillBuildItem,
)
from d4_leaderboard.domain.enums.equipment_slot import EquipmentSlot
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
            json={
                "player_name": "Test Player",
                "player_class": "BARBARIAN",
                "tier": 100,
                "duration_ms": 120000,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    assert response.status_code == 201


@pytest.mark.anyio
async def test_get_entry_endpoint_success(
    app: FastAPI, mock_session: AsyncMock
) -> None:
    test_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    mock_model = EntryModel(
        id=test_id,
        player_name="Found Entry",
        player_class=PlayerClass.BARBARIAN,
        tier=100,
        duration_ms=120000,
        occurred_at=now,
    )
    mock_session.get.return_value = mock_model

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/entries/{test_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_id)
    assert data["player_name"] == "Found Entry"
    assert data["player_class"] == "BARBARIAN"
    assert data["tier"] == 100


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
    now_str = datetime.now(timezone.utc).isoformat()
    mock_query_service.find_by_query.return_value = {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "player_name": "Item 1",
                "player_class": "BARBARIAN",
                "tier": 50,
                "duration_ms": 60000,
                "occurred_at": now_str,
            }
        ],
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
async def test_list_entries_endpoint_with_class_filter(
    app: FastAPI, container: Container
) -> None:
    mock_query_service = AsyncMock()
    mock_query_service.find_by_query.return_value = {
        "items": [],
        "total": 0,
        "current": 1,
        "size": 10,
    }
    container.entry_query_service.override(mock_query_service)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/entries/?current=1&size=10&player_class=SORCERER")

    assert response.status_code == 200
    page_query = mock_query_service.find_by_query.await_args.args[0]
    assert page_query.condition.player_class == PlayerClass.SORCERER


@pytest.mark.anyio
async def test_get_affix_distribution_endpoint(
    app: FastAPI, container: Container
) -> None:
    mock_query_service = AsyncMock()
    mock_query_service.get_affix_distribution.return_value = AffixDistributionDto(
        player_class=PlayerClass.BARBARIAN,
        slot=EquipmentSlot.HELM,
        min_tier=100,
        entry_count=2,
        item_count=3,
        masterwork_item_count=2,
        innate=[
            AffixDistributionItem(
                codename="A", stat_type="+A", count=3, percentage=100.0
            )
        ],
        temper=[],
        transfigured=[],
        masterwork_crit=[],
    )
    container.entry_query_service.override(mock_query_service)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/entries/affix-distribution?player_class=BARBARIAN&slot=288&min_tier=100"
        )

    # 200 而非 422, 同时验证了路由未被 /{entry_id} 抢先匹配
    assert response.status_code == 200
    data = response.json()
    assert data["item_count"] == 3
    assert data["innate"][0]["codename"] == "A"

    condition = mock_query_service.get_affix_distribution.await_args.args[0]
    assert condition.player_class == PlayerClass.BARBARIAN
    assert condition.slot == EquipmentSlot.HELM
    assert condition.min_tier == 100


@pytest.mark.anyio
async def test_get_affix_distribution_endpoint_rejects_invalid_min_tier(
    app: FastAPI, container: Container
) -> None:
    mock_query_service = AsyncMock()
    container.entry_query_service.override(mock_query_service)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/entries/affix-distribution?min_tier=0")

    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_affix_distribution_endpoint_with_build_key(
    app: FastAPI, container: Container
) -> None:
    mock_query_service = AsyncMock()
    mock_query_service.get_affix_distribution.return_value = AffixDistributionDto(
        entry_count=0, item_count=0, masterwork_item_count=0
    )
    container.entry_query_service.override(mock_query_service)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/entries/affix-distribution?build_key=warcry%2Bwhirlwind"
        )

    assert response.status_code == 200
    condition = mock_query_service.get_affix_distribution.await_args.args[0]
    assert condition.build_key == "warcry+whirlwind"


@pytest.mark.anyio
async def test_get_skill_builds_endpoint(app: FastAPI, container: Container) -> None:
    mock_query_service = AsyncMock()
    mock_query_service.get_skill_build_distribution.return_value = (
        SkillBuildDistributionDto(
            player_class=PlayerClass.BARBARIAN,
            min_tier=100,
            entry_count=200,
            build_count=1,
            items=[
                SkillBuildItem(
                    build_key="warcry+whirlwind",
                    skills=["warcry", "whirlwind"],
                    count=153,
                    percentage=76.5,
                )
            ],
        )
    )
    container.entry_query_service.override(mock_query_service)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/entries/skill-builds?player_class=BARBARIAN&min_tier=100"
        )

    # 200 而非 422, 同时验证了路由未被 /{entry_id} 抢先匹配
    assert response.status_code == 200
    data = response.json()
    assert data["entry_count"] == 200
    assert data["items"][0]["build_key"] == "warcry+whirlwind"
    assert data["items"][0]["skills"] == ["warcry", "whirlwind"]

    condition = mock_query_service.get_skill_build_distribution.await_args.args[0]
    assert condition.player_class == PlayerClass.BARBARIAN
    assert condition.min_tier == 100


@pytest.mark.anyio
async def test_update_entry_endpoint(app: FastAPI, mock_session: AsyncMock) -> None:
    test_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    mock_model = EntryModel(
        id=test_id,
        player_name="Updated Entry",
        player_class=PlayerClass.BARBARIAN,
        tier=100,
        duration_ms=120000,
        occurred_at=now,
    )
    mock_session.get.return_value = mock_model

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            f"/entries/{test_id}",
            json={"player_name": "Updated Entry"},
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
            json={"player_name": "Nonexistent Entry"},
        )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_entry_endpoint(app: FastAPI, mock_session: AsyncMock) -> None:
    test_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    mock_model = EntryModel(
        id=test_id,
        player_name="To Delete",
        player_class=PlayerClass.BARBARIAN,
        tier=100,
        duration_ms=120000,
        occurred_at=now,
    )
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
