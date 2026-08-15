"""Use Case: 从 helltides.com 抓取榜单并注入 d4_leaderboard。

编排流程::

    rows = await helltides_client.fetch_leaderboard_rows()   # GET /api/tower/getAll
    occurred_at = 抓取时刻 (约定: 榜单行无时间戳, 统一用抓取时间)
    for row in rows:
        record = row_mapper.to_record(row, occurred_at)      # 行 -> 基础 record
        detail = await helltides_client.fetch_run(row.id)    # GET /api/tower/getRun
        record = build_mapper.to_record(record, detail)      # 回填 build 数据
        await entry_client.create_entry(record)              # HTTP POST /entries/

build 数据逐条抓取, 单条 fetch/映射失败降级为基础记录继续注入, 不中断流程。
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
from d4_injestion.domain.serivces.helltides_build_mapper import HelltidesBuildMapper
from d4_injestion.domain.serivces.helltides_row_mapper import HelltidesRowMapper
from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord

logger = logging.getLogger(__name__)


@dataclass
class InjestHelltidesLeaderboard:
    """helltides 榜单抓取与注入 Use Case。"""

    helltides_client: HelltidesClient
    row_mapper: HelltidesRowMapper
    build_mapper: HelltidesBuildMapper
    entry_client: LeaderboardEntryClient

    async def execute(self) -> InjestionResult:
        """执行完整的抓取-映射-enrich-注入流程。

        单条记录注入失败只计入失败数, build 数据获取/映射失败降级为
        基础记录继续注入 (计入降级数), 均不中断整体流程。
        """
        rows = await self.helltides_client.fetch_leaderboard_rows()
        occurred_at = _utc_now()

        records: list[LeaderboardRecord] = []
        degraded = 0
        for index, row in enumerate(rows):
            try:
                base_record = self.row_mapper.to_record(row, occurred_at)
            except (KeyError, ValueError) as e:
                logger.warning(
                    "跳过无法映射的榜单行 index=%d player=%r: %s",
                    index,
                    row.player_name,
                    e,
                )
                continue
            record, is_degraded = await self._enrich_build(base_record, row.id)
            degraded += int(is_degraded)
            records.append(record)

        logger.info(
            "helltides 榜单映射完成: 抓取 %d 行, 可注入记录 %d 条 (build 降级 %d 条)",
            len(rows),
            len(records),
            degraded,
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
            degraded=degraded,
            errors=errors,
        )
        logger.info(
            "helltides 注入完成: total=%d succeeded=%d failed=%d degraded=%d",
            result.total,
            result.succeeded,
            result.failed,
            result.degraded,
        )
        return result

    async def _enrich_build(
        self,
        record: LeaderboardRecord,
        run_id: str,
    ) -> tuple[LeaderboardRecord, bool]:
        """逐条抓取 run 详情并回填 build 数据, 失败降级为基础记录。

        Returns:
            (携带 build 数据的新 record 或原 record, 是否发生了降级)。
        """
        try:
            detail = await self.helltides_client.fetch_run(run_id)
            return self.build_mapper.to_record(record, detail), False
        except Exception as e:
            logger.warning(
                "build 数据获取失败, 降级为基础记录 player=%r run_id=%s: %s",
                record.player_name,
                run_id,
                e,
            )
            return record, True

    async def aclose(self) -> None:
        """释放抓取与注入客户端资源。"""
        await self.helltides_client.aclose()
        await self.entry_client.aclose()


def _utc_now() -> datetime:
    """当前 UTC 时刻 (occurred_at 抓取时间来源)。"""
    return datetime.now(UTC)
