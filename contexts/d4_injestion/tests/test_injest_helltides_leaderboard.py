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
from d4_injestion.domain.serivces.helltides_build_mapper import HelltidesBuildMapper
from d4_injestion.domain.serivces.helltides_row_mapper import HelltidesRowMapper
from d4_injestion.domain.value_objects.helltides_row import HelltidesRow
from d4_injestion.domain.value_objects.helltides_run_detail import HelltidesRunDetail
from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord

from test_helltides_run_detail import make_run_payload


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
    """返回固定榜单行的假抓取客户端, 可指定 run 详情获取失败的 run id。"""

    def __init__(
        self,
        rows: list[HelltidesRow],
        fail_run_ids: set[str] | None = None,
        detail: HelltidesRunDetail | None = None,
    ) -> None:
        self._rows = rows
        self._fail_run_ids = fail_run_ids or set()
        self._detail = detail
        self.closed = False
        self.fetched_run_ids: list[str] = []

    @override
    async def fetch_leaderboard_rows(self) -> list[HelltidesRow]:
        return self._rows

    @override
    async def fetch_run(self, run_id: str) -> HelltidesRunDetail:
        self.fetched_run_ids.append(run_id)
        if run_id in self._fail_run_ids:
            raise RuntimeError("network down")
        if self._detail is not None:
            return self._detail
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


def make_use_case(
    helltides: FakeHelltidesClient,
    entry: FakeEntryClient,
) -> InjestHelltidesLeaderboard:
    """装配被测 Use Case (真实 mapper, 假客户端)。"""
    return InjestHelltidesLeaderboard(
        helltides_client=helltides,
        row_mapper=HelltidesRowMapper(),
        build_mapper=HelltidesBuildMapper(),
        entry_client=entry,
    )


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
    use_case = make_use_case(helltides, entry)

    result = await use_case.execute()

    assert result.total == 2
    assert result.succeeded == 1
    assert result.failed == 1
    assert result.degraded == 0
    assert len(result.errors) == 1
    assert "Liam" in result.errors[0]
    assert [r.player_name for r in entry.created] == ["Resistance"]


@pytest.mark.anyio
async def test_execute_stamps_fetch_time_as_occurred_at() -> None:
    """occurred_at 统一使用抓取时刻。"""
    helltides = FakeHelltidesClient([make_row("Resistance")])
    entry = FakeEntryClient(fail_names=set())
    use_case = make_use_case(helltides, entry)

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
    use_case = make_use_case(helltides, entry)

    await use_case.aclose()

    assert helltides.closed
    assert entry.closed


@pytest.mark.anyio
async def test_execute_enriches_records_with_run_detail() -> None:
    """逐条 fetch_run 回填 build 数据: 注入的 record 携带装备/技能。"""
    detail = HelltidesRunDetail.model_validate(make_run_payload())
    helltides = FakeHelltidesClient(
        [make_row("Resistance", id="run-uuid")], detail=detail
    )
    entry = FakeEntryClient(fail_names=set())
    use_case = make_use_case(helltides, entry)

    result = await use_case.execute()

    assert result.succeeded == 1
    assert result.degraded == 0
    assert helltides.fetched_run_ids == ["run-uuid"]
    record = entry.created[0]
    assert len(record.equipment) == 2
    assert record.equipment[0].codename == "Helm_Unique_Druid_102"
    assert record.skills[0].sno == 548399


@pytest.mark.anyio
async def test_execute_degrades_to_base_record_on_fetch_failure() -> None:
    """fetch_run 失败: 降级为基础记录继续注入, 计入 degraded, 不计入 failed。"""
    helltides = FakeHelltidesClient(
        [
            make_row("Resistance", id="run-ok"),
            make_row("Liam", id="run-bad"),
        ],
        fail_run_ids={"run-bad"},
    )
    entry = FakeEntryClient(fail_names=set())
    use_case = make_use_case(helltides, entry)

    result = await use_case.execute()

    assert result.total == 2
    assert result.succeeded == 2
    assert result.failed == 0
    assert result.degraded == 1
    by_name = {record.player_name: record for record in entry.created}
    # 降级记录不携带 build 数据 (exclude_unset 下 payload 不含 build 字段)
    degraded_payload = by_name["Liam"].model_dump(mode="json", exclude_unset=True)
    assert "equipment" not in degraded_payload
    assert "talismans" not in degraded_payload
    # 正常 enrich 记录携带 build 字段
    assert "equipment" in by_name["Resistance"].model_dump(mode="json")


def test_fake_row_matches_real_class_field() -> None:
    """守护测试夹具: 夹具职业字段可映射到 PlayerClass 枚举。"""
    row = make_row("Resistance")
    assert PlayerClass[row.player_class.upper()] is PlayerClass.DRUID
