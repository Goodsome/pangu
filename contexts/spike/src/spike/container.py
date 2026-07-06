
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory
from spike.application.commands.create_dependency_scaffold import CreateDependencyScaffoldCommandHandler

class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    
    create_dependency_scaffold_handler: Factory[CreateDependencyScaffoldCommandHandler] = Factory(
        CreateDependencyScaffoldCommandHandler,
    )