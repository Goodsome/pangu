from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import logging

from redis.asyncio import Redis

from codegen.shared.domain.core.event import IntegrationEvent

logger = logging.getLogger(__name__)


@dataclass
class RedisStreamPublisher:
    """Redis Stream 集成事件发布器。"""
    client: Redis
    maxlen: int = 10000

    async def __aenter__(self) -> RedisStreamPublisher:
        await self.client.ping()
        logger.info("✅ Publisher 准备就绪")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        # 如果传入的 client 是共享连接池的，这里只需 close 这个 publisher 即可，
        # 不需要关闭整个连接池
        pass

    async def publish(self, event: IntegrationEvent) -> str:
        """发布集成事件到 Redis Stream。

        Args:
            event: 要发布的集成事件实例。

        Returns:
            Redis Stream 消息 ID。

        Raises:
            RuntimeError: 未连接 Redis 时调用。
        """
        topic = event.topic()
        event_type_name = event.event_type_name
        payload = event.model_dump_json()

        # 构造 Stream 消息
        stream_data: Mapping[str, str] = {
            "event_type": event_type_name,
            "payload": payload,
            "timestamp": event.timestamp.isoformat(),
        }

        # XADD with maxlen trimming
        msg_id: str = await self.client.xadd(
            name=topic,
            fields=stream_data,
            maxlen=self.maxlen,
            approximate=True,
        )

        logger.info(
            "📤 [PUBLISH] → stream=%s | type=%s | id=%s | event_id=%s",
            topic,
            event_type_name,
            msg_id,
            event.event_id.hex[:8],
        )

        return msg_id
