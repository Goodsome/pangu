from code_dom.interfaces.api import CodeDomApi
from code_structure.interfaces.api import CodeStructureApi
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory

from code_generation.application.commands.delete_aggregate import (
    DeleteAggregateCommandHandler,
)
from code_generation.application.commands.generate_aggregate import (
    GenerateAggregateCommandHandler,
)
from code_generation.domain.factories.module_blueprint_factory import (
    ModuleBlueprintFactory,
)
from code_generation.interfaces.api import CodeGenerationApi


class Container(DeclarativeContainer):
    code_dom_api: Dependency[CodeDomApi] = Dependency(instance_of=CodeDomApi)
    code_structure_api: Dependency[CodeStructureApi] = Dependency(
        instance_of=CodeStructureApi
    )

    module_blueprint_factory: Factory[ModuleBlueprintFactory] = Factory(
        ModuleBlueprintFactory
    )

    generate_aggregate_handler: Factory[GenerateAggregateCommandHandler] = Factory(
        GenerateAggregateCommandHandler,
        factory=module_blueprint_factory,
        code_dom_api=code_dom_api,
        code_structure_api=code_structure_api,
    )

    delete_aggregate_handler: Factory[DeleteAggregateCommandHandler] = Factory(
        DeleteAggregateCommandHandler,
        factory=module_blueprint_factory,
        code_dom_api=code_dom_api,
        code_structure_api=code_structure_api,
    )

    api: Factory[CodeGenerationApi] = Factory(
        CodeGenerationApi,
        generate_aggregate_handler=generate_aggregate_handler,
        delete_aggregate_handler=delete_aggregate_handler,
    )
