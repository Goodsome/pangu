from foundation.common_types.pascal_string import PascalString

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.ast_builder_helpers import (
    make_class,
    make_generic_base,
)
from code_generation.domain.factories.fqn_factory import FqnFactory
from code_generation.domain.factories.module_blueprint_builder import (
    ModuleBlueprintBuilder,
)


class DomainBlueprintFactory:
    def create_domain_modules(
        self, context: str, aggregate_name: str
    ) -> list[ModuleBlueprint]:
        return [
            self.create_identity(context, aggregate_name),
            self.create_aggregate(context, aggregate_name),
            self.create_repository_port(context, aggregate_name),
        ]

    def create_aggregate(
        self,
        context: str,
        aggregate_name: str,
    ) -> ModuleBlueprint:
        pascal_name = PascalString(aggregate_name)
        id_type_name = f"{pascal_name}Id"
        base_expr = make_generic_base("AggregateRoot", [id_type_name])
        cls_node = make_class(name=str(pascal_name), bases=[base_expr])
        return (
            ModuleBlueprintBuilder(path=FqnFactory.create_aggregate_fqn(context, aggregate_name))
            .with_symbols(["AggregateRoot", id_type_name])
            .with_stmt(cls_node)
            .build()
        )

    def create_identity(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        pascal_name = PascalString(aggregate_name)
        id_type_name = f"{pascal_name}Id"
        cls_node = make_class(name=id_type_name, bases=[make_generic_base("UuidIdentifier")])
        return (
            ModuleBlueprintBuilder(path=FqnFactory.create_identity_fqn(context, aggregate_name))
            .with_symbols(["UuidIdentifier"])
            .with_stmt(cls_node)
            .build()
        )

    def create_repository_port(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal_name = PascalString(aggregate_name)
        repo_name = f"{pascal_name}Repository"
        id_name = f"{pascal_name}Id"
        repo_base = make_generic_base("Repository", [str(pascal_name), id_name])
        abc_base = make_generic_base("ABC")
        cls_node = make_class(name=repo_name, bases=[repo_base, abc_base])
        return (
            ModuleBlueprintBuilder(path=FqnFactory.create_repository_fqn(context, aggregate_name))
            .with_symbols(["Repository", "ABC", str(pascal_name), id_name])
            .with_stmt(cls_node)
            .build()
        )
