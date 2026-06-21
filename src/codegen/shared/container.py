from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration
from dependency_injector.providers import Singleton
from dependency_injector.providers import Resource
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from codegen.shared.application.integration_events.registry import EventRegistry
from codegen.shared.infrastructure.database import Database
from codegen.shared.infrastructure.database import init_database
from codegen.shared.infrastructure.gateways.redis_stream_publisher import (
    RedisStreamPublisher,
)
from codegen.shared.infrastructure.resources import init_async_db_engine
from codegen.shared.infrastructure.resources import init_async_redis
from codegen.shared.infrastructure.workers.outbox_worker import SqlalchemyOutboxWorker


class Container(DeclarativeContainer):
    """Shared kernel DI container for cross-cutting concerns."""

    config: Configuration = Configuration()
    database: Resource[Database] = Resource(
        init_database, connection_string=config.database_url.as_(str)
    )
    db_engine: Resource[AsyncEngine] = Resource(
        init_async_db_engine, db_url=config.database_url.as_(str)
    )
    redis_client: Resource[Redis] = Resource(
        init_async_redis, redis_url=config.redis_url
    )
    async_session_factory = Singleton(
        async_sessionmaker,
        bind=db_engine,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    redis_publisher: Singleton[RedisStreamPublisher] = Singleton(
        RedisStreamPublisher, client=redis_client
    )
    event_registry: Singleton[EventRegistry] = Singleton(EventRegistry.init)
    outbox_worker: Singleton[SqlalchemyOutboxWorker] = Singleton(
        SqlalchemyOutboxWorker,
        session_factory=async_session_factory,
        publisher=redis_publisher,
        event_registry=event_registry,
    )
