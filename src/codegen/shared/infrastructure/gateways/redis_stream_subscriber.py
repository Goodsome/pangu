from __future__ import annotations
import asyncio
import logging
import os
import socket
import traceback
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from redis import asyncio as aioredis
from codegen.shared.application.integration_events.registry import EventRegistry
from codegen.shared.infrastructure.message_bus import BaseMessageBus

logger = logging.getLogger(__name__)


@dataclass
class RedisStreamSubscriber:
    """Redis Stream 集成事件订阅器。"""

    client: aioredis.Redis
    message_bus_factory: Callable[[], BaseMessageBus[Any]]
    registry: EventRegistry
    service_name: str = "default-service"
    consumer_name: str = f"{socket.gethostname()}-{os.getpid()}"
    block_ms: int = 2000
    batch_size: int = 10
    subscriptions: list[str] = field(default_factory=list)
    _running: bool = False
    _consume_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """连接 Redis 并启动消费循环。"""
        await self.client.ping()
        for topic in self.subscriptions:
            await self._ensure_consumer_group(topic)
        self._running = True
        self._consume_task = asyncio.create_task(
            self._consume_loop(), name=f"subscriber-{self.service_name}"
        )
        logger.info(
            "🚀 消费循环已启动，订阅 %d 个 topic: %s",
            len(self.subscriptions),
            list(self.subscriptions),
        )

    async def stop(self) -> None:
        """优雅停止消费循环并关闭连接。"""
        logger.info("⏳ 正在停止消费循环...")
        self._running = False
        if self._consume_task is not None:
            try:
                await asyncio.wait_for(self._consume_task, timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("⚠️ 消费循环停止超时，强制取消")
                self._consume_task.cancel()
                try:
                    await self._consume_task
                except asyncio.CancelledError:
                    pass
            self._consume_task = None
        logger.info("✅ Subscriber 已完全停止")

    async def run_forever(self) -> None:
        """阻塞式运行，直到接收到停止信号。"""
        if self._consume_task is None:
            raise RuntimeError("请先调用 start()")
        try:
            await self._consume_task
        except asyncio.CancelledError:
            pass

    async def _ensure_consumer_group(self, topic: str) -> None:
        """确保 Consumer Group 存在。"""
        assert self.client is not None
        try:
            await self.client.xgroup_create(
                name=topic, groupname=self.service_name, id="0", mkstream=True
            )
            logger.info(
                "📂 创建 Consumer Group: stream=%s, group=%s", topic, self.service_name
            )
        except aioredis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.debug(
                    "Consumer Group 已存在: stream=%s, group=%s",
                    topic,
                    self.service_name,
                )
            else:
                raise

    async def _consume_loop(self) -> None:
        """消费主循环 —— 持续从所有订阅的 Stream 中读取消息。"""
        assert self.client is not None
        while self._running:
            streams = {topic: ">" for topic in self.subscriptions}
            if not streams:
                logger.info("📦 没有订阅的 Stream，等待中......")
                await asyncio.sleep(1)
                continue
            try:
                results = await self.client.xreadgroup(
                    groupname=self.service_name,
                    consumername=self.consumer_name,
                    streams=streams,
                    count=self.batch_size,
                    block=self.block_ms,
                )
                if not results:
                    continue
                for stream_name, messages in results:
                    for msg_id, data in messages:
                        asyncio.create_task(
                            self._process_message(stream_name, msg_id, data),
                            name=f"process_msg_{msg_id}",
                        )
            except asyncio.CancelledError:
                logger.info("🛑 消费循环被取消")
                break
            except aioredis.ConnectionError as e:
                logger.error("❌ Redis 连接断开: %s，3 秒后重试...", e)
                await asyncio.sleep(3)
            except Exception:
                logger.error("❌ 消费循环异常:\n%s", traceback.format_exc())
                await asyncio.sleep(1)

    async def _process_message(
        self, stream_name: str, msg_id: str, data: dict[str, str]
    ) -> None:
        """处理单条消息：反序列化 → 分发 → ACK。"""
        event_type_name = data.get("event_type", "")
        payload = data.get("payload", "")
        logger.debug(
            "📨 收到消息: stream=%s, id=%s, event_type=%s",
            stream_name,
            msg_id,
            event_type_name,
        )
        event_class = self.registry.resolve(event_type_name)
        if event_class is None:
            logger.warning(
                "⚠️ 未知事件类型 %r，跳过 (stream=%s, id=%s)",
                event_type_name,
                stream_name,
                msg_id,
            )
            await self.client.xack(stream_name, self.service_name, msg_id)
            return
        try:
            event = event_class.model_validate_json(payload)
        except Exception:
            logger.error(
                "❌ 事件反序列化失败: type=%s, id=%s\n%s",
                event_type_name,
                msg_id,
                traceback.format_exc(),
            )
            await self.client.xack(stream_name, self.service_name, msg_id)
            return
        try:
            bus = self.message_bus_factory()
            bus.handle(event)
        except Exception:
            logger.error(f"❌ 业务处理失败: {msg_id}\n{traceback.format_exc()}")
        await self.client.xack(stream_name, self.service_name, msg_id)
        logger.info(
            "✅ [ACK] stream=%s, id=%s, type=%s", stream_name, msg_id, event_type_name
        )
