from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    Dependency,
    Dict,
    Factory,
    List,
    Provider,
    Resource,
    Singleton,
)
from foundation.integration_events.registry import EventRegistry
from foundation.message_bus.gateways.redis_stream_subscriber import (
    RedisStreamSubscriber,
)
from foundation.message_bus.message_bus import BaseMessageBus
from foundation.persistence.adapters.memgraph_unit_of_work import MemgraphUnitOfWork
from foundation.system.file_system_port import FileSystemPort
from neo4j import Driver
from redis.asyncio import Redis
from architecture.application.commands.create_package import (
    CreatePackageCommand,
    CreatePackageHandler,
)
from architecture.application.commands.init_project_graph import (
    InitProjectGraphCommand,
    InitProjectGraphHandler,
)
from architecture.application.commands.move_module import (
    MoveModuleCommand,
    MoveModuleHandler,
)
from architecture.application.commands.remove_module import (
    RemoveModuleCommand,
    RemoveModuleHandler,
)
from architecture.application.commands.sync_staged_modules import (
    SyncStagedModulesCommand,
    SyncStagedModulesHandler,
)
from architecture.application.event_handlers.on_module_created import OnModuleCreated
from architecture.application.event_handlers.on_module_deleted import OnModuleDeleted
from architecture.application.event_handlers.on_module_moved import OnModuleMoved
from architecture.domain.events.module_created import ModuleCreated
from architecture.domain.events.module_deleted import ModuleDeleted
from architecture.domain.events.module_moved import ModuleMoved
from foundation.persistence.adapters.neo4j_driver import init_neo4j_driver
from architecture.infrastructure.gateways.file_system_code_scanner import (
    FileSystemCodeScanner,
)
from architecture.infrastructure.repositories.neo4j_graph_admin import Neo4jGraphAdmin
from architecture.infrastructure.repositories.neo4j_module_query_service import (
    Neo4jModuleQueryService,
)
from architecture.infrastructure.repositories.neo4j_module_repository import (
    Neo4jModuleRepository,
)


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    redis_client: Dependency[Redis] = Dependency(instance_of=Redis)
    file_system_port: Dependency[FileSystemPort] = Dependency(
        instance_of=FileSystemPort
    )
    module_repository_factory: Provider[Neo4jModuleRepository] = Factory(
        Neo4jModuleRepository
    ).provider
    db_driver: Resource[Driver] = Resource(init_neo4j_driver)
    unit_of_work: Factory[MemgraphUnitOfWork[Neo4jModuleRepository]] = Factory(
        MemgraphUnitOfWork[Neo4jModuleRepository],
        driver=db_driver,
        repository_factory=module_repository_factory,
    )
    graph_admin: Singleton[Neo4jGraphAdmin] = Singleton(
        Neo4jGraphAdmin, driver=db_driver
    )
    module_query_service: Singleton[Neo4jModuleQueryService] = Singleton(
        Neo4jModuleQueryService, driver=db_driver
    )
    code_scanner: Singleton[FileSystemCodeScanner] = Singleton(
        FileSystemCodeScanner, file_system=file_system_port
    )
    init_project_graph_handler: Factory[InitProjectGraphHandler] = Factory(
        InitProjectGraphHandler, graph_admin=graph_admin, code_scanner=code_scanner
    )
    sync_staged_modules_handler: Factory[SyncStagedModulesHandler] = Factory(
        SyncStagedModulesHandler, code_scanner=code_scanner
    )
    create_package_handler: Factory[CreatePackageHandler] = Factory(
        CreatePackageHandler
    )
    move_module_handler: Factory[MoveModuleHandler] = Factory(MoveModuleHandler)
    remove_module_handler: Factory[RemoveModuleHandler] = Factory(
        RemoveModuleHandler, query_service=module_query_service
    )
    on_module_created: Singleton[OnModuleCreated] = Singleton(OnModuleCreated)
    on_module_deleted: Singleton[OnModuleDeleted] = Singleton(OnModuleDeleted)
    on_module_moved: Singleton[OnModuleMoved] = Singleton(OnModuleMoved)
    message_bus: Factory[BaseMessageBus] = Factory(
        BaseMessageBus,
        uow=unit_of_work,
        command_handlers=Dict(
            {
                CreatePackageCommand: create_package_handler.provided.execute,
                InitProjectGraphCommand: init_project_graph_handler.provided.execute,
                MoveModuleCommand: move_module_handler.provided.execute,
                RemoveModuleCommand: remove_module_handler.provided.execute,
                SyncStagedModulesCommand: sync_staged_modules_handler.provided.execute,
            }
        ),
        event_handlers=Dict(
            {
                ModuleCreated: List(on_module_created.provided.to_integration),
                ModuleDeleted: List(on_module_deleted.provided.to_integration),
                ModuleMoved: List(
                    on_module_moved.provided.update_fqn_prefix,
                    on_module_moved.provided.to_integration,
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
        service_name="architecture",
        subscriptions=List(),
    )
