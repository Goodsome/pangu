from datetime import datetime, timezone
import contextlib
import typing
import uuid
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.dialects import postgresql

from d4_leaderboard.application.dtos.affix_distribution_filter import (
    AffixDistributionFilter,
)
from d4_leaderboard.application.dtos.entry_filter import EntryFilter
from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.enums.equipment_slot import EquipmentSlot
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
    now = datetime.now(timezone.utc)
    mock_model = EntryModel(
        id=test_uuid,
        player_name="test",
        player_class=PlayerClass.BARBARIAN,
        tier=50,
        duration_ms=60000,
        occurred_at=now,
    )

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
    assert dto.player_name == "test"
    assert dto.player_class == PlayerClass.BARBARIAN
    assert dto.tier == 50
    assert dto.duration_ms == 60000
    assert dto.occurred_at == now
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
    now = datetime.now(timezone.utc)
    mock_model1 = EntryModel(
        id=test_uuid_1,
        player_name="test1",
        player_class=PlayerClass.BARBARIAN,
        tier=50,
        duration_ms=60000,
        occurred_at=now,
    )
    mock_model2 = EntryModel(
        id=test_uuid_2,
        player_name="test2",
        player_class=PlayerClass.BARBARIAN,
        tier=60,
        duration_ms=70000,
        occurred_at=now,
    )

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


@pytest.mark.anyio
async def test_find_by_query_orders_by_leaderboard_semantics() -> None:
    mock_session = AsyncMock(spec=AsyncSession)

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 0
    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value.all.return_value = []

    captured: list[typing.Any] = []

    async def execute_side_effect(stmt: typing.Any) -> MagicMock:
        captured.append(stmt)
        return mock_count_result

    execute_mock = cast(AsyncMock, mock_session.execute)
    execute_mock.side_effect = execute_side_effect

    @contextlib.asynccontextmanager
    async def mock_session_factory():
        yield mock_session

    service = SqlAlchemyEntryQueryService(
        session_factory=cast(typing.Any, mock_session_factory)
    )

    await service.find_by_query(
        PageQuery[EntryFilter](current=1, size=10, condition=EntryFilter())
    )

    # 无过滤条件：count 与 select 均不含 WHERE，select 固定榜单排序
    assert "WHERE" not in str(captured[0])
    assert "WHERE" not in str(captured[1])
    assert "ORDER BY entries.tier DESC, entries.duration_ms ASC" in str(captured[1])


@pytest.mark.anyio
async def test_find_by_query_filters_by_player_class() -> None:
    mock_session = AsyncMock(spec=AsyncSession)

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 0
    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value.all.return_value = []

    captured: list[typing.Any] = []

    async def execute_side_effect(stmt: typing.Any) -> MagicMock:
        captured.append(stmt)
        return mock_count_result

    execute_mock = cast(AsyncMock, mock_session.execute)
    execute_mock.side_effect = execute_side_effect

    @contextlib.asynccontextmanager
    async def mock_session_factory():
        yield mock_session

    service = SqlAlchemyEntryQueryService(
        session_factory=cast(typing.Any, mock_session_factory)
    )

    await service.find_by_query(
        PageQuery[EntryFilter](
            current=1, size=10, condition=EntryFilter(player_class=PlayerClass.SORCERER)
        )
    )

    # 职业过滤同时作用于 count 与 select
    assert "WHERE entries.player_class" in str(captured[0])
    assert "WHERE entries.player_class" in str(captured[1])


def _scalar_result(value: int) -> MagicMock:
    res = MagicMock()
    res.scalar_one.return_value = value
    return res


