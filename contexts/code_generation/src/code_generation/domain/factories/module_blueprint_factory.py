from code_generation.domain.factories.fqn_factory import FqnFactory
from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.module_blueprint_builder import (
    ModuleBlueprintBuilder,
)


class ModuleBlueprintFactory:
    
    def create_aggregate(
        self, context: str, name: str, id_blueprint: ModuleBlueprint,
    ) -> ModuleBlueprint:
        module_path = FqnFactory.create_aggregate_fqn(context, name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_import(
            name="AggregateRoot",
        )
        builder.with_import(
            name=f"{name}Id",
            module_path=id_blueprint.path,
        )
        builder.with_class(
            name=name
        )
        return builder.build()

    def create_identity(
        self, context: str, name: str
    ) -> ModuleBlueprint:
        module_path = FqnFactory.create_identity_fqn(context, name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_import(
            name="UuidIdentifier",
        )
        builder.with_class(
            name=name
        )
        return builder.build()
        