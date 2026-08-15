"""InjestHelltidesLeaderboard Use Case 单元测试。"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, override

import pytest
from d4_types.enums.player_class import PlayerClass

from d4_injestion.application.ports.helltides_client import HelltidesClient
from d4_injestion.application.ports.leaderboard_entry_client import (
    LeaderboardEntryClient,
)
from d4_injestion.application.use_cases.injest_helltides_leaderboard import (
    InjestHelltidesLeaderboard,
)
from d4_injestion.domain.serivces.helltides_row_mapper import HelltidesRowMapper
from d4_injestion.domain.value_objects.helltides_row import HelltidesRow
from d4_injestion.domain.value_objects.helltides_run_detail import HelltidesRunDetail
from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord


def make_row(player_name: str, **overrides: Any) -> HelltidesRow:
    """构造一条 helltides 榜单行强类型模型 (可覆盖字段)。"""
    payload: dict[str, Any] = {
        "id": "run-uuid",
        "rank": 1,
        "filteredRank": 1,
        "playerName": player_name,
        "battle_tag": "Battle#1234",
        "class": "druid",
        "tier": 150,
        "run_time_ms": 121190,
    }
    payload.update(overrides)
    return HelltidesRow.model_validate(payload)


def make_run_detail() -> HelltidesRunDetail:
    """构造最小 run 详情。"""
    return HelltidesRunDetail.model_validate(
        {
            "id": "run-uuid",
            "playerName": "Someone",
            "class": "druid",
            "tier": 150,
            "run_time_ms": 121190,
        }
    )


class FakeHelltidesClient(HelltidesClient):
    """返回固定榜单行的假抓取客户端。"""

    def __init__(self, rows: list[HelltidesRow]) -> None:
        self._rows = rows
        self.closed = False

    @override
    async def fetch_leaderboard_rows(self) -> list[HelltidesRow]:
        return self._rows

    @override
    async def fetch_run(self, run_id: str) -> HelltidesRunDetail:
        return make_run_detail()

    @override
    async def aclose(self) -> None:
        self.closed = True


class FakeEntryClient(LeaderboardEntryClient):
    """按玩家名注入失败的假注入客户端。"""

    def __init__(self, fail_names: set[str]) -> None:
        self.fail_names = fail_names
        self.created: list[LeaderboardRecord] = []
        self.closed = False

    @override
    async def create_entry(self, record: LeaderboardRecord) -> None:
        if record.player_name in self.fail_names:
            raise RuntimeError("boom")
        self.created.append(record)

    @override
    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.anyio
async def test_execute_reports_success_and_failure() -> None:
    """2 条有效记录中 1 条注入失败: 单条失败不中断, 结果计数正确。"""
    helltides = FakeHelltidesClient(
        [
            make_row("Resistance"),
            make_row("Liam"),
            make_row("BadRow", tier=0),  # 无效行被 mapper 跳过
        ]
    )
    entry = FakeEntryClient(fail_names={"Liam"})
    use_case = InjestHelltidesLeaderboard(
        helltides_client=helltides,
        row_mapper=HelltidesRowMapper(),
        entry_client=entry,
    )

    result = await use_case.execute()

    assert result.total == 2
    assert result.succeeded == 1
    assert result.failed == 1
    assert len(result.errors) == 1
    assert "Liam" in result.errors[0]
    assert [r.player_name for r in entry.created] == ["Resistance"]


@pytest.mark.anyio
async def test_execute_stamps_fetch_time_as_occurred_at() -> None:
    """occurred_at 统一使用抓取时刻。"""
    helltides = FakeHelltidesClient([make_row("Resistance")])
    entry = FakeEntryClient(fail_names=set())
    use_case = InjestHelltidesLeaderboard(
        helltides_client=helltides,
        row_mapper=HelltidesRowMapper(),
        entry_client=entry,
    )

    before = datetime.now(UTC)
    await use_case.execute()
    after = datetime.now(UTC)

    assert len(entry.created) == 1
    assert before <= entry.created[0].occurred_at <= after


@pytest.mark.anyio
async def test_aclose_closes_both_clients() -> None:
    """aclose 同时释放抓取与注入客户端。"""
    helltides = FakeHelltidesClient([])
    entry = FakeEntryClient(fail_names=set())
    use_case = InjestHelltidesLeaderboard(
        helltides_client=helltides,
        row_mapper=HelltidesRowMapper(),
        entry_client=entry,
    )

    await use_case.aclose()

    assert helltides.closed
    assert entry.closed


def test_fake_row_matches_real_class_field() -> None:
    """守护测试夹具: 夹具职业字段可映射到 PlayerClass 枚举。"""
    row = make_row("Resistance")
    assert PlayerClass[row.player_class.upper()] is PlayerClass.DRUID
