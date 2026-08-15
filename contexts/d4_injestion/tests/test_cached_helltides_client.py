"""CachedHelltidesClient 文件缓存装饰器单元测试。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import override

import pytest

from d4_injestion.application.ports.helltides_client import HelltidesClient
from d4_injestion.domain.value_objects.helltides_row import HelltidesRow
from d4_injestion.domain.value_objects.helltides_run_detail import HelltidesRunDetail
from d4_injestion.infrastructure.adapters.cached_helltides_client import (
    CachedHelltidesClient,
)


def make_detail(run_id: str) -> HelltidesRunDetail:
    """构造含 build 数据的最小 run 详情。"""
    return HelltidesRunDetail.model_validate(
        {
            "id": run_id,
            "playerName": "Someone",
            "class": "druid",
            "tier": 150,
            "run_time_ms": 121190,
            "skillsSNO": [{"name": "Lightning Storm", "id": "ls", "sno": 548399}],
        }
    )


class CountingHelltidesClient(HelltidesClient):
    """计数透传的假内层客户端。"""

    def __init__(self) -> None:
        self.fetch_run_calls: list[str] = []
        self.closed = False

    @override
    async def fetch_leaderboard_rows(self) -> list[HelltidesRow]:
        return []

    @override
    async def fetch_run(self, run_id: str) -> HelltidesRunDetail:
        self.fetch_run_calls.append(run_id)
        return make_detail(run_id)

    @override
    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.anyio
async def test_fetch_run_hits_memory_cache(tmp_path: Path) -> None:
    """同实例重复 fetch_run: 只穿透一次, 命中返回等值 VO。"""
    inner = CountingHelltidesClient()
    cached = CachedHelltidesClient(inner, tmp_path / "cache.json")

    first = await cached.fetch_run("run-1")
    second = await cached.fetch_run("run-1")

    assert inner.fetch_run_calls == ["run-1"]
    assert first == second
    assert second.skills_sno[0].sno == 548399


@pytest.mark.anyio
async def test_cache_persists_across_instances(tmp_path: Path) -> None:
    """aclose 写盘后, 新实例同路径直接命中, 不再请求内层。"""
    first_inner = CountingHelltidesClient()
    first = CachedHelltidesClient(first_inner, tmp_path / "cache.json")
    await first.fetch_run("run-1")
    await first.aclose()
    assert first_inner.closed
    assert (tmp_path / "cache.json").exists()

    second_inner = CountingHelltidesClient()
    second = CachedHelltidesClient(second_inner, tmp_path / "cache.json")
    detail = await second.fetch_run("run-1")

    assert second_inner.fetch_run_calls == []
    assert detail.player_name == "Someone"


@pytest.mark.anyio
async def test_corrupt_cache_entry_is_refetched(tmp_path: Path) -> None:
    """缓存条目结构不符 (VO 演进/损坏): 视为 miss 重新抓取。"""
    cache_path = tmp_path / "cache.json"
    cache_path.write_text(
        json.dumps({"run-1": {"unexpected": "shape"}}), encoding="utf-8"
    )
    inner = CountingHelltidesClient()
    cached = CachedHelltidesClient(inner, cache_path)

    detail = await cached.fetch_run("run-1")

    assert inner.fetch_run_calls == ["run-1"]
    assert detail.player_name == "Someone"


@pytest.mark.anyio
async def test_corrupt_cache_file_starts_empty(tmp_path: Path) -> None:
    """缓存文件整体损坏 (非法 JSON): 从空缓存开始, 功能不受影响。"""
    cache_path = tmp_path / "cache.json"
    cache_path.write_text("not a json", encoding="utf-8")
    inner = CountingHelltidesClient()
    cached = CachedHelltidesClient(inner, cache_path)

    await cached.fetch_run("run-1")

    assert inner.fetch_run_calls == ["run-1"]


@pytest.mark.anyio
async def test_fetch_failure_is_not_cached(tmp_path: Path) -> None:
    """内层抓取失败不上抛缓存: 下次仍会重试。"""

    class FailingClient(CountingHelltidesClient):
        fail_ids: set[str] = set()

        @override
        async def fetch_run(self, run_id: str) -> HelltidesRunDetail:
            if run_id in self.fail_ids:
                self.fetch_run_calls.append(run_id)
                raise RuntimeError("boom")
            return await super().fetch_run(run_id)

    inner = FailingClient()
    inner.fail_ids.add("run-bad")
    cached = CachedHelltidesClient(inner, tmp_path / "cache.json")

    with pytest.raises(RuntimeError):
        await cached.fetch_run("run-bad")
    inner.fail_ids.clear()
    detail = await cached.fetch_run("run-bad")

    assert inner.fetch_run_calls == ["run-bad", "run-bad"]
    assert detail.player_name == "Someone"


@pytest.mark.anyio
async def test_fetch_leaderboard_rows_passthrough(tmp_path: Path) -> None:
    """getAll 榜单列表不缓存, 透传内层。"""

    class RowsClient(CountingHelltidesClient):
        @override
        async def fetch_leaderboard_rows(self) -> list[HelltidesRow]:
            return [
                HelltidesRow.model_validate(
                    {
                        "id": "run-1",
                        "rank": 1,
                        "filteredRank": 1,
                        "playerName": "Someone",
                        "class": "druid",
                        "tier": 150,
                        "run_time_ms": 121190,
                    }
                )
            ]

    cached = CachedHelltidesClient(RowsClient(), tmp_path / "cache.json")
    rows = await cached.fetch_leaderboard_rows()

    assert len(rows) == 1
