from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dict, Factory, Provider, Resource
from neo4j import Driver

from architecture.application.commands.init_project_graph import InitProjectGraphCommand, InitProjectGraphHandler
from architecture.infrastructure.databases.neo4j_driver import init_neo4j_driver
from architecture.infrastructure.message_bus import MessageBus
from architecture.infrastructure.repositories.memgraph_module_repository import MemgraphModuleRepository
from architecture.infrastructure.unit_of_work import UnitOfWork


class Container(DeclarativeContainer):

    config: Configuration = Configuration()
    
    # project_root: Dependency[Path] = Dependency(instance_of=Path)
    
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

    init_project_graph_handler: Factory[InitProjectGraphHandler] = Factory(
        InitProjectGraphHandler
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