from foundation.common_types.pascal_string import PascalString
from foundation.common_types.snake_string import SnakeString
from foundation.system.context_registry import ContextRegistry

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.fqn_factory import FqnFactory
from code_generation.domain.factories.module_blueprint_builder import (
    ModuleBlueprintBuilder,
)
from code_generation.domain.value_objects.symbol_def import ClassInheritance


class ModuleBlueprintFactory:
    def create_aggregate_modules(
        self, context: str, name: str
    ) -> list[ModuleBlueprint]:
        aggregate_name = PascalString(name)
        context_name = SnakeString(context)
        if not ContextRegistry.check_is_internal(context_name):
            raise ValueError(f"Context {context_name} is not an internal context")

        id_name = f"{aggregate_name}Id"
        identity_blueprint = self.create_identity(context_name, id_name)
        aggregate_blueprint = self.create_aggregate(
            context_name,
            aggregate_name,
            id_blueprint=identity_blueprint,
        )
        repo_port_blueprint = self.create_repository_port(context_name, aggregate_name)
        return [identity_blueprint, aggregate_blueprint, repo_port_blueprint]

    def create_aggregate(
        self,
        context: str,
        name: str,
        id_blueprint: ModuleBlueprint,
    ) -> ModuleBlueprint:
        module_path = FqnFactory.create_aggregate_fqn(context, name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_import(
            name=f"{name}Id",
            module_path=id_blueprint.path,
        )
        builder.with_class(
            name=name,
            inherits=[ClassInheritance(name="AggregateRoot", args=[f"{name}Id"])],
        )
        return builder.build()

    def create_identity(self, context: str, name: str) -> ModuleBlueprint:
        module_path = FqnFactory.create_identity_fqn(context, name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_class(
            name=name,
            inherits=[ClassInheritance(name="UuidIdentifier")],
        )
        return builder.build()

    def create_repository_port(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        name = f"{aggregate_name}Repository"
        id_name = f"{aggregate_name}Id"
        module_path = FqnFactory.create_repository_fqn(context, name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_class(
            name=name,
            inherits=[
                ClassInheritance(name="Repository", args=[aggregate_name, id_name]),
                ClassInheritance(name="ABC"),
            ],
        )
        return builder.build()

    def create_unit_of_work(
        self, context: str, aggregate_names: list[str]
    ) -> ModuleBlueprint:
        context_name = SnakeString(context)
        if not ContextRegistry.check_is_internal(context_name):
            raise ValueError(f"Context {context_name} is not an internal context")

        module_path = FqnFactory.create_unit_of_work_fqn(context_name)
        builder = ModuleBlueprintBuilder(path=module_path)

        for agg_name in aggregate_names:
            repo_name = f"{PascalString(agg_name)}Repository"
            builder.with_import(name=repo_name)

        builder.with_class(
            name="UnitOfWork",
            inherits=[
                ClassInheritance(name="BaseUnitOfWork"),
                ClassInheritance(name="ABC"),
            ],
        )
        return builder.build()
