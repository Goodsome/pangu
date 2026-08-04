"""基于 httpx 的 d4_leaderboard HTTP 注入适配器。"""

from __future__ import annotations

import logging
from typing import override

import httpx

from d4_injestion.application.ports.leaderboard_entry_client import (
    LeaderboardEntryClient,
)
from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord

logger = logging.getLogger(__name__)


class HttpLeaderboardEntryClient(LeaderboardEntryClient):
    """通过 HTTP POST /entries/ 将榜单记录注入 d4_leaderboard 的适配器。"""

    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """初始化 HTTP 注入客户端。

        Args:
            base_url: d4_leaderboard 服务基址 (如 ``http://localhost:8000``)。
            client: 可选的已配置 AsyncClient (测试注入用), 默认懒创建。
        """
        ...

    @override
    async def create_entry(self, record: LeaderboardRecord) -> None:
        """POST /entries/ 创建一条榜单记录。

        请求体对齐 d4_leaderboard ``CreateEntryRequest``:
        ``player_name / player_class / tier / duration_ms / occurred_at``。
        """
        ...

    @override
    async def aclose(self) -> None:
        """关闭底层 httpx.AsyncClient。"""
        ...