@pytest.mark.anyio
async def test_get_affix_distribution_groups_and_sorts() -> None:
    mock_session = AsyncMock(spec=AsyncSession)

    rows_result = MagicMock()
    rows_result.all.return_value = [
        SimpleNamespace(
            category="innate",
            codename="A",
            stat_type="+A",
            affix_count=3,
            masterwork_count=1,
        ),
        SimpleNamespace(
            category="temper",
            codename="T",
            stat_type="+T",
            affix_count=2,
            masterwork_count=1,
        ),
        SimpleNamespace(
            category="transfigured",
            codename="X",
            stat_type="+X",
            affix_count=1,
            masterwork_count=0,
        ),
    ]
    execute_mock = cast(AsyncMock, mock_session.execute)
    execute_mock.side_effect = [
        _scalar_result(2),  # entry_count
        _scalar_result(3),  # item_count
        _scalar_result(2),  # masterwork_item_count
        rows_result,
    ]

    @contextlib.asynccontextmanager
    async def mock_session_factory():
        yield mock_session

    service = SqlAlchemyEntryQueryService(
        session_factory=cast(typing.Any, mock_session_factory)
    )

    dto = await service.get_affix_distribution(
        AffixDistributionFilter(
            player_class=PlayerClass.BARBARIAN,
            slot=EquipmentSlot.HELM,
            min_tier=100,
        )
    )

    assert dto.entry_count == 2
    assert dto.item_count == 3
    assert dto.masterwork_item_count == 2

    assert [i.codename for i in dto.innate] == ["A"]
    assert dto.innate[0].count == 3
    assert dto.innate[0].percentage == 100.0

    assert [i.codename for i in dto.temper] == ["T"]
    assert dto.temper[0].percentage == 66.67

    assert [i.codename for i in dto.transfigured] == ["X"]
    assert dto.transfigured[0].percentage == 33.33

    # 精炼分布跨类别汇总, 不含 masterwork_count == 0 的嬗变词缀
    assert {i.codename for i in dto.masterwork_crit} == {"A", "T"}
    assert all(i.percentage == 50.0 for i in dto.masterwork_crit)


@pytest.mark.anyio
async def test_get_affix_distribution_sql_aggregates_in_postgres() -> None:
    mock_session = AsyncMock(spec=AsyncSession)

    empty_rows = MagicMock()
    empty_rows.all.return_value = []
    captured: list[typing.Any] = []

    async def execute_side_effect(stmt: typing.Any) -> MagicMock:
        captured.append(stmt)
        # 前 3 次为 count 查询, 第 4 次为词缀分布查询
        return empty_rows if len(captured) == 4 else _scalar_result(0)

    execute_mock = cast(AsyncMock, mock_session.execute)
    execute_mock.side_effect = execute_side_effect

    @contextlib.asynccontextmanager
    async def mock_session_factory():
        yield mock_session

    service = SqlAlchemyEntryQueryService(
        session_factory=cast(typing.Any, mock_session_factory)
    )

    await service.get_affix_distribution(
        AffixDistributionFilter(
            player_class=PlayerClass.BARBARIAN,
            slot=EquipmentSlot.HELM,
            min_tier=100,
        )
    )

    # 过滤条件同时作用于条目数/装备件数与词缀分布查询
    for stmt in captured:
        sql = str(stmt.compile(dialect=postgresql.dialect()))
        assert "WHERE entries.player_class" in sql
        assert "entries.tier >=" in sql

    dist_compiled = captured[3].compile(dialect=postgresql.dialect())
    dist_sql = str(dist_compiled)
    assert "jsonb_array_elements" in dist_sql
    assert "entry_equipments.slot" in dist_sql
    assert "GROUP BY" in dist_sql
    assert "FILTER (WHERE" in dist_sql
    # JSONB 键名以绑定参数形式出现
    assert "is_masterwork_crit" in dist_compiled.params.values()
    assert "is_transfigured" in dist_compiled.params.values()


@pytest.mark.anyio
async def test_get_affix_distribution_zero_item_count_no_division_error() -> None:
    mock_session = AsyncMock(spec=AsyncSession)
    empty_rows = MagicMock()
    empty_rows.all.return_value = []
    execute_mock = cast(AsyncMock, mock_session.execute)
    execute_mock.side_effect = [
        _scalar_result(0),
        _scalar_result(0),
        _scalar_result(0),
        empty_rows,
    ]

    @contextlib.asynccontextmanager
    async def mock_session_factory():
        yield mock_session

    service = SqlAlchemyEntryQueryService(
        session_factory=cast(typing.Any, mock_session_factory)
    )

    dto = await service.get_affix_distribution(AffixDistributionFilter())
    assert dto.item_count == 0
    assert dto.innate == []
    assert dto.masterwork_crit == []
