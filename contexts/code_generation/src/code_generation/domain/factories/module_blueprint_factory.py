import ast

from code_dom.domain.value_objects.ast_expr import AstExprBase
from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_expr.ast_subscript import AstSubscript
from code_dom.domain.value_objects.ast_expr.ast_tuple import AstTuple
from code_dom.domain.value_objects.ast_stmt import (
    AstAnnAssign,
    AstAssign,
    AstClassDef,
    AstFunctionDef,
    AstPass,
    AstStmtBase,
)
from code_dom.infrastructure.mappers.ast_to_stmt import AstToStmt
from foundation.common_types.pascal_string import PascalString
from foundation.common_types.snake_string import SnakeString
from foundation.system.context_registry import ContextRegistry

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.fqn_factory import FqnFactory
from code_generation.domain.factories.module_blueprint_builder import (
    ModuleBlueprintBuilder,
)


def _make_generic_base(base_name: str, generic_args: list[str] | None = None) -> AstExprBase:
    if not generic_args:
        return AstName(id=base_name)
    if len(generic_args) == 1:
        slice_expr: AstExprBase = AstName(id=generic_args[0])
    else:
        slice_expr = AstTuple(elts=[AstName(id=arg) for arg in generic_args])
    return AstSubscript(value=AstName(id=base_name), slice=slice_expr)


def _make_class(
    name: str,
    bases: list[AstExprBase] | None = None,
    body: list[AstStmtBase] | None = None,
    decorators: list[str] | None = None,
) -> AstClassDef:
    return AstClassDef(
        name=name,
        bases=bases or [],
        keywords=[],
        body=body or [],
        decorator_list=[AstName(id=d) for d in (decorators or [])],
    )


def _make_func(
    name: str,
    params: list[tuple[str, str | None]] | None = None,
    returns: str | None = None,
    body: list[AstStmtBase] | None = None,
    decorators: list[str] | None = None,
) -> AstFunctionDef:
    arguments: list[AstAssign | AstAnnAssign] = []
    for param_name, annotation in params or []:
        if annotation:
            arguments.append(
                AstAnnAssign(
                    target=AstName(id=param_name),
                    annotation=AstName(id=annotation),
                    value=None,
                )
            )
        else:
            arguments.append(
                AstAssign(
                    targets=[AstName(id=param_name)],
                    value=None,
                )
            )
    return AstFunctionDef(
        lineno=0,
        name=name,
        arguments=arguments,
        decorator_list=[AstName(id=d) for d in (decorators or [])],
        returns=AstName(id=returns) if returns else None,
        body=body or [AstPass()],
    )


def _parse_body(code: str) -> list[AstStmtBase]:
    parsed = ast.parse(code.strip())
    return [AstToStmt.to_stmt(stmt) for stmt in parsed.body]


