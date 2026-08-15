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

_REQUEST_TIMEOUT_SECONDS = 30.0


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
        self._base_url: str = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = client

    @override
    async def create_entry(self, record: LeaderboardRecord) -> None:
        """POST /entries/ 创建一条榜单记录。

        请求体对齐 d4_leaderboard ``CreateEntryRequest``:
        ``player_name / player_class / tier / duration_ms / occurred_at``。

        Raises:
            httpx.HTTPStatusError: 服务端返回非 2xx 状态码。
        """
        payload = {
            "player_name": record.player_name,
            "player_class": record.player_class.value,
            "tier": record.tier,
            "duration_ms": record.duration_ms,
            "occurred_at": record.occurred_at.isoformat(),
        }
        response = await self._get_client().post(
            f"{self._base_url}/entries/",
            json=payload,
        )
        response.raise_for_status()
        logger.debug(
            "注入成功: %s (%s) tier=%d duration_ms=%d",
            record.player_name,
            record.player_class.value,
            record.tier,
            record.duration_ms,
        )

    @override
    async def aclose(self) -> None:
        """关闭底层 httpx.AsyncClient。"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """获取或懒创建底层 AsyncClient。"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS)
        return self._client
