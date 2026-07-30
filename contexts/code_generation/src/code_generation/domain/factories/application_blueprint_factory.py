from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_stmt import AstAnnAssign, AstStmtBase
from foundation.common_types.pascal_string import PascalString
from foundation.common_types.snake_string import SnakeString
from foundation.system.context_registry import ContextRegistry

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.ast_builder_helpers import (
    make_class,
    make_func,
    make_generic_base,
    parse_body,
    to_plural,
)
from code_generation.domain.factories.fqn_factory import FqnFactory
from code_generation.domain.factories.module_blueprint_builder import (
    ModuleBlueprintBuilder,
)


class ApplicationBlueprintFactory:
    def create_application_modules(
        self, context: str, aggregate_name: str
    ) -> list[ModuleBlueprint]:
        return [
            self.create_dto(context, aggregate_name),
            self.create_dto_to_entity_mapper(context, aggregate_name),
            self.create_update_entity_from_dto_mapper(context, aggregate_name),
            self.create_entity_to_dto_mapper(context, aggregate_name),
            self.create_create_command(context, aggregate_name),
            self.create_update_command(context, aggregate_name),
            self.create_delete_command(context, aggregate_name),
        ]

    def create_dto(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        pascal_name = PascalString(aggregate_name)
        dto_name = f"{pascal_name}Dto"
        cls_node = make_class(name=dto_name, bases=[make_generic_base("BaseModel")])
        return (
            ModuleBlueprintBuilder(path=FqnFactory.create_dto_fqn(context, aggregate_name))
            .with_symbols(["BaseModel"])
            .with_stmt(cls_node)
            .build()
        )

    def create_dto_to_entity_mapper(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        snake = SnakeString(aggregate_name)
        pascal = PascalString(aggregate_name)
        id_name = f"{pascal}Id"
        func_name = f"{snake}_dto_to_{snake}"
        body_code = f"return {pascal}(id={id_name}.create())"
        func_node = make_func(
            name=func_name,
            params=[("dto", f"{pascal}Dto")],
            returns=str(pascal),
            body=parse_body(body_code),
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_dto_to_entity_mapper_fqn(context, aggregate_name)
            )
            .with_symbols([f"{pascal}Dto", str(pascal), id_name])
            .with_stmt(func_node)
            .build()
        )

    def create_update_entity_from_dto_mapper(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        snake = SnakeString(aggregate_name)
        pascal = PascalString(aggregate_name)
        func_name = f"update_{snake}_from_dto"
        body_code = f"return {snake}"
        func_node = make_func(
            name=func_name,
            params=[(str(snake), str(pascal)), ("dto", f"{pascal}Dto")],
            returns=str(pascal),
            body=parse_body(body_code),
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_update_entity_from_dto_mapper_fqn(context, aggregate_name)
            )
            .with_symbols([f"{pascal}Dto", str(pascal)])
            .with_stmt(func_node)
            .build()
        )

    def create_entity_to_dto_mapper(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        snake = SnakeString(aggregate_name)
        pascal = PascalString(aggregate_name)
        dto_name = f"{pascal}Dto"
        func_name = f"{snake}_to_{snake}_dto"
        body_code = f"return {dto_name}()"
        func_node = make_func(
            name=func_name,
            params=[(str(snake), str(pascal))],
            returns=dto_name,
            body=parse_body(body_code),
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_entity_to_dto_mapper_fqn(context, aggregate_name)
            )
            .with_symbols([dto_name, str(pascal)])
            .with_stmt(func_node)
            .build()
        )

    def create_create_command(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        snake = SnakeString(aggregate_name)
        plural = to_plural(aggregate_name)

        cmd_name = f"Create{pascal}Command"
        handler_name = f"Create{pascal}CommandHandler"
        dto_name = f"{pascal}Dto"
        mapper_func = f"{snake}_dto_to_{snake}"

        cmd_cls = make_class(
            name=cmd_name,
            bases=[make_generic_base("Command")],
            body=[
                AstAnnAssign(
                    target=AstName(id="dto"),
                    annotation=AstName(id=dto_name),
                    value=None,
                )
            ],
        )

        handler_code = f"""
{snake} = {mapper_func}(cmd.dto)
uow.{plural}.add({snake})
"""
        exec_func = make_func(
            name="execute",
            params=[("self", None), ("cmd", cmd_name), ("uow", "RepoProvider")],
            returns="None",
            body=parse_body(handler_code),
        )
        handler_cls = make_class(
            name=handler_name,
            decorators=["dataclass"],
            body=[exec_func],
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_create_command_fqn(context, aggregate_name)
            )
            .with_symbols(["Command", "dataclass", "RepoProvider", dto_name, mapper_func])
            .with_stmt(cmd_cls)
            .with_stmt(handler_cls)
            .build()
        )

    def create_update_command(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        snake = SnakeString(aggregate_name)
        plural = to_plural(aggregate_name)

        cmd_name = f"Update{pascal}Command"
        handler_name = f"Update{pascal}CommandHandler"
        id_type_name = f"{pascal}Id"
        dto_name = f"{pascal}Dto"
        update_mapper_func = f"update_{snake}_from_dto"

        cmd_cls = make_class(
            name=cmd_name,
            bases=[make_generic_base("Command")],
            body=[
                AstAnnAssign(
                    target=AstName(id="id"),
                    annotation=AstName(id=id_type_name),
                    value=None,
                ),
                AstAnnAssign(
                    target=AstName(id="dto"),
                    annotation=AstName(id=dto_name),
                    value=None,
                ),
            ],
        )

        handler_code = f"""
{snake} = uow.{plural}.get(cmd.id)
{update_mapper_func}({snake}, cmd.dto)
uow.{plural}.save({snake})
"""
        exec_func = make_func(
            name="execute",
            params=[("self", None), ("cmd", cmd_name), ("uow", "RepoProvider")],
            returns="None",
            body=parse_body(handler_code),
        )
        handler_cls = make_class(
            name=handler_name,
            decorators=["dataclass"],
            body=[exec_func],
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_update_command_fqn(context, aggregate_name)
            )
            .with_symbols(["Command", "dataclass", "RepoProvider", id_type_name, dto_name, update_mapper_func])
            .with_stmt(cmd_cls)
            .with_stmt(handler_cls)
            .build()
        )

    def create_delete_command(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        snake = SnakeString(aggregate_name)
        plural = to_plural(aggregate_name)

        cmd_name = f"Delete{pascal}Command"
        handler_name = f"Delete{pascal}CommandHandler"
        id_type_name = f"{pascal}Id"

        cmd_cls = make_class(
            name=cmd_name,
            bases=[make_generic_base("Command")],
            body=[
                AstAnnAssign(
                    target=AstName(id="id"),
                    annotation=AstName(id=id_type_name),
                    value=None,
                )
            ],
        )

        handler_code = f"""
{snake} = uow.{plural}.get(cmd.id)
uow.{plural}.delete({snake})
"""
        exec_func = make_func(
            name="execute",
            params=[("self", None), ("cmd", cmd_name), ("uow", "RepoProvider")],
            returns="None",
            body=parse_body(handler_code),
        )
        handler_cls = make_class(
            name=handler_name,
            decorators=["dataclass"],
            body=[exec_func],
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_delete_command_fqn(context, aggregate_name)
            )
            .with_symbols(["Command", "dataclass", "RepoProvider", id_type_name])
            .with_stmt(cmd_cls)
            .with_stmt(handler_cls)
            .build()
        )

    def create_repo_provider(
        self, context: str, aggregate_names: list[str]
    ) -> ModuleBlueprint:
        context_name = str(SnakeString(context))
        if not ContextRegistry.check_is_internal(context_name):
            raise ValueError(f"Context {context_name} is not an internal context")

        builder = ModuleBlueprintBuilder(path=FqnFactory.create_repo_provider_fqn(context_name))
        builder.with_symbols(["ABC", "abstractmethod"])

        methods: list[AstStmtBase] = []
        for agg_name in aggregate_names:
            repo_name = f"{PascalString(agg_name)}Repository"
            prop_name = to_plural(agg_name)
            prop_func = make_func(
                name=prop_name,
                params=[("self", None)],
                returns=repo_name,
                decorators=["property", "abstractmethod"],
            )
            methods.append(prop_func)
            builder.with_symbol(repo_name)

        provider_cls = make_class(
            name="RepoProvider",
            bases=[make_generic_base("ABC")],
            body=methods,
        )
        return builder.with_stmt(provider_cls).build()

    def create_unit_of_work(
        self, context: str, aggregate_names: list[str]
    ) -> ModuleBlueprint:
        return self.create_repo_provider(context, aggregate_names)
