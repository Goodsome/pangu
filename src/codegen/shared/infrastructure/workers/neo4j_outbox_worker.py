import asyncio
import json
import logging
from dataclasses import dataclass

from neo4j import AsyncDriver
from neo4j.exceptions import ClientError, TransientError

from codegen.shared.application.integration_events.registry import EventRegistry
from codegen.shared.infrastructure.gateways.redis_stream_publisher import RedisStreamPublisher

logger = logging.getLogger(__name__)


@dataclass
class Neo4jOutboxWorker:
    # 使用 neo4j 的 AsyncDriver 替代 async_sessionmaker
    driver: AsyncDriver
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
        
        async with self.driver.session() as session:
            transcaction = await session.begin_transaction()
            async with transcaction as tx:
                # 1. 获取未处理消息并立即标记以获取节点排他锁
                # 使用 elementId 获取现代 Neo4j 的内部唯一标识符
                fetch_query = """
                MATCH (m:OutboxMessage)
                WHERE m.processed = false OR m.processed IS NULL
                WITH m LIMIT $batch_size
                
                // 立即更新状态，阻止其他并行的 Worker 拉取到相同节点
                SET m.processed = true
                
                RETURN id(m) AS id, m.event_type AS event_type, m.payload AS payload
                """
                
                result = await tx.run(fetch_query, batch_size=batch_size)
                records = await result.data()

                if not records:
                    return 0

                failed_ids = []

                # 2. 遍历处理消息并推送到 Redis
                for record in records:
                    msg_id = record["id"]
                    event_type = record["event_type"]
                    
                    # 兼容 payload 的存储形式（字符串或原生字典）
                    raw_payload = record["payload"]
                    payload = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload

                    event_class = self.event_registry.resolve(event_type)
                    if not event_class:
                        logger.error(f"⚠️ 发现未知事件类型 '{event_type}'，跳过处理")
                        # 未知类型保留为 processed = true，避免死循环处理
                        continue

                    try:
                        event = event_class.model_validate(payload)
                        await self.publisher.publish(event)
                        processed_count += 1
                    except Exception as e:
                        logger.error(f"❌ 处理消息 {msg_id} 失败: {e}")
                        failed_ids.append(msg_id)

                # 3. 补偿逻辑：重置发布失败的消息状态
                if failed_ids:
                    rollback_query = """
                    MATCH (m:OutboxMessage)
                    WHERE id(m) IN $failed_ids
                    SET m.processed = false
                    """
                    await tx.run(rollback_query, failed_ids=failed_ids)

                # 4. 提交事务（成功处理的保持 processed=true，失败的回滚为 false）
                await tx.commit()

        return processed_count