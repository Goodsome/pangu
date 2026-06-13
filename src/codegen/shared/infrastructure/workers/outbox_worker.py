import asyncio
from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import not_, select

from codegen.shared.application.integration_events.registry import EventRegistry
from codegen.shared.infrastructure.gateways.redis_stream_publisher import RedisStreamPublisher
from codegen.shared.infrastructure.orm_models.outbox_message_module import OutboxMessageModel

logger = logging.getLogger(__name__)

@dataclass
class OutboxWorker:
    
    session_factory: async_sessionmaker[AsyncSession]
    publisher: RedisStreamPublisher
    event_registry: EventRegistry

    async def run_forever(self, poll_interval: float = 1.0):
        async with self.publisher:
            while True:
                try:
                    processed_count = await self._process_batch()
                    if processed_count == 0:
                        await asyncio.sleep(poll_interval)
                except Exception as e:
                    logger.error(f"Worker Error: {e}")
                    await asyncio.sleep(5)

    async def _process_batch(self, batch_size: int = 100) -> int:
        processed_count = 0
        
        async with self.session_factory() as session:
            stmt = select(OutboxMessageModel).where(
                not_(OutboxMessageModel.processed)
            ).limit(batch_size).with_for_update(skip_locked=True)
            
            result = await session.execute(stmt) 
            messages = result.scalars().all()
            if not messages:
                return 0
            
            for msg in messages:
                event_class = self.event_registry.resolve(msg.event_type)
                if not event_class:
                    logger.error(f"⚠️ 发现未知事件类型 '{msg.event_type}'，跳过处理")
                    msg.processed = True
                    continue
                try:
                    event = event_class.model_validate(msg.payload)
                    await self.publisher.publish(event)
                    msg.processed = True
                    processed_count += 1
                except Exception as e:
                    logger.error(f"❌ 处理消息 {msg.id} 失败: {e}")
                    
            await session.commit()
            
        return processed_count