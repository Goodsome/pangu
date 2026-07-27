from foundation.common_types.pascal_string import PascalString
from foundation.common_types.snake_string import SnakeString
from foundation.system.context_registry import ContextRegistry

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.fqn_factory import FqnFactory
from code_generation.domain.factories.module_blueprint_builder import (
    ModuleBlueprintBuilder,
)
from code_generation.domain.value_objects.symbol_def import (
    ClassInheritance,
    FunctionDef,
    MethodDef,
    ParamDef,
)


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

        dto_blueprint = self.create_dto(context_name, aggregate_name)
        dto_to_entity_blueprint = self.create_dto_to_entity_mapper(context_name, aggregate_name)
        entity_to_dto_blueprint = self.create_entity_to_dto_mapper(context_name, aggregate_name)

        create_cmd_blueprint = self.create_create_command(context_name, aggregate_name)
        update_cmd_blueprint = self.create_update_command(context_name, aggregate_name)
        delete_cmd_blueprint = self.create_delete_command(context_name, aggregate_name)

        return [
            identity_blueprint,
            aggregate_blueprint,
            repo_port_blueprint,
            dto_blueprint,
            dto_to_entity_blueprint,
            entity_to_dto_blueprint,
            create_cmd_blueprint,
            update_cmd_blueprint,
            delete_cmd_blueprint,
        ]

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

    def create_dto(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        dto_name = f"{PascalString(aggregate_name)}Dto"
        module_path = FqnFactory.create_dto_fqn(context, aggregate_name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_class(
            name=dto_name,
            inherits=[ClassInheritance(name="BaseModel")],
        )
        return builder.build()

    def create_dto_to_entity_mapper(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        snake = SnakeString(aggregate_name)
        pascal = PascalString(aggregate_name)
        func_name = f"{snake}_dto_to_{snake}"
        module_path = FqnFactory.create_dto_to_entity_mapper_fqn(context, aggregate_name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_symbol(
            FunctionDef(
                name=func_name,
                params=[ParamDef(name="dto", type_annotation=f"{pascal}Dto")],
                return_type=pascal,
            )
        )
        return builder.build()

    def create_entity_to_dto_mapper(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        snake = SnakeString(aggregate_name)
        pascal = PascalString(aggregate_name)
        func_name = f"{snake}_to_{snake}_dto"
        module_path = FqnFactory.create_entity_to_dto_mapper_fqn(context, aggregate_name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_symbol(
            FunctionDef(
                name=func_name,
                params=[ParamDef(name=str(snake), type_annotation=pascal)],
                return_type=f"{pascal}Dto",
            )
        )
        return builder.build()

    def create_create_command(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        cmd_name = f"Create{pascal}Command"
        handler_name = f"Create{pascal}CommandHandler"
        module_path = FqnFactory.create_create_command_fqn(context, aggregate_name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_class(
            name=cmd_name,
            inherits=[ClassInheritance(name="Command")],
        )
        builder.with_class(
            name=handler_name,
            decorators=["dataclass"],
            methods=[
                MethodDef(
                    name="execute",
                    params=[
                        ParamDef(name="self"),
                        ParamDef(name="cmd", type_annotation=cmd_name),
                        ParamDef(name="uow", type_annotation="UnitOfWork"),
                    ],
                )
            ],
        )
        return builder.build()

    def create_update_command(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        cmd_name = f"Update{pascal}Command"
        handler_name = f"Update{pascal}CommandHandler"
        module_path = FqnFactory.create_update_command_fqn(context, aggregate_name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_class(
            name=cmd_name,
            inherits=[ClassInheritance(name="Command")],
        )
        builder.with_class(
            name=handler_name,
            decorators=["dataclass"],
            methods=[
                MethodDef(
                    name="execute",
                    params=[
                        ParamDef(name="self"),
                        ParamDef(name="cmd", type_annotation=cmd_name),
                        ParamDef(name="uow", type_annotation="UnitOfWork"),
                    ],
                )
            ],
        )
        return builder.build()

    def create_delete_command(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        cmd_name = f"Delete{pascal}Command"
        handler_name = f"Delete{pascal}CommandHandler"
        module_path = FqnFactory.create_delete_command_fqn(context, aggregate_name)
        builder = ModuleBlueprintBuilder(path=module_path)
        builder.with_class(
            name=cmd_name,
            inherits=[ClassInheritance(name="Command")],
        )
        builder.with_class(
            name=handler_name,
            decorators=["dataclass"],
            methods=[
                MethodDef(
                    name="execute",
                    params=[
                        ParamDef(name="self"),
                        ParamDef(name="cmd", type_annotation=cmd_name),
                        ParamDef(name="uow", type_annotation="UnitOfWork"),
                    ],
                )
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

        methods: list[MethodDef] = []
        for agg_name in aggregate_names:
            repo_name = f"{PascalString(agg_name)}Repository"
            prop_name = self._to_plural(agg_name)
            methods.append(
                MethodDef(
                    name=prop_name,
                    decorators=["property", "abstractmethod"],
                    return_type=repo_name,
                    params=[ParamDef(name="self")],
                )
            )

        builder.with_class(
            name="UnitOfWork",
            inherits=[
                ClassInheritance(name="BaseUnitOfWork"),
                ClassInheritance(name="ABC"),
            ],
            methods=methods,
        )
        return builder.build()

    @staticmethod
    def _to_plural(name: str) -> str:
        s = str(SnakeString(name))
        if s.endswith("y") and not s.endswith(("ay", "ey", "iy", "oy", "uy")):
            return s[:-1] + "ies"
        elif s.endswith(("s", "sh", "ch", "x", "z")):
            return s + "es"
        return s + "s"
