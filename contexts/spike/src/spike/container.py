
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Singleton
from spike.application.commands.create_dependency_scaffold import CreateDependencyScaffoldCommandHandler
from spike.infrastructure.adapters.agent_engine_scaffold_builder import AgentEngineScaffoldBuilder

class Container(DeclarativeContainer):
    config: Configuration = Configuration()

    agent_engine_scaffold_builder: Singleton[AgentEngineScaffoldBuilder] = Singleton(
        AgentEngineScaffoldBuilder,
    )
    
    create_dependency_scaffold_handler: Factory[CreateDependencyScaffoldCommandHandler] = Factory(
        CreateDependencyScaffoldCommandHandler,
        scaffold_builder=agent_engine_scaffold_builder,
    )