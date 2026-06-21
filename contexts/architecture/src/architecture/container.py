from re import L
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Dict, Factory, List, Provider, Resource, Singleton
from neo4j import Driver
from redis.asyncio import Redis

from architecture.application.commands.init_project_graph import InitProjectGraphCommand, InitProjectGraphHandler
from architecture.application.commands.move_module import MoveModuleCommand, MoveModuleHandler
from architecture.application.commands.remove_module import RemoveModuleCommand, RemoveModuleHandler
from architecture.application.event_handlers.on_module_created import OnModuleCreated
from architecture.application.event_handlers.on_module_deleted import OnModuleDeleted
from architecture.application.event_handlers.on_module_moved import OnModuleMoved
from architecture.domain.events.module_created import ModuleCreated
from architecture.domain.events.module_deleted import ModuleDeleted
from architecture.domain.events.module_moved import ModuleMoved
from architecture.infrastructure.databases.neo4j_driver import init_neo4j_driver
from architecture.infrastructure.gateways.file_system_code_scanner import FileSystemCodeScanner
from architecture.infrastructure.message_bus import MessageBus
from architecture.infrastructure.repositories.neo4j_module_repository import Neo4jModuleRepository
from architecture.infrastructure.repositories.neo4j_graph_admin import Neo4jGraphAdmin
from architecture.infrastructure.repositories.neo4j_module_query_service import Neo4jModuleQueryService
from architecture.infrastructure.unit_of_work import UnitOfWork
from codegen.shared.application.integration_events.module_created import ModuleCreatedIntegrationEvent
from codegen.shared.application.integration_events.module_deleted import ModuleDeletedIntegrationEvent
from codegen.shared.application.integration_events.registry import EventRegistry
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.infrastructure.gateways.redis_stream_subscriber import RedisStreamSubscriber


class Container(DeclarativeContainer):

    config: Configuration = Configuration()
    
    redis_client: Dependency[Redis] = Dependency(instance_of=Redis)
    file_system_port: Dependency[FileSystemPort] = Dependency(
        instance_of=FileSystemPort
    )
    
    module_repository_factory: Provider[Neo4jModuleRepository] = Factory(
        Neo4jModuleRepository
    ).provider
    
    db_driver: Resource[Driver] = Resource(
        init_neo4j_driver,
    )

    unit_of_work: Factory[UnitOfWork] = Factory(
        UnitOfWork,
        driver=db_driver,
        repository_factory=module_repository_factory
    )

    graph_admin: Singleton[Neo4jGraphAdmin] = Singleton(
        Neo4jGraphAdmin,
        driver=db_driver
    )

    module_query_service: Singleton[Neo4jModuleQueryService] = Singleton(
        Neo4jModuleQueryService,
        driver=db_driver
    )

    code_scanner: Singleton[FileSystemCodeScanner] = Singleton(
        FileSystemCodeScanner,
        file_system=file_system_port,
    )

    init_project_graph_handler: Factory[InitProjectGraphHandler] = Factory(
        InitProjectGraphHandler,
        graph_admin=graph_admin,
        code_scanner=code_scanner
    )

    move_module_handler: Factory[MoveModuleHandler] = Factory(
        MoveModuleHandler,
    )

    remove_module_handler: Factory[RemoveModuleHandler] = Factory(
        RemoveModuleHandler,
        query_service=module_query_service
    )

    on_module_created: Singleton[OnModuleCreated] = Singleton(
        OnModuleCreated,
        file_system=file_system_port,
    )

    on_module_deleted: Singleton[OnModuleDeleted] = Singleton(
        OnModuleDeleted,
        file_system=file_system_port,
    )

    on_module_moved: Singleton[OnModuleMoved] = Singleton(
        OnModuleMoved,
    )
    
    message_bus: Factory[MessageBus] = Factory(
        MessageBus,
        uow=unit_of_work,
        command_handlers=Dict(
            {
                InitProjectGraphCommand: init_project_graph_handler.provided.execute,
                MoveModuleCommand: move_module_handler.provided.execute,
                RemoveModuleCommand: remove_module_handler.provided.execute,
            }
        ),
        event_handlers=Dict(
            {
                ModuleCreated: List(
                    on_module_created.provided.to_integration,
                ),
                ModuleCreatedIntegrationEvent: List(
                    on_module_created.provided.create_file
                ),
                ModuleDeleted: List(
                    on_module_deleted.provided.to_integration,
                ),
                ModuleMoved: List(
                    on_module_moved.provided.update_fqn_prefix,
                    on_module_moved.provided.to_integration,
                ),
                ModuleDeletedIntegrationEvent: List(
                    on_module_deleted.provided.clean_filesystem,
                )
            }
        ),
    )
    
    event_registry: Singleton[EventRegistry] = Singleton(EventRegistry.init)
    
    redis_subscriber: Singleton[RedisStreamSubscriber] = Singleton(
        RedisStreamSubscriber,
        client=redis_client,
        message_bus_factory=message_bus.provider,
        registry=event_registry,
        service_name="architecture",
        subscriptions=List("architecture_events"),
    )
