from __future__ import annotations

import logging
from dataclasses import dataclass
from types import TracebackType
from typing import Any, cast

from redis.asyncio import Redis
from foundation.building_blocks.event import IntegrationEvent

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

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
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
        stream_data: dict[str, str] = {
            "event_type": event_type_name,
            "payload": payload,
            "timestamp": event.timestamp.isoformat(),
        }
        raw_msg_id = await self.client.xadd(
            name=topic,
            fields=cast(Any, stream_data),
            maxlen=self.maxlen,
            approximate=True,
        )
        msg_id = raw_msg_id.decode() if isinstance(raw_msg_id, bytes) else raw_msg_id
        logger.info(
            "📤 [PUBLISH] → stream=%s | type=%s | id=%s | event_id=%s",
            topic,
            event_type_name,
            msg_id,
            event.event_id.hex[:8],
        )
        return msg_id
