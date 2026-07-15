from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.fqn_factory import FqnFactory
from code_generation.domain.factories.module_blueprint_builder import (
    ModuleBlueprintBuilder,
)
from code_generation.domain.value_objects.symbol_def import ClassInheritance


class ModuleBlueprintFactory:
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
