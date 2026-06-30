from code_dom.application.queries.get_file_document import GetFileDocumentHandler
from code_structure.infrastructure.adapters.code_dom_scanner import CodeDomScanner
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    Dependency,
    Dict,
    Factory,
    List,
    Singleton,
)
from foundation.integration_events.registry import EventRegistry
from foundation.message_bus.gateways.redis_stream_subscriber import (
    RedisStreamSubscriber,
)
from foundation.message_bus.message_bus import BaseMessageBus
from neo4j import Driver
from redis.asyncio import Redis
from code_structure.application.commands.init_symbol_graph import (
    InitSymbolGraphCommand,
    InitSymbolGraphCommandHandler,
)
from code_structure.application.ports.symbol_graph_admin import SymbolGraphAdmin
from code_structure.infrastructure.adapters.neo4j_unit_of_work import Neo4jUnitOfWork
from code_structure.infrastructure.repositories.neo4j_symbol_graph_admin import (
    Neo4jSymbolGraphAdmin,
)


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    redis_client: Dependency[Redis] = Dependency(instance_of=Redis)
    db_driver: Dependency[Driver] = Dependency(instance_of=Driver)
    get_file_document_handler: Dependency[GetFileDocumentHandler] = Dependency(instance_of=GetFileDocumentHandler)

    unit_of_work: Factory[Neo4jUnitOfWork] = Factory(
        Neo4jUnitOfWork,
        driver=db_driver,
    )
    symbol_graph_admin: Singleton[SymbolGraphAdmin] = Singleton(
        Neo4jSymbolGraphAdmin,
        driver=db_driver,
    )
    code_dom_scanner: Singleton[CodeDomScanner] = Singleton(
        CodeDomScanner,
        get_file_document_handler=get_file_document_handler,
    )
    init_symbol_graph_handler: Factory[InitSymbolGraphCommandHandler] = Factory(
        InitSymbolGraphCommandHandler,
        symbol_graph_admin=symbol_graph_admin,
        symbol_scanner=code_dom_scanner,
    )
    message_bus: Factory[BaseMessageBus] = Factory(
        BaseMessageBus,
        uow=unit_of_work,
        command_handlers=Dict(
            {
                InitSymbolGraphCommand: init_symbol_graph_handler.provided.execute,
            }
        ),
        event_handlers=Dict(),
    )
    event_registry: Singleton[EventRegistry] = Singleton(EventRegistry.init)
    redis_subscriber: Singleton[RedisStreamSubscriber] = Singleton(
        RedisStreamSubscriber,
        client=redis_client,
        message_bus_factory=message_bus.provider,
        registry=event_registry,
        service_name="code_structure",
        subscriptions=List(),
    )
