from code_dom.domain.value_objects.ast_stmt import AstStmtBase
from foundation.common_types.pascal_string import PascalString
from foundation.common_types.snake_string import SnakeString

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


class InfrastructureBlueprintFactory:
    def create_infrastructure_modules(
        self, context: str, aggregate_name: str, is_async: bool = True
    ) -> list[ModuleBlueprint]:
        return [
            self.create_orm_model(context, aggregate_name),
            self.create_orm_mapper(context, aggregate_name),
            self.create_sqlalchemy_repository(
                context, aggregate_name, is_async=is_async
            ),
        ]

    def create_orm_model(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        plural = to_plural(aggregate_name)
        model_name = f"{pascal}Model"

        table_stmt = parse_body(f'__tablename__: str = "{plural}"')[0]
        id_stmt = parse_body("id: Mapped[UUID] = mapped_column(primary_key=True)")[0]

        model_cls = make_class(
            name=model_name,
            bases=[make_generic_base("BaseORM")],
            body=[table_stmt, id_stmt],
        )

        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_orm_model_fqn(context, aggregate_name)
            )
            .with_symbols(["BaseORM", "Mapped", "mapped_column", "UUID"])
            .with_stmt(model_cls)
            .build()
        )

    def create_orm_mapper(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        snake = SnakeString(aggregate_name)
        pascal = PascalString(aggregate_name)
        id_name = f"{pascal}Id"
        model_name = f"{pascal}Model"

        m2e_func_name = f"{snake}_model_to_entity"
        m2e_code = f"return {pascal}(id={id_name}.reconstitute(model.id))"
        m2e_node = make_func(
            name=m2e_func_name,
            params=[("model", model_name)],
            returns=str(pascal),
            body=parse_body(m2e_code),
        )

        e2m_func_name = f"{snake}_entity_to_model"
        e2m_code = f"return {model_name}(id=entity.id.value)"
        e2m_node = make_func(
            name=e2m_func_name,
            params=[("entity", str(pascal))],
            returns=model_name,
            body=parse_body(e2m_code),
        )

        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_orm_mapper_fqn(context, aggregate_name)
            )
            .with_symbols([model_name, str(pascal), id_name])
            .with_stmt(m2e_node)
            .with_stmt(e2m_node)
            .build()
        )

    def create_sqlalchemy_repository(
        self, context: str, aggregate_name: str, is_async: bool = True
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        snake = SnakeString(aggregate_name)
        repo_interface_name = f"{pascal}Repository"
        repo_class_name = f"SqlAlchemy{pascal}Repository"
        id_name = f"{pascal}Id"
        model_name = f"{pascal}Model"

        m2e_func = f"{snake}_model_to_entity"
        e2m_func = f"{snake}_entity_to_model"

        session_type = "AsyncSqlAlchemySession" if is_async else "SqlAlchemySession"
        session_field = parse_body(f"session: {session_type}")[0]

        add_code = f"""
model = {e2m_func}(aggregate)
self.session.add(model)
"""
        add_func = make_func(
            name="_add",
            params=[("self", None), ("aggregate", str(pascal))],
            returns="None",
            decorators=["override"],
            is_async=is_async,
            body=parse_body(add_code),
        )

        add_all_code = f"""
models = [{e2m_func}(a) for a in aggregates]
self.session.add_all(models)
"""
        add_all_func = make_func(
            name="_add_all",
            params=[("self", None), ("aggregates", f"list[{pascal}]")],
            returns="None",
            decorators=["override"],
            is_async=is_async,
            body=parse_body(add_all_code),
        )

        get_call = (
            f"await self.session.get({model_name}, id.value)"
            if is_async
            else f"self.session.get({model_name}, id.value)"
        )
        get_code = f"""
model = {get_call}
if not model:
    raise ValueError(f"{pascal} {{id}} not found")
return {m2e_func}(model)
"""
        get_func = make_func(
            name="_get",
            params=[("self", None), ("id", id_name)],
            returns=str(pascal),
            decorators=["override"],
            is_async=is_async,
            body=parse_body(get_code),
        )

        merge_call = (
            "await self.session.merge(model)"
            if is_async
            else "self.session.merge(model)"
        )
        save_code = f"""
model = {e2m_func}(aggregate)
{merge_call}
"""
        save_func = make_func(
            name="_save",
            params=[("self", None), ("aggregate", str(pascal))],
            returns="None",
            decorators=["override"],
            is_async=is_async,
            body=parse_body(save_code),
        )

        save_all_call = (
            "await self._save(aggregate)" if is_async else "self._save(aggregate)"
        )
        save_all_code = f"""
for aggregate in aggregates:
    {save_all_call}
"""
        save_all_func = make_func(
            name="_save_all",
            params=[("self", None), ("aggregates", f"list[{pascal}]")],
            returns="None",
            decorators=["override"],
            is_async=is_async,
            body=parse_body(save_all_code),
        )

        delete_get_call = (
            f"await self.session.get({model_name}, aggregate.id.value)"
            if is_async
            else f"self.session.get({model_name}, aggregate.id.value)"
        )
        delete_exec_call = (
            "await self.session.delete(model)"
            if is_async
            else "self.session.delete(model)"
        )
        delete_code = f"""
model = {delete_get_call}
if model:
    {delete_exec_call}
"""
        delete_func = make_func(
            name="_delete",
            params=[("self", None), ("aggregate", str(pascal))],
            returns="None",
            decorators=["override"],
            is_async=is_async,
            body=parse_body(delete_code),
        )

        methods: list[AstStmtBase] = [
            session_field,
            add_func,
            add_all_func,
            get_func,
            save_func,
            save_all_func,
            delete_func,
        ]

        repo_cls = make_class(
            name=repo_class_name,
            bases=[make_generic_base(repo_interface_name)],
            decorators=["dataclass"],
            body=methods,
        )

        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_sqlalchemy_repository_fqn(
                    context, aggregate_name
                )
            )
            .with_symbols(
                [
                    "dataclass",
                    "override",
                    session_type,
                    repo_interface_name,
                    model_name,
                    str(pascal),
                    id_name,
                    m2e_func,
                    e2m_func,
                ]
            )
            .with_stmt(repo_cls)
            .build()
        )

    def create_sql_alchemy_unit_of_work(
        self, context: str, aggregate_names: list[str], is_async: bool = True
    ) -> ModuleBlueprint:
        context_name = str(SnakeString(context))
        builder = ModuleBlueprintBuilder(
            path=FqnFactory.create_sql_alchemy_unit_of_work_fqn(context_name)
        )
        mgr_class = "AsyncSessionManager" if is_async else "SessionManager"
        session_type = "AsyncSqlAlchemySession" if is_async else "SqlAlchemySession"

        builder.with_symbols(
            ["dataclass", "override", mgr_class, session_type, "RepoProvider"]
        )

        methods: list[AstStmtBase] = []
        for agg_name in aggregate_names:
            pascal_name = PascalString(agg_name)
            repo_interface = f"{pascal_name}Repository"
            sql_repo_class = f"SqlAlchemy{pascal_name}Repository"
            prop_name = to_plural(agg_name)

            prop_code = f"return {sql_repo_class}(self.session)"
            prop_func = make_func(
                name=prop_name,
                params=[("self", None)],
                returns=repo_interface,
                decorators=["property", "override"],
                body=parse_body(prop_code),
            )
            methods.append(prop_func)
            builder.with_symbol(repo_interface)
            builder.with_symbol(sql_repo_class)

        base_session_mgr = make_generic_base(mgr_class, [session_type])
        base_repo_provider = make_generic_base("RepoProvider")

        uow_cls = make_class(
            name="SqlAlchemyUnitOfWork",
            bases=[base_session_mgr, base_repo_provider],
            decorators=["dataclass"],
            body=methods,
        )

        return builder.with_stmt(uow_cls).build()
