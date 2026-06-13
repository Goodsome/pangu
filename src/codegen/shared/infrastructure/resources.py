from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

async def init_async_db_engine(db_url: str) -> AsyncIterator[AsyncEngine]:
    """初始化并管理异步数据库引擎的生命周期"""
    engine = create_async_engine(db_url, echo=False, pool_size=20, max_overflow=10)
    logger.info("✅ Async DB Engine initialized.")
    
    yield engine  # 将 engine 提供给 DI 容器
    
    # 当应用关闭，DI 容器销毁时，执行优雅释放
    await engine.dispose()
    logger.info("🔌 Async DB Engine disposed.")

async def init_async_redis(redis_url: str) -> AsyncIterator[Redis]:
    """初始化并管理 Redis 连接池的生命周期"""
    client = Redis.from_url(redis_url, decode_responses=True)
    
    # 验证连接
    await client.ping()
    logger.info("✅ Async Redis Client connected.")
    
    yield client
    
    await client.aclose()
    logger.info("🔌 Async Redis Client disconnected.")

