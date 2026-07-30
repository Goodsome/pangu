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
from architecture.application.commands.rename_module import (
    RenameModuleCommand,
    RenameModuleHandler,
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
from architecture.domain.events.file_module_created import FileModuleCreated
from architecture.domain.events.file_module_deleted import FileModuleDeleted
from architecture.domain.events.file_module_moved import FileModuleMoved
from architecture.domain.events.package_module_created import PackageModuleCreated
from architecture.domain.events.package_module_deleted import PackageModuleDeleted
from architecture.domain.events.package_module_moved import PackageModuleMoved
from architecture.infrastructure.gateways.file_system_code_scanner import (
    FileSystemCodeScanner,
)
from architecture.infrastructure.repositories.neo4j_graph_admin import Neo4jGraphAdmin
from architecture.infrastructure.repositories.neo4j_module_query_service import (
    Neo4jModuleQueryService,
)
from architecture.infrastructure.adapters.neo4j_unit_of_work import Neo4jUnitOfWork
from foundation.persistence.sessions.neo4j_session import Neo4jSession


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    redis_client: Dependency[Redis] = Dependency(instance_of=Redis)
    file_system_port: Dependency[FileSystemPort] = Dependency(
        instance_of=FileSystemPort
    )
    db_driver: Dependency[Driver] = Dependency(instance_of=Driver)
    unit_of_work: Factory[Neo4jUnitOfWork] = Factory(
        Neo4jUnitOfWork,
        session_factory=Factory(
            lambda driver: lambda: Neo4jSession(driver=driver), driver=db_driver
        ),
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
    rename_module_handler: Factory[RenameModuleHandler] = Factory(RenameModuleHandler)
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
                RenameModuleCommand: rename_module_handler.provided.execute,
                RemoveModuleCommand: remove_module_handler.provided.execute,
                SyncStagedModulesCommand: sync_staged_modules_handler.provided.execute,
            }
        ),
        event_handlers=Dict(
            {
                FileModuleCreated: List(
                    on_module_created.provided.to_integration_from_file
                ),
                PackageModuleCreated: List(
                    on_module_created.provided.to_integration_from_package
                ),
                FileModuleDeleted: List(
                    on_module_deleted.provided.to_integration_from_file
                ),
                PackageModuleDeleted: List(
                    on_module_deleted.provided.to_integration_from_package
                ),
                FileModuleMoved: List(
                    on_module_moved.provided.update_fqn_prefix_from_file,
                    on_module_moved.provided.to_integration_from_file,
                ),
                PackageModuleMoved: List(
                    on_module_moved.provided.update_fqn_prefix_from_package,
                    on_module_moved.provided.to_integration_from_package,
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
