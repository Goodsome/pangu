from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Dict, Factory, Provider, Resource, Singleton
from neo4j import Driver

from architecture.application.commands.init_project_graph import InitProjectGraphCommand, InitProjectGraphHandler
from architecture.infrastructure.databases.neo4j_driver import init_neo4j_driver
from architecture.infrastructure.gateways.file_system_code_scanner import FileSystemCodeScanner
from architecture.infrastructure.message_bus import MessageBus
from architecture.infrastructure.repositories.memgraph_module_repository import MemgraphModuleRepository
from architecture.infrastructure.repositories.neo4j_graph_admin import Neo4jGraphAdmin
from architecture.infrastructure.unit_of_work import UnitOfWork
from codegen.shared.domain.ports.file_system_port import FileSystemPort


class Container(DeclarativeContainer):

    config: Configuration = Configuration()
    
    # project_root: Dependency[Path] = Dependency(instance_of=Path)
    file_system_port: Dependency[FileSystemPort] = Dependency(
        instance_of=FileSystemPort
    )
    
    module_repository_factory: Provider[MemgraphModuleRepository] = Factory(
        MemgraphModuleRepository
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

    code_scanner: Singleton[FileSystemCodeScanner] = Singleton(
        FileSystemCodeScanner,
        file_system=file_system_port,
    )

    init_project_graph_handler: Factory[InitProjectGraphHandler] = Factory(
        InitProjectGraphHandler,
        graph_admin=graph_admin,
        code_scanner=code_scanner
    )
    
    message_bus: Factory[MessageBus] = Factory(
        MessageBus,
        uow=unit_of_work,
        command_handlers=Dict(
            {
                InitProjectGraphCommand: init_project_graph_handler.provided.execute
            }
        ),
        event_handlers=Dict(),
    )