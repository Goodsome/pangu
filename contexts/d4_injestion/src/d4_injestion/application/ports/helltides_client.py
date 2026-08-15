"""helltides.com 抓取客户端端口。

用于从第三方网站 helltides.com 抓取 D4 Tower 榜单数据:

  - ``GET /api/tower/getAll``         -> 榜单列表 (JSON 数组, ~1400 行)
  - ``GET /api/tower/getRun?id=<uuid>`` -> 单条完整 build (装备/技能/巅峰/护身符)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from d4_injestion.domain.value_objects.helltides_row import HelltidesRow
from d4_injestion.domain.value_objects.helltides_run_detail import HelltidesRunDetail


class HelltidesClient(ABC):
    """helltides.com 榜单抓取客户端端口。"""

    @abstractmethod
    async def fetch_leaderboard_rows(self) -> list[HelltidesRow]:
        """抓取榜单列表 (GET /api/tower/getAll)。

        Returns:
            强类型榜单行列表 (含 id/rank/playerName/class/tier/run_time_ms 等)。
        """
        ...

    @abstractmethod
    async def fetch_run(self, run_id: str) -> HelltidesRunDetail:
        """抓取单条 run 完整详情 (GET /api/tower/getRun?id=)。

        Args:
            run_id: run 的 uuid (榜单行 ``id`` 字段)。

        Returns:
            含装备/技能/巅峰/护身符的完整 build 强类型详情。
        """
        ...

    @abstractmethod
    async def aclose(self) -> None:
        """释放底层 HTTP 连接资源。"""
        ...
