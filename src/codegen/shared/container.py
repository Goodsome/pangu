from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration
from dependency_injector.providers import Resource
from codegen.shared.infrastructure.database import Database
from codegen.shared.infrastructure.database import init_database


class Container(DeclarativeContainer):
    """Shared kernel DI container for cross-cutting concerns."""

    config: Configuration = Configuration()
    database: Resource[Database] = Resource(
        init_database, connection_string=config.database_url.as_(str)
    )