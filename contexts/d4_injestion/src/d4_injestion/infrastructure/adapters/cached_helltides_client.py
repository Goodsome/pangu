"""带文件持久化缓存的 helltides 抓取客户端装饰器。

getRun 返回的 build 数据不可变, 以 run_id 为键缓存到 JSON 文件, 跨执行
复用: 周期性重跑注入任务时, 榜单中未变化的 run 直接命中本地缓存, 不再
请求 helltides.com。getAll 榜单列表需要最新数据, 不缓存。

缓存文件在首次访问时懒加载, 新条目累积到内存并在 ``aclose`` 时一次性
原子写回 (tmp + rename); 进程中途崩溃会丢失当次新增条目, 下次重新拉取,
不影响正确性。缓存条目因 VO 结构演进无法重新校验时视为 miss 并重新抓取。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import override

from pydantic import TypeAdapter, ValidationError

from d4_injestion.application.ports.helltides_client import HelltidesClient
from d4_injestion.domain.value_objects.helltides_row import HelltidesRow
from d4_injestion.domain.value_objects.helltides_run_detail import HelltidesRunDetail

logger = logging.getLogger(__name__)

_CACHE_ADAPTER: TypeAdapter[dict[str, dict[str, object]]] = TypeAdapter(
    dict[str, dict[str, object]]
)


class CachedHelltidesClient(HelltidesClient):
    """``HelltidesClient`` 装饰器: fetch_run 走本地 JSON 文件缓存。"""

    def __init__(self, delegate: HelltidesClient, cache_path: Path) -> None:
        """初始化缓存装饰器。

        Args:
            delegate: 实际发起 HTTP 请求的被装饰客户端。
            cache_path: 缓存 JSON 文件路径 (run_id -> getRun 响应 payload)。
        """
        self._delegate: HelltidesClient = delegate
        self._cache_path: Path = cache_path
        self._cache: dict[str, dict[str, object]] | None = None

    @override
    async def fetch_leaderboard_rows(self) -> list[HelltidesRow]:
        """榜单列表不缓存, 透传被装饰客户端。"""
        return await self._delegate.fetch_leaderboard_rows()

    @override
    async def fetch_run(self, run_id: str) -> HelltidesRunDetail:
        """优先读本地缓存, miss 时抓取并写回内存缓存。

        Raises:
            Exception: miss 且被装饰客户端抓取失败时原样上抛 (由上层降级)。
        """
        cache = self._ensure_cache_loaded()
        cached = cache.get(run_id)
        if cached is not None:
            try:
                logger.debug("getRun 缓存命中: %s", run_id)
                return HelltidesRunDetail.model_validate(cached)
            except ValidationError:
                logger.warning("缓存条目与当前 VO 结构不符, 重新抓取 run_id=%s", run_id)

        detail = await self._delegate.fetch_run(run_id)
        cache[run_id] = detail.model_dump(mode="json")
        return detail

    @override
    async def aclose(self) -> None:
        """写回缓存并释放被装饰客户端。"""
        try:
            self._flush_cache()
        finally:
            await self._delegate.aclose()

    def _ensure_cache_loaded(self) -> dict[str, dict[str, object]]:
        """懒加载缓存文件; 文件不存在或损坏时从空缓存开始。"""
        if self._cache is None:
            self._cache = {}
            if self._cache_path.exists():
                try:
                    self._cache = _CACHE_ADAPTER.validate_json(
                        self._cache_path.read_text(encoding="utf-8")
                    )
                except (OSError, ValidationError) as e:
                    logger.warning("缓存文件读取失败, 从空缓存开始: %s", e)
        return self._cache

    def _flush_cache(self) -> None:
        """将内存缓存原子写回磁盘 (tmp + rename)。"""
        if self._cache is None:
            return
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._cache_path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(self._cache, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp_path.replace(self._cache_path)
        logger.info(
            "getRun 缓存写回完成: %d 条 -> %s", len(self._cache), self._cache_path
        )
