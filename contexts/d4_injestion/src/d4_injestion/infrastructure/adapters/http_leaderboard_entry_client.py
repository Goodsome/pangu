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

        请求体为 ``LeaderboardRecord`` 的 JSON 序列化, 字段与 d4_leaderboard
        ``CreateEntryRequest`` 对齐; record 上新增的可选字段 (如 build 数据)
        未设置时不会出现在 payload 中, 由服务端默认值兜底。

        Raises:
            httpx.HTTPStatusError: 服务端返回非 2xx 状态码。
        """
        payload = record.model_dump(mode="json", exclude_unset=True)
        response = await self._get_client().post(
            f"{self._base_url}/entries/",
            json=payload,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            # 记录服务端返回体 (如 FastAPI 422 校验详情), 便于定位字段问题
            logger.warning(
                "注入被服务端拒绝 status=%d body=%s",
                response.status_code,
                response.text[:500],
            )
            raise
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