class ModuleBlueprintFactory:
    def create_aggregate_modules(
        self, context: str, name: str
    ) -> list[ModuleBlueprint]:
        context_name = str(SnakeString(context))
        if not ContextRegistry.check_is_internal(context_name):
            raise ValueError(f"Context {context_name} is not an internal context")

        identity_blueprint = self.create_identity(context_name, name)
        aggregate_blueprint = self.create_aggregate(context_name, name)
        repo_port_blueprint = self.create_repository_port(context_name, name)

        dto_blueprint = self.create_dto(context_name, name)
        dto_to_entity_blueprint = self.create_dto_to_entity_mapper(context_name, name)
        update_entity_from_dto_blueprint = self.create_update_entity_from_dto_mapper(context_name, name)
        entity_to_dto_blueprint = self.create_entity_to_dto_mapper(context_name, name)

        create_cmd_blueprint = self.create_create_command(context_name, name)
        update_cmd_blueprint = self.create_update_command(context_name, name)
        delete_cmd_blueprint = self.create_delete_command(context_name, name)

        return [
            identity_blueprint,
            aggregate_blueprint,
            repo_port_blueprint,
            dto_blueprint,
            dto_to_entity_blueprint,
            update_entity_from_dto_blueprint,
            entity_to_dto_blueprint,
            create_cmd_blueprint,
            update_cmd_blueprint,
            delete_cmd_blueprint,
        ]

    def create_aggregate(
        self,
        context: str,
        aggregate_name: str,
    ) -> ModuleBlueprint:
        pascal_name = PascalString(aggregate_name)
        id_type_name = f"{pascal_name}Id"
        base_expr = _make_generic_base("AggregateRoot", [id_type_name])
        cls_node = _make_class(name=str(pascal_name), bases=[base_expr])
        return (
            ModuleBlueprintBuilder(path=FqnFactory.create_aggregate_fqn(context, aggregate_name))
            .with_symbols(["AggregateRoot", id_type_name])
            .with_stmt(cls_node)
            .build()
        )

    def create_identity(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        pascal_name = PascalString(aggregate_name)
        id_type_name = f"{pascal_name}Id"
        cls_node = _make_class(name=id_type_name, bases=[_make_generic_base("UuidIdentifier")])
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
        repo_base = _make_generic_base("Repository", [str(pascal_name), id_name])
        abc_base = _make_generic_base("ABC")
        cls_node = _make_class(name=repo_name, bases=[repo_base, abc_base])
        return (
            ModuleBlueprintBuilder(path=FqnFactory.create_repository_fqn(context, aggregate_name))
            .with_symbols(["Repository", "ABC", str(pascal_name), id_name])
            .with_stmt(cls_node)
            .build()
        )

    def create_dto(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        pascal_name = PascalString(aggregate_name)
        dto_name = f"{pascal_name}Dto"
        cls_node = _make_class(name=dto_name, bases=[_make_generic_base("BaseModel")])
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
        func_node = _make_func(
            name=func_name,
            params=[("dto", f"{pascal}Dto")],
            returns=str(pascal),
            body=_parse_body(body_code),
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
        func_node = _make_func(
            name=func_name,
            params=[(str(snake), str(pascal)), ("dto", f"{pascal}Dto")],
            returns=str(pascal),
            body=_parse_body(body_code),
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
        func_node = _make_func(
            name=func_name,
            params=[(str(snake), str(pascal))],
            returns=dto_name,
            body=_parse_body(body_code),
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
        plural = self._to_plural(aggregate_name)

        cmd_name = f"Create{pascal}Command"
        handler_name = f"Create{pascal}CommandHandler"
        dto_name = f"{pascal}Dto"
        mapper_func = f"{snake}_dto_to_{snake}"

        cmd_cls = _make_class(
            name=cmd_name,
            bases=[_make_generic_base("Command")],
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
        exec_func = _make_func(
            name="execute",
            params=[("self", None), ("cmd", cmd_name), ("uow", "UnitOfWork")],
            returns="None",
            body=_parse_body(handler_code),
        )
        handler_cls = _make_class(
            name=handler_name,
            decorators=["dataclass"],
            body=[exec_func],
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_create_command_fqn(context, aggregate_name)
            )
            .with_symbols(["Command", "dataclass", "UnitOfWork", dto_name, mapper_func])
            .with_stmt(cmd_cls)
            .with_stmt(handler_cls)
            .build()
        )

    def create_update_command(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        snake = SnakeString(aggregate_name)
        plural = self._to_plural(aggregate_name)

        cmd_name = f"Update{pascal}Command"
        handler_name = f"Update{pascal}CommandHandler"
        id_type_name = f"{pascal}Id"
        dto_name = f"{pascal}Dto"
        update_mapper_func = f"update_{snake}_from_dto"

        cmd_cls = _make_class(
            name=cmd_name,
            bases=[_make_generic_base("Command")],
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
        exec_func = _make_func(
            name="execute",
            params=[("self", None), ("cmd", cmd_name), ("uow", "UnitOfWork")],
            returns="None",
            body=_parse_body(handler_code),
        )
        handler_cls = _make_class(
            name=handler_name,
            decorators=["dataclass"],
            body=[exec_func],
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_update_command_fqn(context, aggregate_name)
            )
            .with_symbols(["Command", "dataclass", "UnitOfWork", id_type_name, dto_name, update_mapper_func])
            .with_stmt(cmd_cls)
            .with_stmt(handler_cls)
            .build()
        )

    def create_delete_command(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        snake = SnakeString(aggregate_name)
        plural = self._to_plural(aggregate_name)

        cmd_name = f"Delete{pascal}Command"
        handler_name = f"Delete{pascal}CommandHandler"
        id_type_name = f"{pascal}Id"

        cmd_cls = _make_class(
            name=cmd_name,
            bases=[_make_generic_base("Command")],
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
        exec_func = _make_func(
            name="execute",
            params=[("self", None), ("cmd", cmd_name), ("uow", "UnitOfWork")],
            returns="None",
            body=_parse_body(handler_code),
        )
        handler_cls = _make_class(
            name=handler_name,
            decorators=["dataclass"],
            body=[exec_func],
        )
        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_delete_command_fqn(context, aggregate_name)
            )
            .with_symbols(["Command", "dataclass", "UnitOfWork", id_type_name])
            .with_stmt(cmd_cls)
            .with_stmt(handler_cls)
            .build()
        )

    def create_unit_of_work(
        self, context: str, aggregate_names: list[str]
    ) -> ModuleBlueprint:
        context_name = str(SnakeString(context))
        if not ContextRegistry.check_is_internal(context_name):
            raise ValueError(f"Context {context_name} is not an internal context")

        builder = ModuleBlueprintBuilder(path=FqnFactory.create_unit_of_work_fqn(context_name))
        builder.with_symbols(["BaseUnitOfWork", "ABC", "abstractmethod"])

        methods: list[AstStmtBase] = []
        for agg_name in aggregate_names:
            repo_name = f"{PascalString(agg_name)}Repository"
            prop_name = self._to_plural(agg_name)
            prop_func = _make_func(
                name=prop_name,
                params=[("self", None)],
                returns=repo_name,
                decorators=["property", "abstractmethod"],
            )
            methods.append(prop_func)
            builder.with_symbol(repo_name)

        uow_cls = _make_class(
            name="UnitOfWork",
            bases=[_make_generic_base("BaseUnitOfWork"), _make_generic_base("ABC")],
            body=methods,
        )
        return builder.with_stmt(uow_cls).build()

    @staticmethod
    def _to_plural(name: str) -> str:
        s = str(SnakeString(name))
        if s.endswith("y") and not s.endswith(("ay", "ey", "iy", "oy", "uy")):
            return s[:-1] + "ies"
        elif s.endswith(("s", "sh", "ch", "x", "z")):
            return s + "es"
        return s + "s"
