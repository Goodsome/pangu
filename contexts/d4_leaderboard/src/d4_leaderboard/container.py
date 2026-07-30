from collections.abc import Callable
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Dependency,
    Dict,
    Factory,
    List,
    Resource,
    Singleton,
)
from foundation.integration_events.registry import EventRegistry
from foundation.message_bus.gateways.redis_stream_subscriber import (
    RedisStreamSubscriber,
)
from foundation.message_bus.message_bus import AsyncBaseMessageBus
from foundation.persistence.adapters.resources import init_async_db_engine
from foundation.persistence.sessions.sqlalchemy_session import AsyncSqlAlchemySession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from d4_leaderboard.application.commands.create_entry import (
    CreateEntryCommand,
    CreateEntryCommandHandler,
)
from d4_leaderboard.application.commands.delete_entry import (
    DeleteEntryCommand,
    DeleteEntryCommandHandler,
)
from d4_leaderboard.application.commands.update_entry import (
    UpdateEntryCommand,
    UpdateEntryCommandHandler,
)
from d4_leaderboard.config import Settings
from d4_leaderboard.infrastructure.persistence.repositories.sql_alchemy_unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from d4_leaderboard.interfaces.api import D4LeaderboardApi


def _create_session_factory(
    maker: async_sessionmaker[AsyncSession],
) -> Callable[[], AsyncSqlAlchemySession]:
    return lambda: AsyncSqlAlchemySession(maker())


class Container(DeclarativeContainer):
    settings: Singleton[Settings] = Singleton(Settings)

    db_engine: Resource[AsyncEngine] = Resource(
        init_async_db_engine,
        db_url=settings.provided.db_url,
    )

    session_maker: Factory[async_sessionmaker[AsyncSession]] = Factory(
        async_sessionmaker,
        bind=db_engine,
        expire_on_commit=False,
        autoflush=False,
    )

    session_factory: Factory[Callable[[], AsyncSqlAlchemySession]] = Factory(
        _create_session_factory,
        maker=session_maker,
    )

    redis_client: Dependency[Redis] = Dependency(instance_of=Redis, default=None)

    unit_of_work: Factory[SqlAlchemyUnitOfWork] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=session_factory,
    )

    create_entry_handler: Factory[CreateEntryCommandHandler] = Factory(
        CreateEntryCommandHandler
    )
    update_entry_handler: Factory[UpdateEntryCommandHandler] = Factory(
        UpdateEntryCommandHandler
    )
    delete_entry_handler: Factory[DeleteEntryCommandHandler] = Factory(
        DeleteEntryCommandHandler
    )

    message_bus: Factory[AsyncBaseMessageBus] = Factory(
        AsyncBaseMessageBus,
        uow=unit_of_work,
        command_handlers=Dict(
            {
                CreateEntryCommand: create_entry_handler.provided.execute,
                UpdateEntryCommand: update_entry_handler.provided.execute,
                DeleteEntryCommand: delete_entry_handler.provided.execute,
            }
        ),
        event_handlers=Dict({}),
    )

    event_registry: Singleton[EventRegistry] = Singleton(EventRegistry.init)
    redis_subscriber: Singleton[RedisStreamSubscriber] = Singleton(
        RedisStreamSubscriber,
        client=redis_client,
        message_bus_factory=message_bus.provider,
        registry=event_registry,
        service_name="d4_leaderboard",
        subscriptions=List(),
    )

    api: Factory[D4LeaderboardApi] = Factory(
        D4LeaderboardApi,
        message_bus=message_bus,
    )
