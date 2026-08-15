"""Use Case: 从 helltides.com 抓取榜单并注入 d4_leaderboard。

编排流程::

    rows = await helltides_client.fetch_leaderboard_rows()   # GET /api/tower/getAll
    occurred_at = 抓取时刻 (约定: 榜单行无时间戳, 统一用抓取时间)
    records = row_mapper.to_records(rows, occurred_at)        # 行 -> LeaderboardRecord
    for record in records:
        await entry_client.create_entry(record)               # HTTP POST /entries/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from d4_injestion.application.dtos.injestion_result import InjestionResult
from d4_injestion.application.ports.helltides_client import HelltidesClient
from d4_injestion.application.ports.leaderboard_entry_client import (
    LeaderboardEntryClient,
)
from d4_injestion.domain.serivces.helltides_row_mapper import HelltidesRowMapper

logger = logging.getLogger(__name__)


@dataclass
class InjestHelltidesLeaderboard:
    """helltides 榜单抓取与注入 Use Case。"""

    helltides_client: HelltidesClient
    row_mapper: HelltidesRowMapper
    entry_client: LeaderboardEntryClient

    async def execute(self) -> InjestionResult:
        """执行完整的抓取-映射-注入流程。

        单条记录注入失败只计入失败数, 不中断整体流程。
        """
        rows = await self.helltides_client.fetch_leaderboard_rows()
        records = self.row_mapper.to_records(rows, occurred_at=_utc_now())
        logger.info(
            "helltides 榜单映射完成: 抓取 %d 行, 可注入记录 %d 条",
            len(rows),
            len(records),
        )

        succeeded = 0
        errors: list[str] = []
        for record in records:
            try:
                await self.entry_client.create_entry(record)
                succeeded += 1
            except Exception as e:
                message = f"{record.player_name}({record.player_class.value}): {e}"
                errors.append(message)
                logger.warning("注入失败 %s", message)

        result = InjestionResult(
            total=len(records),
            succeeded=succeeded,
            failed=len(records) - succeeded,
            errors=errors,
        )
        logger.info(
            "helltides 注入完成: total=%d succeeded=%d failed=%d",
            result.total,
            result.succeeded,
            result.failed,
        )
        return result

    async def aclose(self) -> None:
        """释放抓取与注入客户端资源。"""
        await self.helltides_client.aclose()
        await self.entry_client.aclose()


def _utc_now() -> datetime:
    """当前 UTC 时刻 (occurred_at 抓取时间来源)。"""
    return datetime.now(UTC)
