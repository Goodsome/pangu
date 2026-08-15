"""基于 httpx 的 helltides.com 抓取适配器。"""

from __future__ import annotations

import logging
from typing import override

import httpx
from pydantic import TypeAdapter

from d4_injestion.application.ports.helltides_client import HelltidesClient
from d4_injestion.domain.value_objects.helltides_row import HelltidesRow
from d4_injestion.domain.value_objects.helltides_run_detail import HelltidesRunDetail

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT_SECONDS = 60.0

_ROWS_ADAPTER: TypeAdapter[list[HelltidesRow]] = TypeAdapter(list[HelltidesRow])


class HttpHelltidesClient(HelltidesClient):
    """通过 httpx 抓取 helltides.com 榜单 API 的适配器。"""

    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """初始化抓取客户端。

        Args:
            base_url: helltides 基址 (如 ``https://helltides.com``)。
            client: 可选的已配置 AsyncClient (测试注入用), 默认懒创建。
        """
        self._base_url: str = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = client

    @override
    async def fetch_leaderboard_rows(self) -> list[HelltidesRow]:
        """GET /api/tower/getAll 抓取榜单列表并解析为强类型行。

        Raises:
            httpx.HTTPStatusError: 服务端返回非 2xx 状态码。
            pydantic.ValidationError: 响应结构与强类型模型不符。
        """
        response = await self._get_client().get(f"{self._base_url}/api/tower/getAll")
        response.raise_for_status()
        payload: object = response.json()
        rows = _ROWS_ADAPTER.validate_python(payload)
        logger.info("helltides 榜单抓取完成: %d 行", len(rows))
        return rows

    @override
    async def fetch_run(self, run_id: str) -> HelltidesRunDetail:
        """GET /api/tower/getRun?id= 抓取单条 run 详情并解析为强类型模型。

        Raises:
            httpx.HTTPStatusError: 服务端返回非 2xx 状态码。
            pydantic.ValidationError: 响应结构与强类型模型不符。
        """
        response = await self._get_client().get(
            f"{self._base_url}/api/tower/getRun",
            params={"id": run_id},
        )
        response.raise_for_status()
        payload: object = response.json()
        return HelltidesRunDetail.model_validate(payload)

    @override
    async def aclose(self) -> None:
        """关闭底层 httpx.AsyncClient。"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """获取或懒创建底层 AsyncClient (getAll 响应约 2.3MB, 超时放宽)。"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS)
        return self._client
