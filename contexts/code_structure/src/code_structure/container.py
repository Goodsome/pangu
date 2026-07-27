from code_dom.application.queries.get_file_document import GetFileDocumentHandler
from code_structure.application.queries.get_aggregates import GetAggregatesQueryHandler
from code_structure.application.queries.get_symbols import GetSymbolsQueryHandler
from code_structure.infrastructure.queries.neo4j_symbol_query import Neo4jSymbolQuery
from code_structure.interfaces.api import CodeStructureApi
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
from code_structure.application.commands.move_class import (
    MoveClassCommand,
    MoveClassCommandHandler,
)
from code_structure.application.commands.sync_staged_module_symbols import (
    SyncStagedModuleSymbolsCommand,
    SyncStagedModuleSymbolsCommandHandler,
)
from code_structure.domain.events.class_moved import ClassMoved
from code_structure.application.event_handlers.on_class_moved import OnClassMoved
from code_structure.infrastructure.adapters.code_dom_scanner import CodeDomScanner
from code_structure.infrastructure.adapters.neo4j_unit_of_work import Neo4jUnitOfWork
from code_structure.domain.serivces.sync_module_symbols_service import (
    SyncModuleSymbolsService,
)


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    redis_client: Dependency[Redis] = Dependency(instance_of=Redis)
    db_driver: Dependency[Driver] = Dependency(instance_of=Driver)
    get_file_document_handler: Dependency[GetFileDocumentHandler] = Dependency(
        instance_of=GetFileDocumentHandler
    )

    neo4j_symbol_query: Factory[Neo4jSymbolQuery] = Factory(
        Neo4jSymbolQuery, 
        driver=db_driver,
    )
    unit_of_work: Factory[Neo4jUnitOfWork] = Factory(
        Neo4jUnitOfWork,
        driver=db_driver,
    )
    code_dom_scanner: Singleton[CodeDomScanner] = Singleton(
        CodeDomScanner,
        get_file_document_handler=get_file_document_handler,
    )
    init_symbol_graph_handler: Factory[InitSymbolGraphCommandHandler] = Factory(
        InitSymbolGraphCommandHandler,
        symbol_scanner=code_dom_scanner,
    )
    move_class_handler: Factory[MoveClassCommandHandler] = Factory(
        MoveClassCommandHandler
    )
    sync_module_symbols_service: Singleton[SyncModuleSymbolsService] = Singleton(
        SyncModuleSymbolsService
    )
    sync_staged_module_symbols_handler: Factory[
        SyncStagedModuleSymbolsCommandHandler
    ] = Factory(
        SyncStagedModuleSymbolsCommandHandler,
        symbol_scanner=code_dom_scanner,
        sync_service=sync_module_symbols_service,
    )
    get_symbols_query_handler: Factory[GetSymbolsQueryHandler] = Factory(
        GetSymbolsQueryHandler,
        symbol_query=neo4j_symbol_query,
    )
    get_aggregates_query_handler: Factory[GetAggregatesQueryHandler] = Factory(
        GetAggregatesQueryHandler,
        symbol_query=neo4j_symbol_query,
    )
    on_class_moved_handler: Factory[OnClassMoved] = Factory(OnClassMoved)
    message_bus: Factory[BaseMessageBus] = Factory(
        BaseMessageBus,
        uow=unit_of_work,
        command_handlers=Dict(
            {
                InitSymbolGraphCommand: init_symbol_graph_handler.provided.execute,
                MoveClassCommand: move_class_handler.provided.execute,
                SyncStagedModuleSymbolsCommand: sync_staged_module_symbols_handler.provided.execute,
            }
        ),
        event_handlers=Dict(
            {
                ClassMoved: List(
                    on_class_moved_handler.provided.to_integration,
                    on_class_moved_handler.provided.update_module_imports,
                ),
            }
        ),
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

    api: Factory[CodeStructureApi] = Factory(
        CodeStructureApi,
        get_symbols_query_handler=get_symbols_query_handler,
        get_aggregates_query_handler=get_aggregates_query_handler,
    )
