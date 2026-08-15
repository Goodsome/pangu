"""helltides 榜单行 -> LeaderboardRecord 映射领域服务。

注意:
  - helltides 的 ``class`` 为小写 (如 ``druid``), 需映射为 ``PlayerClass`` 枚举;
  - ``getAll`` 行不含通关时间戳, ``occurred_at`` 统一使用抓取时刻;
  - 超出领域约束的行 (如 duration_ms > 600000) 应跳过并记录, 不中断整体流程。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from d4_types.enums.player_class import PlayerClass

from d4_injestion.domain.value_objects.helltides_row import HelltidesRow
from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord

logger = logging.getLogger(__name__)


@dataclass
class HelltidesRowMapper:
    """helltides 强类型榜单行 -> ``LeaderboardRecord`` 列表映射器。"""

    def to_records(
        self,
        rows: list[HelltidesRow],
        occurred_at: datetime,
    ) -> list[LeaderboardRecord]:
        """将榜单行批量映射为待注入记录。

        无法映射的行 (未知职业 / 超出领域校验约束) 跳过并记录
        warning, 不中断整体流程。

        Args:
            rows: ``/api/tower/getAll`` 的强类型行列表。
            occurred_at: 抓取时刻, 统一作为记录的通关时间。
        """
        records: list[LeaderboardRecord] = []
        for index, row in enumerate(rows):
            try:
                records.append(self.to_record(row, occurred_at))
            except (KeyError, ValueError) as e:
                logger.warning(
                    "跳过无法映射的榜单行 index=%d player=%r: %s",
                    index,
                    row.player_name,
                    e,
                )
        return records

    def to_record(self, row: HelltidesRow, occurred_at: datetime) -> LeaderboardRecord:
        """单行映射, 未知职业或校验失败时抛出 KeyError / ValueError。"""
        return LeaderboardRecord(
            player_name=row.player_name,
            player_class=self._map_player_class(row.player_class),
            tier=row.tier,
            duration_ms=row.run_time_ms,
            occurred_at=occurred_at,
        )

    def _map_player_class(self, raw: str) -> PlayerClass:
        """映射职业: ``druid`` -> ``PlayerClass.DRUID``。"""
        return PlayerClass[raw.upper()]
