import asyncio
from collections.abc import Iterator
from event_hub import EventHub
from event_hub import RedisStreamPublisher
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration
from dependency_injector.providers import Resource
from dependency_injector.providers import Callable
from codegen.shared.infrastructure.database import Database
from codegen.shared.infrastructure.database import init_database
from codegen.shared.infrastructure.adapters.event_hub_adapter import EventHubAdapter


def _init_event_hub() -> Iterator[EventHub]:
    publisher = RedisStreamPublisher()
    hub = EventHub(publisher=publisher)
    asyncio.run(hub.start())
    yield hub
    try:
        asyncio.run(hub.stop())
    except RuntimeError:
        pass


class Container(DeclarativeContainer):
    """Shared kernel DI container for cross-cutting concerns."""

    config: Configuration = Configuration()
    database: Resource[Database] = Resource(
        init_database, connection_string=config.database_url.as_(str)
    )
    event_hub: Resource[EventHub] = Resource(_init_event_hub)
    event_publisher_factory: Callable = Callable(
        EventHubAdapter.build_factory, hub=event_hub
    )
