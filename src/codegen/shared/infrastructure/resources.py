from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

async def init_async_db_engine(db_url: str) -> AsyncIterator[AsyncEngine]:
    """初始化并管理异步数据库引擎的生命周期"""
    engine = create_async_engine(db_url, echo=False, pool_size=20, max_overflow=10)
    
    yield engine  # 将 engine 提供给 DI 容器
    
    await engine.dispose()

async def init_async_redis(redis_url: str) -> AsyncIterator[Redis]:
    """初始化并管理 Redis 连接池的生命周期"""
    client = Redis.from_url(redis_url, decode_responses=True)
    
    await client.ping()
    
    yield client
    
    await client.aclose()

