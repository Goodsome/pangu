from dataclasses import dataclass, field

from foundation.common_types.snake_string import SnakeString
from foundation.system.context_registry import ContextRegistry

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.application_blueprint_factory import (
    ApplicationBlueprintFactory,
)
from code_generation.domain.factories.domain_blueprint_factory import (
    DomainBlueprintFactory,
)
from code_generation.domain.factories.infrastructure_blueprint_factory import (
    InfrastructureBlueprintFactory,
)


@dataclass
class ModuleBlueprintFactory:
    domain_factory: DomainBlueprintFactory = field(
        default_factory=DomainBlueprintFactory
    )
    app_factory: ApplicationBlueprintFactory = field(
        default_factory=ApplicationBlueprintFactory
    )
    infra_factory: InfrastructureBlueprintFactory = field(
        default_factory=InfrastructureBlueprintFactory
    )

    def create_aggregate_modules(
        self, context: str, name: str
    ) -> list[ModuleBlueprint]:
        context_name = str(SnakeString(context))
        if not ContextRegistry.check_is_internal(context_name):
            raise ValueError(f"Context {context_name} is not an internal context")

        return (
            self.domain_factory.create_domain_modules(context_name, name)
            + self.app_factory.create_application_modules(context_name, name)
            + self.infra_factory.create_infrastructure_modules(context_name, name)
        )

    def create_unit_of_work(
        self, context: str, aggregate_names: list[str]
    ) -> list[ModuleBlueprint]:
        repo_provider_bp = self.app_factory.create_repo_provider(context, aggregate_names)
        sql_uow_bp = self.infra_factory.create_sql_alchemy_unit_of_work(context, aggregate_names)
        return [repo_provider_bp, sql_uow_bp]
